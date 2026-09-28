import json

A="https://a.example/e"; B="https://b.example/e"

def result(vm,verdict,confidence=90,fact_a="A says X.",fact_b="B says X."):
    vm.clear_mocks()
    vm.mock_web(r".*a\.example.*",{"status":200,"body":"Source A."})
    vm.mock_web(r".*b\.example.*",{"status":200,"body":"Source B."})
    vm.mock_llm(r"(?s).*Compare two public sources for factual conflict.*",json.dumps({"verdict":verdict,"confidence":confidence,"fact_a":fact_a,"fact_b":fact_b}))

def test_consistent(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/statement_conflict_attestor.py"); direct_vm.sender=direct_alice
    result(direct_vm,"CONSISTENT"); c.compare("s1","topic",A,B); assert c.get_result("s1").verdict=="CONSISTENT"

def test_conflicting(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/statement_conflict_attestor.py"); direct_vm.sender=direct_alice
    result(direct_vm,"CONFLICTING",90,"A says 10.","B says 20."); c.compare("s2","topic",A,B)
    assert c.get_result("s2").verdict=="CONFLICTING"

def test_unrelated(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/statement_conflict_attestor.py"); direct_vm.sender=direct_alice
    result(direct_vm,"UNRELATED"); c.compare("s3","topic",A,B); assert c.get_result("s3").verdict=="UNRELATED"

def test_low_confidence_fails_closed(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/statement_conflict_attestor.py"); direct_vm.sender=direct_alice
    result(direct_vm,"CONFLICTING",40); c.compare("s4","topic",A,B); assert c.get_result("s4").verdict=="UNDETERMINED"

def test_same_domain_rejected(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/statement_conflict_attestor.py"); direct_vm.sender=direct_alice
    with direct_vm.expect_revert("two independent HTTPS domains"):
        c.compare("s5","topic","https://example.com/a","https://www.example.com/b")

def test_validator_rejects_conflict_flip(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/statement_conflict_attestor.py"); direct_vm.sender=direct_alice
    result(direct_vm,"CONSISTENT"); c.compare("s6","topic",A,B)
    result(direct_vm,"CONFLICTING",90,"A says 10.","B says 20."); assert direct_vm.run_validator() is False


def test_validator_allows_nondecisive_fact_paraphrase(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/statement_conflict_attestor.py"); direct_vm.sender=direct_alice
    result(direct_vm,"CONFLICTING",90,"A says ten.","B says twenty."); c.compare("s7","topic",A,B)
    result(direct_vm,"CONFLICTING",90,"Source A reports 10.","Source B reports 20.")
    assert direct_vm.run_validator() is True
