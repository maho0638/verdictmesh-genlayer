import json

A="https://a.example/e"; B="https://b.example/e"; C="https://c.example/e"

def item(vm,url,verdict,date,confidence=90):
    domain=url.split("://",1)[1].split("/",1)[0].replace(".",r"\.")
    vm.mock_web(rf".*{domain}.*",{"status":200,"body":"Controlled dated evidence."})
    vm.mock_llm(rf"(?s).*SOURCE URL:.*{domain}.*",json.dumps({"verdict":verdict,"confidence":confidence,"published_on":date}))

def setup(vm,rows):
    vm.clear_mocks()
    for url,verdict,date,confidence in rows: item(vm,url,verdict,date,confidence)

def test_pre_cutoff_support_counts(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/as_of_evidence_panel.py"); direct_vm.sender=direct_alice
    setup(direct_vm,[(A,"SUPPORT","2026-01-01",90),(B,"SUPPORT","2026-02-01",91),(C,"SUPPORT","2026-03-01",92)])
    c.evaluate("a1","Claim.","2026-06-01",A,B,C)
    r=c.get_result("a1"); assert r.verdict=="SUPPORTED"; assert int(r.eligible_count)==3

def test_post_cutoff_is_excluded(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/as_of_evidence_panel.py"); direct_vm.sender=direct_alice
    setup(direct_vm,[(A,"SUPPORT","2026-01-01",90),(B,"SUPPORT","2026-02-01",90),(C,"SUPPORT","2027-01-01",90)])
    c.evaluate("a2","Claim.","2026-06-01",A,B,C)
    r=c.get_result("a2"); assert r.verdict=="SUPPORTED"; assert int(r.eligible_count)==2; assert r.vote_c=="INSUFFICIENT"

def test_unknown_date_cannot_count(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/as_of_evidence_panel.py"); direct_vm.sender=direct_alice
    setup(direct_vm,[(A,"SUPPORT","UNKNOWN",90),(B,"SUPPORT","2026-02-01",90),(C,"INSUFFICIENT","UNKNOWN",90)])
    c.evaluate("a3","Claim.","2026-06-01",A,B,C)
    r=c.get_result("a3"); assert r.verdict=="INSUFFICIENT"; assert int(r.eligible_count)==1

def test_pre_cutoff_conflict_is_preserved(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/as_of_evidence_panel.py"); direct_vm.sender=direct_alice
    setup(direct_vm,[(A,"SUPPORT","2026-01-01",90),(B,"CONTRADICT","2026-02-01",90),(C,"SUPPORT","2027-01-01",90)])
    c.evaluate("a4","Claim.","2026-06-01",A,B,C)
    assert c.get_result("a4").verdict=="CONFLICTED"

def test_requires_independent_domains(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/as_of_evidence_panel.py"); direct_vm.sender=direct_alice
    with direct_vm.expect_revert("three independent HTTPS domains"):
        c.evaluate("a5","Claim.","2026-06-01","https://example.com/a","https://www.example.com/b",C)

def test_validator_rejects_date_change(direct_vm,direct_deploy,direct_alice):
    c=direct_deploy("contracts/as_of_evidence_panel.py"); direct_vm.sender=direct_alice
    rows=[(A,"SUPPORT","2026-01-01",90),(B,"SUPPORT","2026-02-01",90),(C,"SUPPORT","2026-03-01",90)]
    setup(direct_vm,rows); c.evaluate("a6","Claim.","2026-06-01",A,B,C)
    rows[0]=(A,"SUPPORT","2027-01-01",90); setup(direct_vm,rows)
    assert direct_vm.run_validator() is False
