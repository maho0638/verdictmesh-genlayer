import json

A="https://a.example/e"; B="https://b.example/e"; C="https://c.example/e"

def vote(vm,url,verdict,confidence=90):
    domain=url.split("://",1)[1].split("/",1)[0].replace(".",r"\.")
    vm.mock_web(rf".*{domain}.*",{"status":200,"body":"Controlled corroboration evidence."})
    vm.mock_llm(rf"(?s).*SOURCE URL:.*{domain}.*",json.dumps({"verdict":verdict,"confidence":confidence}))

def setup(vm,p="SUPPORT",a="SUPPORT",b="SUPPORT"):
    vm.clear_mocks(); vote(vm,A,p); vote(vm,B,a); vote(vm,C,b)

def test_primary_plus_corroborator_verifies(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/primary_corroboration_gate.py"); direct_vm.sender=direct_alice
    setup(direct_vm,"SUPPORT","SUPPORT","INSUFFICIENT")
    c.verify("pcg1","Claim.",A,B,C); assert c.get_result("pcg1").verdict=="VERIFIED"

def test_any_contradiction_forces_conflict(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/primary_corroboration_gate.py"); direct_vm.sender=direct_alice
    setup(direct_vm,"SUPPORT","SUPPORT","CONTRADICT")
    c.verify("pcg2","Claim.",A,B,C); assert c.get_result("pcg2").verdict=="CONFLICTED"

def test_primary_must_support(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/primary_corroboration_gate.py"); direct_vm.sender=direct_alice
    setup(direct_vm,"INSUFFICIENT","SUPPORT","SUPPORT")
    c.verify("pcg3","Claim.",A,B,C); assert c.get_result("pcg3").verdict=="INSUFFICIENT"

def test_requires_three_independent_domains(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/primary_corroboration_gate.py"); direct_vm.sender=direct_alice
    with direct_vm.expect_revert("three independent HTTPS domains"):
        c.verify("pcg4","Claim.","https://example.com/a","https://www.example.com/b",C)

def test_validator_rejects_primary_flip(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/primary_corroboration_gate.py"); direct_vm.sender=direct_alice
    setup(direct_vm); c.verify("pcg5","Claim.",A,B,C)
    setup(direct_vm,"CONTRADICT","SUPPORT","SUPPORT"); assert direct_vm.run_validator() is False
