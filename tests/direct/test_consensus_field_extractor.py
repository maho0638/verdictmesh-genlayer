import json

A="https://a.example/e"; B="https://b.example/e"; C="https://c.example/e"

def val(vm,url,value,confidence=90):
    domain=url.split("://",1)[1].split("/",1)[0].replace(".",r"\.")
    vm.mock_web(rf".*{domain}.*",{"status":200,"body":"Controlled field evidence."})
    vm.mock_llm(rf"(?s).*SOURCE URL:.*{domain}.*",json.dumps({"value":value,"confidence":confidence}))

def setup(vm,a,b,c,conf=90):
    vm.clear_mocks(); val(vm,A,a,conf); val(vm,B,b,conf); val(vm,C,c,conf)

def test_three_way_agreement(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/consensus_field_extractor.py"); direct_vm.sender=direct_alice
    setup(direct_vm,"v2.1","V2.1"," v2.1 "); c.extract("f1","release version",A,B,C)
    r=c.get_result("f1"); assert r.verdict=="AGREED"; assert r.consensus_value=="v2.1"; assert int(r.agreement_count)==3

def test_two_agree_one_missing(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/consensus_field_extractor.py"); direct_vm.sender=direct_alice
    setup(direct_vm,"42","42",""); c.extract("f2","value",A,B,C)
    r=c.get_result("f2"); assert r.verdict=="AGREED"; assert int(r.agreement_count)==2

def test_competing_values_force_conflict(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/consensus_field_extractor.py"); direct_vm.sender=direct_alice
    setup(direct_vm,"42","42","43"); c.extract("f3","value",A,B,C)
    assert c.get_result("f3").verdict=="CONFLICTED"

def test_low_confidence_value_does_not_count(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/consensus_field_extractor.py"); direct_vm.sender=direct_alice
    direct_vm.clear_mocks(); val(direct_vm,A,"42",40); val(direct_vm,B,"42",90); val(direct_vm,C,"",90)
    c.extract("f4","value",A,B,C); assert c.get_result("f4").verdict=="INSUFFICIENT"

def test_requires_independent_domains(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/consensus_field_extractor.py"); direct_vm.sender=direct_alice
    with direct_vm.expect_revert("three independent HTTPS domains"):
        c.extract("f5","value","https://example.com/a","https://www.example.com/b",C)

def test_validator_rejects_changed_value(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/consensus_field_extractor.py"); direct_vm.sender=direct_alice
    setup(direct_vm,"42","42","42"); c.extract("f6","value",A,B,C)
    setup(direct_vm,"99","99","99"); assert direct_vm.run_validator() is False
