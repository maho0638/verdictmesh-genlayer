"""Expanded live Studionet proof for VerdictMesh evidence-consensus primitives."""

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded

RAW_A = "https://raw.githubusercontent.com/maho0638/verdictmesh-genlayer/main/fixtures/catalog_a.txt"
GITHUB_B = "https://github.com/maho0638/verdictmesh-genlayer/raw/refs/heads/main/fixtures/catalog_b.txt"
JSDELIVR_C = "https://cdn.jsdelivr.net/gh/maho0638/verdictmesh-genlayer@main/fixtures/catalog_c.txt"

def _field(value, name):
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name)

@pytest.mark.integration
def test_evidence_panel_live(default_account):
    c = get_contract_factory("EvidencePanel").deploy(account=default_account, consensus_max_rotations=4)
    print(f"VERDICTMESH_PANEL_CONTRACT={c.address}", flush=True)
    rid = "panel-release-v1"
    tx = c.evaluate(args=[rid, "The VerdictMesh controlled catalog release code is VM-2026-09.", RAW_A, GITHUB_B, JSDELIVR_C]).transact(
        consensus_max_rotations=4, wait_interval=10000, wait_retries=80
    )
    assert tx_execution_succeeded(tx)
    print(f"VERDICTMESH_PANEL_TX={tx.get('hash','')}", flush=True)
    r = c.get_result(args=[rid]).call()
    print(f"VERDICTMESH_PANEL_VERDICT={_field(r,'verdict')}", flush=True)
    print(f"VERDICTMESH_PANEL_SUPPORT={int(_field(r,'support_count'))}", flush=True)
    assert str(_field(r,"verdict")) == "SUPPORTED"
    assert int(_field(r,"support_count")) == 3

@pytest.mark.integration
def test_as_of_panel_live(default_account):
    c = get_contract_factory("AsOfEvidencePanel").deploy(account=default_account, consensus_max_rotations=4)
    print(f"VERDICTMESH_ASOF_CONTRACT={c.address}", flush=True)
    rid = "asof-release-v1"
    tx = c.evaluate(args=[rid, "The VerdictMesh controlled catalog release code is VM-2026-09.", "2026-12-31", RAW_A, GITHUB_B, JSDELIVR_C]).transact(
        consensus_max_rotations=4, wait_interval=10000, wait_retries=90
    )
    assert tx_execution_succeeded(tx)
    print(f"VERDICTMESH_ASOF_TX={tx.get('hash','')}", flush=True)
    r = c.get_result(args=[rid]).call()
    print(f"VERDICTMESH_ASOF_VERDICT={_field(r,'verdict')}", flush=True)
    print(f"VERDICTMESH_ASOF_ELIGIBLE={int(_field(r,'eligible_count'))}", flush=True)
    print(f"VERDICTMESH_ASOF_DATE_A={_field(r,'date_a')}", flush=True)
    print(f"VERDICTMESH_ASOF_DATE_C={_field(r,'date_c')}", flush=True)
    assert str(_field(r,"verdict")) == "SUPPORTED"
    assert int(_field(r,"eligible_count")) == 2

@pytest.mark.integration
def test_consensus_field_extractor_live(default_account):
    c = get_contract_factory("ConsensusFieldExtractor").deploy(account=default_account, consensus_max_rotations=4)
    print(f"VERDICTMESH_FIELD_CONTRACT={c.address}", flush=True)
    rid = "field-release-v1"
    tx = c.extract(args=[rid, "Release code", RAW_A, GITHUB_B, JSDELIVR_C]).transact(
        consensus_max_rotations=4, wait_interval=10000, wait_retries=80
    )
    assert tx_execution_succeeded(tx)
    print(f"VERDICTMESH_FIELD_TX={tx.get('hash','')}", flush=True)
    r = c.get_result(args=[rid]).call()
    print(f"VERDICTMESH_FIELD_VERDICT={_field(r,'verdict')}", flush=True)
    print(f"VERDICTMESH_FIELD_VALUE={_field(r,'consensus_value')}", flush=True)
    print(f"VERDICTMESH_FIELD_AGREEMENT={int(_field(r,'agreement_count'))}", flush=True)
    assert str(_field(r,"verdict")) == "AGREED"
    assert str(_field(r,"consensus_value")) == "vm-2026-09"
    assert int(_field(r,"agreement_count")) == 3

@pytest.mark.integration
def test_numeric_consensus_oracle_live(default_account):
    c = get_contract_factory("NumericConsensusOracle").deploy(account=default_account, consensus_max_rotations=4)
    print(f"VERDICTMESH_NUMERIC_CONTRACT={c.address}", flush=True)
    rid = "numeric-nodes-v1"
    tx = c.evaluate(args=[rid, "Active nodes", "nodes", 2, RAW_A, GITHUB_B, JSDELIVR_C]).transact(
        consensus_max_rotations=4, wait_interval=10000, wait_retries=90
    )
    assert tx_execution_succeeded(tx)
    print(f"VERDICTMESH_NUMERIC_TX={tx.get('hash','')}", flush=True)
    r = c.get_result(args=[rid]).call()
    print(f"VERDICTMESH_NUMERIC_VERDICT={_field(r,'verdict')}", flush=True)
    print(f"VERDICTMESH_NUMERIC_VALUE={int(_field(r,'consensus_value'))}", flush=True)
    print(f"VERDICTMESH_NUMERIC_SPREAD={int(_field(r,'spread'))}", flush=True)
    assert str(_field(r,"verdict")) == "CONSENSUS"
    assert int(_field(r,"consensus_value")) == 100
    assert int(_field(r,"spread")) == 2

@pytest.mark.integration
def test_claim_dependency_graph_live(default_account):
    c = get_contract_factory("ClaimDependencyGraph").deploy(account=default_account, consensus_max_rotations=4)
    print(f"VERDICTMESH_GRAPH_CONTRACT={c.address}", flush=True)
    create_root = c.create_claim(args=["foundation", "", "Foundation step is complete.", RAW_A, GITHUB_B]).transact(
        wait_interval=10000, wait_retries=50
    )
    assert tx_execution_succeeded(create_root)
    print(f"VERDICTMESH_GRAPH_CREATE_ROOT_TX={create_root.get('hash','')}", flush=True)
    create_child = c.create_claim(args=["delivery", "foundation", "Delivery step is complete.", RAW_A, GITHUB_B]).transact(
        wait_interval=10000, wait_retries=50
    )
    assert tx_execution_succeeded(create_child)
    print(f"VERDICTMESH_GRAPH_CREATE_CHILD_TX={create_child.get('hash','')}", flush=True)
    assert c.is_unlocked(args=["delivery"]).call() is False
    resolve_root = c.resolve(args=["foundation"]).transact(
        consensus_max_rotations=4, wait_interval=10000, wait_retries=80
    )
    assert tx_execution_succeeded(resolve_root)
    print(f"VERDICTMESH_GRAPH_RESOLVE_ROOT_TX={resolve_root.get('hash','')}", flush=True)
    assert c.is_unlocked(args=["delivery"]).call() is True
    resolve_child = c.resolve(args=["delivery"]).transact(
        consensus_max_rotations=4, wait_interval=10000, wait_retries=80
    )
    assert tx_execution_succeeded(resolve_child)
    print(f"VERDICTMESH_GRAPH_RESOLVE_CHILD_TX={resolve_child.get('hash','')}", flush=True)
    root = c.get_claim(args=["foundation"]).call()
    child = c.get_claim(args=["delivery"]).call()
    print(f"VERDICTMESH_GRAPH_ROOT={_field(root,'verdict')}", flush=True)
    print(f"VERDICTMESH_GRAPH_CHILD={_field(child,'verdict')}", flush=True)
    assert str(_field(root,"verdict")) == "SUPPORTED"
    assert str(_field(child,"verdict")) == "SUPPORTED"

@pytest.mark.integration
def test_policy_change_attestor_live(default_account):
    c = get_contract_factory("PolicyChangeAttestor").deploy(account=default_account, consensus_max_rotations=4)
    print(f"VERDICTMESH_POLICY_CONTRACT={c.address}", flush=True)
    rid = "policy-unchanged-v1"
    baseline = "Example access policy allows documentation use."
    tx = c.attest(args=[rid, baseline, RAW_A]).transact(
        consensus_max_rotations=4, wait_interval=10000, wait_retries=70
    )
    assert tx_execution_succeeded(tx)
    print(f"VERDICTMESH_POLICY_TX={tx.get('hash','')}", flush=True)
    r = c.get_result(args=[rid]).call()
    print(f"VERDICTMESH_POLICY_VERDICT={_field(r,'verdict')}", flush=True)
    print(f"VERDICTMESH_POLICY_BASELINE_HASH={_field(r,'baseline_hash')}", flush=True)
    assert str(_field(r,"verdict")) == "UNCHANGED"
    assert len(str(_field(r,"baseline_hash"))) == 64

@pytest.mark.integration
def test_statement_conflict_attestor_live(default_account):
    c = get_contract_factory("StatementConflictAttestor").deploy(account=default_account, consensus_max_rotations=4)
    print(f"VERDICTMESH_CONFLICT_CONTRACT={c.address}", flush=True)
    rid = "quota-conflict-v1"
    tx = c.compare(args=[rid, "The test quota measured in units.", RAW_A, GITHUB_B]).transact(
        consensus_max_rotations=4, wait_interval=10000, wait_retries=80
    )
    assert tx_execution_succeeded(tx)
    print(f"VERDICTMESH_CONFLICT_TX={tx.get('hash','')}", flush=True)
    r = c.get_result(args=[rid]).call()
    print(f"VERDICTMESH_CONFLICT_VERDICT={_field(r,'verdict')}", flush=True)
    print(f"VERDICTMESH_CONFLICT_FACT_A={_field(r,'fact_a')}", flush=True)
    print(f"VERDICTMESH_CONFLICT_FACT_B={_field(r,'fact_b')}", flush=True)
    assert str(_field(r,"verdict")) == "CONFLICTING"


@pytest.mark.integration
def test_primary_corroboration_gate_live(default_account):
    c = get_contract_factory("PrimaryCorroborationGate").deploy(account=default_account, consensus_max_rotations=4)
    print(f"VERDICTMESH_CORROBORATION_CONTRACT={c.address}", flush=True)
    rid = "corroboration-release-v1"
    tx = c.verify(args=[rid, "The VerdictMesh controlled catalog release code is VM-2026-09.", RAW_A, GITHUB_B, JSDELIVR_C]).transact(
        consensus_max_rotations=4, wait_interval=10000, wait_retries=90
    )
    assert tx_execution_succeeded(tx)
    print(f"VERDICTMESH_CORROBORATION_TX={tx.get('hash','')}", flush=True)
    r = c.get_result(args=[rid]).call()
    print(f"VERDICTMESH_CORROBORATION_VERDICT={_field(r,'verdict')}", flush=True)
    assert str(_field(r,"verdict")) == "VERIFIED"

@pytest.mark.integration
def test_provenance_chain_attestor_live(default_account):
    c = get_contract_factory("ProvenanceChainAttestor").deploy(account=default_account, consensus_max_rotations=4)
    print(f"VERDICTMESH_PROVENANCE_CONTRACT={c.address}", flush=True)
    rid = "provenance-release-v1"
    tx = c.attest(args=[rid, "The VerdictMesh controlled catalog release code is VM-2026-09.", RAW_A, GITHUB_B]).transact(
        consensus_max_rotations=4, wait_interval=10000, wait_retries=90
    )
    assert tx_execution_succeeded(tx)
    print(f"VERDICTMESH_PROVENANCE_TX={tx.get('hash','')}", flush=True)
    r = c.get_result(args=[rid]).call()
    print(f"VERDICTMESH_PROVENANCE_VERDICT={_field(r,'verdict')}", flush=True)
    print(f"VERDICTMESH_PROVENANCE_ORIGIN={_field(r,'origin_label')}", flush=True)
    assert str(_field(r,"verdict")) == "PROVENANCE_CONFIRMED"
    assert bool(_field(r,"primary_attributes_origin")) is True

@pytest.mark.integration
def test_correction_status_attestor_live(default_account):
    c = get_contract_factory("CorrectionStatusAttestor").deploy(account=default_account, consensus_max_rotations=4)
    print(f"VERDICTMESH_CORRECTION_CONTRACT={c.address}", flush=True)
    rid = "correction-current-v1"
    statement = "Example access policy allows documentation use."
    tx = c.attest(args=[rid, statement, RAW_A]).transact(
        consensus_max_rotations=4, wait_interval=10000, wait_retries=80
    )
    assert tx_execution_succeeded(tx)
    print(f"VERDICTMESH_CORRECTION_TX={tx.get('hash','')}", flush=True)
    r = c.get_result(args=[rid]).call()
    print(f"VERDICTMESH_CORRECTION_STATUS={_field(r,'status')}", flush=True)
    assert str(_field(r,"status")) == "CURRENT"

@pytest.mark.integration
def test_expiring_evidence_attestor_live(default_account):
    c = get_contract_factory("ExpiringEvidenceAttestor").deploy(account=default_account, consensus_max_rotations=4)
    print(f"VERDICTMESH_EXPIRING_CONTRACT={c.address}", flush=True)
    rid = "expiring-release-v1"
    tx = c.attest(args=[rid, "The VerdictMesh controlled catalog release code is VM-2026-09.", 3600, RAW_A, GITHUB_B]).transact(
        consensus_max_rotations=4, wait_interval=10000, wait_retries=80
    )
    assert tx_execution_succeeded(tx)
    print(f"VERDICTMESH_EXPIRING_TX={tx.get('hash','')}", flush=True)
    r = c.get_result(args=[rid]).call()
    print(f"VERDICTMESH_EXPIRING_VERDICT={_field(r,'verdict')}", flush=True)
    print(f"VERDICTMESH_EXPIRING_ROUND={int(_field(r,'round'))}", flush=True)
    print(f"VERDICTMESH_EXPIRING_VALID_UNTIL={int(_field(r,'valid_until'))}", flush=True)
    assert str(_field(r,"verdict")) == "SUPPORTED"
    assert int(_field(r,"round")) == 1
    assert c.is_active(args=[rid]).call() is True
