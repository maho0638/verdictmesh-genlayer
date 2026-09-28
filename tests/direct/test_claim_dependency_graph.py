import json

A="https://a.example/e"; B="https://b.example/e"; C="https://c.example/e"; D="https://d.example/e"

def vote(vm,url,verdict,confidence=90):
    domain=url.split("://",1)[1].split("/",1)[0].replace(".",r"\.")
    vm.mock_web(rf".*{domain}.*",{"status":200,"body":"Controlled graph evidence."})
    vm.mock_llm(rf"(?s).*SOURCE URL:.*{domain}.*",json.dumps({"verdict":verdict,"confidence":confidence}))

def pair(vm,a="SUPPORT",b="SUPPORT",urls=(A,B)):
    vm.clear_mocks(); vote(vm,urls[0],a); vote(vm,urls[1],b)

def test_root_supported(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/claim_dependency_graph.py"); direct_vm.sender=direct_alice
    c.create_claim("root","","Root claim.",A,B); pair(direct_vm); c.resolve("root")
    assert c.get_claim("root").verdict=="SUPPORTED"

def test_child_locked_until_prerequisite_supported(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/claim_dependency_graph.py"); direct_vm.sender=direct_alice
    c.create_claim("root","","Root.",A,B); c.create_claim("child","root","Child.",C,D)
    assert c.is_unlocked("child") is False
    with direct_vm.expect_revert("Prerequisite must be resolved and supported"): c.resolve("child")

def test_child_unlocks_after_supported_root(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/claim_dependency_graph.py"); direct_vm.sender=direct_alice
    c.create_claim("root","","Root.",A,B); c.create_claim("child","root","Child.",C,D)
    pair(direct_vm); c.resolve("root"); assert c.is_unlocked("child") is True
    pair(direct_vm,urls=(C,D)); c.resolve("child"); assert c.get_claim("child").verdict=="SUPPORTED"

def test_contradicted_root_keeps_child_locked(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/claim_dependency_graph.py"); direct_vm.sender=direct_alice
    c.create_claim("root","","Root.",A,B); c.create_claim("child","root","Child.",C,D)
    pair(direct_vm,"CONTRADICT","CONTRADICT"); c.resolve("root"); assert c.is_unlocked("child") is False

def test_mixed_sources_create_conflict(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/claim_dependency_graph.py"); direct_vm.sender=direct_alice
    c.create_claim("root","","Root.",A,B); pair(direct_vm,"SUPPORT","CONTRADICT"); c.resolve("root")
    assert c.get_claim("root").verdict=="CONFLICTED"

def test_missing_prerequisite_rejected(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/claim_dependency_graph.py"); direct_vm.sender=direct_alice
    with direct_vm.expect_revert("Prerequisite claim not found"): c.create_claim("child","missing","Child.",C,D)

def test_validator_rejects_flip(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/claim_dependency_graph.py"); direct_vm.sender=direct_alice
    c.create_claim("root","","Root.",A,B); pair(direct_vm); c.resolve("root")
    pair(direct_vm,"CONTRADICT","CONTRADICT"); assert direct_vm.run_validator() is False
