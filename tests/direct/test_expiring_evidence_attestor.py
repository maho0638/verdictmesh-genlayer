import json
from datetime import datetime,timedelta,timezone

A="https://a.example/e"; B="https://b.example/e"; C="https://c.example/e"; D="https://d.example/e"

def vote(vm,url,verdict,confidence=90):
    domain=url.split("://",1)[1].split("/",1)[0].replace(".",r"\.")
    vm.mock_web(rf".*{domain}.*",{"status":200,"body":"Controlled expiring evidence."})
    vm.mock_llm(rf"(?s).*SOURCE URL:.*{domain}.*",json.dumps({"verdict":verdict,"confidence":confidence}))

def pair(vm,a="SUPPORT",b="SUPPORT",urls=(A,B),confidence=90):
    vm.clear_mocks(); vote(vm,urls[0],a,confidence); vote(vm,urls[1],b,confidence)

def test_supported_attestation_is_active(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/expiring_evidence_attestor.py"); direct_vm.sender=direct_alice
    pair(direct_vm); c.attest("ex1","Claim.",3600,A,B)
    r=c.get_result("ex1"); assert r.verdict=="SUPPORTED"; assert int(r.round)==1; assert c.is_active("ex1") is True

def test_mixed_sources_are_conflicted(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/expiring_evidence_attestor.py"); direct_vm.sender=direct_alice
    pair(direct_vm,"SUPPORT","CONTRADICT"); c.attest("ex2","Claim.",3600,A,B)
    assert c.get_result("ex2").verdict=="CONFLICTED"

def test_low_confidence_fails_closed(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/expiring_evidence_attestor.py"); direct_vm.sender=direct_alice
    pair(direct_vm,"SUPPORT","SUPPORT",confidence=40); c.attest("ex3","Claim.",3600,A,B)
    assert c.get_result("ex3").verdict=="INSUFFICIENT"

def test_invalid_ttl_rejected(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/expiring_evidence_attestor.py"); direct_vm.sender=direct_alice
    with direct_vm.expect_revert("TTL must be between"): c.attest("ex4","Claim.",0,A,B)

def test_refresh_blocked_while_active(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/expiring_evidence_attestor.py"); direct_vm.sender=direct_alice
    pair(direct_vm); c.attest("ex5","Claim.",3600,A,B)
    with direct_vm.expect_revert("still active"): c.refresh("ex5",3600,C,D)

def test_refresh_after_expiry_increments_round(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/expiring_evidence_attestor.py"); direct_vm.sender=direct_alice
    pair(direct_vm); c.attest("ex6","Claim.",60,A,B)
    direct_vm.warp((datetime.now(timezone.utc)+timedelta(minutes=2)).isoformat())
    assert c.is_active("ex6") is False
    pair(direct_vm,urls=(C,D)); c.refresh("ex6",3600,C,D)
    r=c.get_result("ex6"); assert int(r.round)==2; assert r.verdict=="SUPPORTED"; assert c.is_active("ex6") is True

def test_validator_rejects_vote_flip(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/expiring_evidence_attestor.py"); direct_vm.sender=direct_alice
    pair(direct_vm); c.attest("ex7","Claim.",3600,A,B)
    pair(direct_vm,"CONTRADICT","CONTRADICT"); assert direct_vm.run_validator() is False
