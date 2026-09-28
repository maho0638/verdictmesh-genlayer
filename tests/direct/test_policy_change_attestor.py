import hashlib, json

URL="https://policy.example/current"

def result(vm,verdict,confidence=90,excerpt="Current policy text."):
    vm.clear_mocks()
    vm.mock_web(r".*policy\.example.*",{"status":200,"body":"Current public policy."})
    vm.mock_llm(r"(?s).*Compare a frozen baseline statement.*",json.dumps({"verdict":verdict,"confidence":confidence,"current_excerpt":excerpt}))

def test_unchanged(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/policy_change_attestor.py"); direct_vm.sender=direct_alice
    result(direct_vm,"UNCHANGED"); c.attest("pc1","The policy allows X.",URL)
    assert c.get_result("pc1").verdict=="UNCHANGED"

def test_changed(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/policy_change_attestor.py"); direct_vm.sender=direct_alice
    result(direct_vm,"CHANGED"); c.attest("pc2","The policy allows X.",URL)
    assert c.get_result("pc2").verdict=="CHANGED"

def test_low_confidence_fails_closed(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/policy_change_attestor.py"); direct_vm.sender=direct_alice
    result(direct_vm,"CHANGED",40); c.attest("pc3","The policy allows X.",URL)
    assert c.get_result("pc3").verdict=="UNDETERMINED"

def test_baseline_sha256_is_bound(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/policy_change_attestor.py"); direct_vm.sender=direct_alice
    baseline="The policy allows X."; result(direct_vm,"UNCHANGED"); c.attest("pc4",baseline,URL)
    assert c.get_result("pc4").baseline_hash==hashlib.sha256(baseline.encode()).hexdigest()

def test_invalid_url_rejected(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/policy_change_attestor.py"); direct_vm.sender=direct_alice
    with direct_vm.expect_revert("valid HTTPS"): c.attest("pc5","baseline","http://policy.example")

def test_validator_rejects_semantic_flip(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/policy_change_attestor.py"); direct_vm.sender=direct_alice
    result(direct_vm,"UNCHANGED"); c.attest("pc6","The policy allows X.",URL)
    result(direct_vm,"CHANGED"); assert direct_vm.run_validator() is False


def test_validator_allows_nondecisive_excerpt_paraphrase(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/policy_change_attestor.py"); direct_vm.sender=direct_alice
    result(direct_vm,"UNCHANGED",90,"Version A wording."); c.attest("pc7","The policy allows X.",URL)
    result(direct_vm,"UNCHANGED",90,"Equivalent version B wording.")
    assert direct_vm.run_validator() is True
