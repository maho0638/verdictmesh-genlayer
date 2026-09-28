import json

URL="https://status.example/e"

def setup(vm,status,confidence=90,correction=""):
    vm.clear_mocks()
    vm.mock_web(r".*status\.example.*",{"status":200,"body":"Controlled status evidence."})
    vm.mock_llm(r"(?s).*Determine the status of one frozen public statement.*",json.dumps({"status":status,"confidence":confidence,"correction":correction}))

def test_current(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/correction_status_attestor.py"); direct_vm.sender=direct_alice
    setup(direct_vm,"CURRENT"); c.attest("cs1","Statement.",URL); assert c.get_result("cs1").status=="CURRENT"

def test_corrected(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/correction_status_attestor.py"); direct_vm.sender=direct_alice
    setup(direct_vm,"CORRECTED",90,"Replacement statement."); c.attest("cs2","Statement.",URL)
    r=c.get_result("cs2"); assert r.status=="CORRECTED"; assert r.correction=="Replacement statement."

def test_retracted(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/correction_status_attestor.py"); direct_vm.sender=direct_alice
    setup(direct_vm,"RETRACTED"); c.attest("cs3","Statement.",URL); assert c.get_result("cs3").status=="RETRACTED"

def test_low_confidence_fails_closed(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/correction_status_attestor.py"); direct_vm.sender=direct_alice
    setup(direct_vm,"CORRECTED",40,"Maybe."); c.attest("cs4","Statement.",URL); assert c.get_result("cs4").status=="UNDETERMINED"

def test_non_https_rejected(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/correction_status_attestor.py"); direct_vm.sender=direct_alice
    with direct_vm.expect_revert("valid HTTPS"): c.attest("cs5","Statement.","http://status.example")

def test_validator_rejects_status_flip(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/correction_status_attestor.py"); direct_vm.sender=direct_alice
    setup(direct_vm,"CURRENT"); c.attest("cs6","Statement.",URL)
    setup(direct_vm,"RETRACTED"); assert direct_vm.run_validator() is False


def test_validator_allows_nondecisive_correction_paraphrase(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/correction_status_attestor.py"); direct_vm.sender=direct_alice
    setup(direct_vm,"CORRECTED",90,"Replacement A."); c.attest("cs7","Statement.",URL)
    setup(direct_vm,"CORRECTED",90,"Equivalent replacement wording.")
    assert direct_vm.run_validator() is True
