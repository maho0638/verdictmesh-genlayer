import json

A="https://a.example/e"; B="https://b.example/e"; C="https://c.example/e"

def num(vm,url,value,found=True,confidence=90):
    domain=url.split("://",1)[1].split("/",1)[0].replace(".",r"\.")
    vm.mock_web(rf".*{domain}.*",{"status":200,"body":"Controlled numeric evidence."})
    vm.mock_llm(rf"(?s).*SOURCE URL:.*{domain}.*",json.dumps({"found":found,"value":value,"confidence":confidence}))

def setup(vm,values,confidence=90):
    vm.clear_mocks()
    for url,value in zip((A,B,C),values): num(vm,url,value,True,confidence)

def test_values_inside_tolerance_reach_consensus(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/numeric_consensus_oracle.py"); direct_vm.sender=direct_alice
    setup(direct_vm,(100,101,99)); c.evaluate("n1","active users","users",2,A,B,C)
    r=c.get_result("n1"); assert r.verdict=="CONSENSUS"; assert int(r.spread)==2; assert int(r.consensus_value)==100

def test_large_spread_is_divergent(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/numeric_consensus_oracle.py"); direct_vm.sender=direct_alice
    setup(direct_vm,(100,150,101)); c.evaluate("n2","active users","users",5,A,B,C)
    assert c.get_result("n2").verdict=="DIVERGENT"

def test_missing_source_is_insufficient(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/numeric_consensus_oracle.py"); direct_vm.sender=direct_alice
    direct_vm.clear_mocks(); num(direct_vm,A,100); num(direct_vm,B,101); num(direct_vm,C,0,False,90)
    c.evaluate("n3","active users","users",5,A,B,C); assert c.get_result("n3").verdict=="INSUFFICIENT"

def test_low_confidence_source_is_insufficient(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/numeric_consensus_oracle.py"); direct_vm.sender=direct_alice
    direct_vm.clear_mocks(); num(direct_vm,A,100); num(direct_vm,B,101); num(direct_vm,C,100,True,40)
    c.evaluate("n4","active users","users",5,A,B,C); assert c.get_result("n4").verdict=="INSUFFICIENT"

def test_requires_independent_domains(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/numeric_consensus_oracle.py"); direct_vm.sender=direct_alice
    with direct_vm.expect_revert("three independent HTTPS domains"):
        c.evaluate("n5","m","u",5,"https://example.com/a","https://www.example.com/b",C)

def test_validator_rejects_changed_number(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/numeric_consensus_oracle.py"); direct_vm.sender=direct_alice
    setup(direct_vm,(100,100,100)); c.evaluate("n6","m","u",0,A,B,C)
    setup(direct_vm,(200,200,200)); assert direct_vm.run_validator() is False
