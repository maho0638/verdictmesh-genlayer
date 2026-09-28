import json

A="https://a.example/e"
B="https://b.example/e"
C="https://c.example/e"

def vote(vm,url,verdict,confidence=90):
    domain=url.split("://",1)[1].split("/",1)[0].replace(".",r"\.")
    vm.mock_web(rf".*{domain}.*",{"status":200,"body":"Controlled panel evidence."})
    vm.mock_llm(rf"(?s).*SOURCE URL:.*{domain}.*",json.dumps({"verdict":verdict,"confidence":confidence}))

def panel(vm,a="SUPPORT",b="SUPPORT",c="SUPPORT",conf=90):
    vm.clear_mocks()
    vote(vm,A,a,conf); vote(vm,B,b,conf); vote(vm,C,c,conf)

def test_all_support(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/evidence_panel.py"); direct_vm.sender=direct_alice
    panel(direct_vm); c.evaluate("p1","Claim.",A,B,C)
    r=c.get_result("p1"); assert r.verdict=="SUPPORTED"; assert int(r.support_count)==3

def test_material_counterevidence_forces_conflict(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/evidence_panel.py"); direct_vm.sender=direct_alice
    panel(direct_vm,"SUPPORT","SUPPORT","CONTRADICT"); c.evaluate("p2","Claim.",A,B,C)
    r=c.get_result("p2"); assert r.verdict=="CONFLICTED"; assert int(r.contradict_count)==1

def test_low_confidence_fails_closed(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/evidence_panel.py"); direct_vm.sender=direct_alice
    panel(direct_vm,"SUPPORT","SUPPORT","SUPPORT",40); c.evaluate("p3","Claim.",A,B,C)
    r=c.get_result("p3"); assert r.verdict=="INSUFFICIENT"; assert int(r.insufficient_count)==3

def test_duplicate_domains_rejected(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/evidence_panel.py"); direct_vm.sender=direct_alice
    with direct_vm.expect_revert("three independent domains"):
        c.evaluate("p4","Claim.","https://example.com/a","https://www.example.com/b",C)

def test_non_https_rejected(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/evidence_panel.py"); direct_vm.sender=direct_alice
    with direct_vm.expect_revert("valid HTTPS URLs"):
        c.evaluate("p5","Claim.","http://a.example",B,C)

def test_validator_rejects_vote_flip(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/evidence_panel.py"); direct_vm.sender=direct_alice
    panel(direct_vm); c.evaluate("p6","Claim.",A,B,C)
    panel(direct_vm,"CONTRADICT","CONTRADICT","CONTRADICT")
    assert direct_vm.run_validator() is False
