"""Canonical live Studionet proof for VerdictMesh."""

import pytest
from gltest import get_contract_factory
from gltest.assertions import tx_execution_succeeded


def _field(value, name):
    if isinstance(value, dict):
        return value.get(name)
    return getattr(value, name)


@pytest.mark.integration
def test_verdictmesh_conflict_challenge_and_split_refund_live(default_account, accounts):
    assert len(accounts) >= 2
    claimant_account = default_account
    respondent_account = accounts[1]

    factory = get_contract_factory("VerdictMesh")
    contract = factory.deploy(
        account=claimant_account,
        consensus_max_rotations=4,
    )

    print(f"VERDICTMESH_CONTRACT={contract.address}", flush=True)
    print(f"VERDICTMESH_CLAIMANT={claimant_account.address}", flush=True)
    print(f"VERDICTMESH_RESPONDENT={respondent_account.address}", flush=True)

    claimant = contract.connect(account=claimant_account)
    respondent = contract.connect(account=respondent_account)

    case_id = "example-domain-dispute-v1"
    stake = 1_000_000_000_000
    claim = "example.com is reserved for use in documentation examples."

    open_tx = claimant.open_case(
        args=[
            case_id,
            respondent_account.address,
            claim,
            "https://example.com",
            "https://www.rfc-editor.org/rfc/rfc2606",
        ]
    ).transact(
        value=stake,
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(open_tx)
    print(f"VERDICTMESH_OPEN_TX={open_tx.get('hash', '')}", flush=True)

    accept_tx = respondent.accept_case(
        args=[
            case_id,
            "https://www.iana.org/help/example-domains",
        ]
    ).transact(
        value=stake,
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(accept_tx)
    print(f"VERDICTMESH_ACCEPT_TX={accept_tx.get('hash', '')}", flush=True)

    resolve_tx = claimant.resolve(args=[case_id]).transact(
        consensus_max_rotations=4,
        wait_interval=10000,
        wait_retries=70,
    )
    assert tx_execution_succeeded(resolve_tx)
    print(f"VERDICTMESH_RESOLVE_TX={resolve_tx.get('hash', '')}", flush=True)

    initial = contract.get_case(args=[case_id]).call()
    initial_verdict = str(_field(initial, "verdict"))
    print(f"VERDICTMESH_INITIAL_VERDICT={initial_verdict}", flush=True)
    print(f"VERDICTMESH_INITIAL_SUPPORT={int(_field(initial, 'support_count'))}", flush=True)
    print(f"VERDICTMESH_INITIAL_CONTRADICT={int(_field(initial, 'contradict_count'))}", flush=True)
    print(f"VERDICTMESH_INITIAL_HASH={_field(initial, 'decision_hash')}", flush=True)
    print(f"VERDICTMESH_CHALLENGE_DEADLINE={int(_field(initial, 'challenge_deadline'))}", flush=True)

    assert initial_verdict == "SUPPORTED"
    assert int(_field(initial, "support_count")) >= 2
    assert int(_field(initial, "contradict_count")) == 0
    assert contract.is_settlement_ready(args=[case_id]).call() is False

    challenge_tx = respondent.challenge(
        args=[
            case_id,
            "https://raw.githubusercontent.com/maho0638/verdictmesh-genlayer/main/fixtures/contradict_example.html",
        ]
    ).transact(
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(challenge_tx)
    print(f"VERDICTMESH_CHALLENGE_TX={challenge_tx.get('hash', '')}", flush=True)

    reresolve_tx = claimant.resolve_challenge(args=[case_id]).transact(
        consensus_max_rotations=4,
        wait_interval=10000,
        wait_retries=80,
    )
    assert tx_execution_succeeded(reresolve_tx)
    print(f"VERDICTMESH_RERESOLVE_TX={reresolve_tx.get('hash', '')}", flush=True)

    final = contract.get_case(args=[case_id]).call()
    final_verdict = str(_field(final, "verdict"))
    print(f"VERDICTMESH_FINAL_VERDICT={final_verdict}", flush=True)
    print(f"VERDICTMESH_FINAL_SUPPORT={int(_field(final, 'support_count'))}", flush=True)
    print(f"VERDICTMESH_FINAL_CONTRADICT={int(_field(final, 'contradict_count'))}", flush=True)
    print(f"VERDICTMESH_RESOLUTION_ROUND={int(_field(final, 'resolution_round'))}", flush=True)
    print(f"VERDICTMESH_CHALLENGE_COUNT={int(_field(final, 'challenge_count'))}", flush=True)
    print(f"VERDICTMESH_FINAL_HASH={_field(final, 'decision_hash')}", flush=True)

    assert final_verdict == "CONFLICTED"
    assert int(_field(final, "support_count")) > 0
    assert int(_field(final, "contradict_count")) > 0
    assert int(_field(final, "resolution_round")) == 2
    assert int(_field(final, "challenge_count")) == 1
    assert contract.is_settlement_ready(args=[case_id]).call() is True

    split_tx = claimant.settle_split(args=[case_id]).transact(
        wait_interval=10000,
        wait_retries=50,
    )
    assert tx_execution_succeeded(split_tx)
    print(f"VERDICTMESH_SPLIT_TX={split_tx.get('hash', '')}", flush=True)

    settled = contract.get_case(args=[case_id]).call()
    assert str(_field(settled, "status")) == "SPLIT_REFUNDED"
    assert bool(_field(settled, "settled")) is True
    print("VERDICTMESH_FINAL_STATUS=SPLIT_REFUNDED", flush=True)
