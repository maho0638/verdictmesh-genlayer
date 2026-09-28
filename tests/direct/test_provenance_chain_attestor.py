import json

PRIMARY="https://primary.example/e"; ORIGIN="https://origin.example/e"

def setup(vm,attributes=True,origin_vote="SUPPORT",pconf=90,oconf=90,label="Origin Record"):
    vm.clear_mocks()
    vm.mock_web(r".*primary\.example.*",{"status":200,"body":"Primary attribution."})
    vm.mock_web(r".*origin\.example.*",{"status":200,"body":"Origin evidence."})
    vm.mock_llm(r"(?s).*Check whether this PRIMARY source.*",json.dumps({"attributes_origin":attributes,"origin_label":label,"confidence":pconf}))
    vm.mock_llm(r"(?s).*Judge whether this ORIGIN source.*",json.dumps({"verdict":origin_vote,"confidence":oconf}))

def test_confirmed_provenance(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/provenance_chain_attestor.py"); direct_vm.sender=direct_alice
    setup(direct_vm); c.attest("pr1","Claim.",PRIMARY,ORIGIN)
    r=c.get_result("pr1"); assert r.verdict=="PROVENANCE_CONFIRMED"; assert r.primary_attributes_origin is True

def test_missing_attribution_is_insufficient(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/provenance_chain_attestor.py"); direct_vm.sender=direct_alice
    setup(direct_vm,False,"SUPPORT"); c.attest("pr2","Claim.",PRIMARY,ORIGIN)
    assert c.get_result("pr2").verdict=="INSUFFICIENT"

def test_origin_contradiction_is_conflict(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/provenance_chain_attestor.py"); direct_vm.sender=direct_alice
    setup(direct_vm,True,"CONTRADICT"); c.attest("pr3","Claim.",PRIMARY,ORIGIN)
    assert c.get_result("pr3").verdict=="CONFLICTED"

def test_requires_independent_domains(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/provenance_chain_attestor.py"); direct_vm.sender=direct_alice
    with direct_vm.expect_revert("two independent HTTPS domains"):
        c.attest("pr4","Claim.","https://example.com/a","https://www.example.com/b")

def test_validator_rejects_origin_flip(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/provenance_chain_attestor.py"); direct_vm.sender=direct_alice
    setup(direct_vm); c.attest("pr5","Claim.",PRIMARY,ORIGIN)
    setup(direct_vm,True,"CONTRADICT"); assert direct_vm.run_validator() is False


def test_validator_allows_origin_label_paraphrase(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/provenance_chain_attestor.py"); direct_vm.sender=direct_alice
    setup(direct_vm,True,"SUPPORT",90,90,"Origin Record"); c.attest("pr6","Claim.",PRIMARY,ORIGIN)
    setup(direct_vm,True,"SUPPORT",90,90,"The Origin Record")
    assert direct_vm.run_validator() is True
