import json
from datetime import datetime, timedelta, timezone

import pytest


CLAIMANT_URL = "https://claimant.example/evidence"
RESPONDENT_URL = "https://respondent.example/evidence"
ANCHOR_URL = "https://anchor.example/evidence"
CHALLENGE_URL = "https://challenge.example/evidence"
STAKE = 2500


@pytest.fixture(autouse=True)
def strict_direct_vm(direct_vm):
    direct_vm.strict_mocks = True
    direct_vm.check_pickling = True


def _address(account):
    return "0x" + account.hex()


def _domain_regex(url):
    domain = url.split("://", 1)[1].split("/", 1)[0]
    return domain.replace(".", r"\.")


def mock_vote(direct_vm, url, verdict, confidence=92, body=None):
    pattern = _domain_regex(url)
    direct_vm.mock_web(
        rf".*{pattern}.*",
        {
            "status": 200,
            "body": body or f"Controlled evidence from {url}.",
        },
    )
    direct_vm.mock_llm(
        rf"(?s).*SOURCE URL:.*{pattern}.*",
        json.dumps(
            {
                "verdict": verdict,
                "confidence": confidence,
                "note": f"{verdict} from controlled evidence.",
            }
        ),
    )


def mock_panel(direct_vm, a="SUPPORT", b="SUPPORT", c="SUPPORT", d=None):
    direct_vm.clear_mocks()
    mock_vote(direct_vm, CLAIMANT_URL, a)
    mock_vote(direct_vm, RESPONDENT_URL, b)
    mock_vote(direct_vm, ANCHOR_URL, c)
    if d is not None:
        mock_vote(direct_vm, CHALLENGE_URL, d)


def create_open_case(direct_vm, contract, claimant, respondent, case_id="case-1"):
    direct_vm.sender = claimant
    direct_vm.value = STAKE
    contract.open_case(
        case_id,
        _address(respondent),
        "The referenced release is publicly documented.",
        CLAIMANT_URL,
        ANCHOR_URL,
    )
    direct_vm.value = 0
    direct_vm.deal(contract.address, STAKE)


def accept_case(direct_vm, contract, respondent, case_id="case-1"):
    direct_vm.sender = respondent
    direct_vm.value = STAKE
    contract.accept_case(case_id, RESPONDENT_URL)
    direct_vm.value = 0
    direct_vm.deal(contract.address, STAKE * 2)


def create_active_case(direct_vm, contract, claimant, respondent, case_id="case-1"):
    create_open_case(direct_vm, contract, claimant, respondent, case_id)
    accept_case(direct_vm, contract, respondent, case_id)


def test_open_and_accept_equal_bond(direct_vm, direct_deploy, direct_alice, direct_bob):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_active_case(direct_vm, c, direct_alice, direct_bob)
    case = c.get_case("case-1")
    assert case.status == "ACTIVE"
    assert int(case.stake) == STAKE
    assert str(case.respondent).lower() == _address(direct_bob).lower()
    assert int(case.accepted_at) > 0
    assert case.policy_version == "VERDICT_MESH_V1"


def test_zero_stake_is_rejected(direct_vm, direct_deploy, direct_alice, direct_bob):
    c = direct_deploy("contracts/verdict_mesh.py")
    direct_vm.sender = direct_alice
    direct_vm.value = 0
    with direct_vm.expect_revert("Stake must be greater than zero"):
        c.open_case(
            "zero",
            _address(direct_bob),
            "A sufficiently descriptive factual claim.",
            CLAIMANT_URL,
            ANCHOR_URL,
        )


def test_claimant_cannot_dispute_self(direct_vm, direct_deploy, direct_alice):
    c = direct_deploy("contracts/verdict_mesh.py")
    direct_vm.sender = direct_alice
    direct_vm.value = STAKE
    with direct_vm.expect_revert("must be different"):
        c.open_case(
            "self",
            _address(direct_alice),
            "A sufficiently descriptive factual claim.",
            CLAIMANT_URL,
            ANCHOR_URL,
        )


def test_initial_sources_require_independent_domains(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    direct_vm.sender = direct_alice
    direct_vm.value = STAKE
    with direct_vm.expect_revert("independent domains"):
        c.open_case(
            "same-domain",
            _address(direct_bob),
            "A sufficiently descriptive factual claim.",
            "https://example.com/a",
            "https://www.example.com/b",
        )


def test_only_designated_respondent_can_accept(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_open_case(direct_vm, c, direct_alice, direct_bob)
    direct_vm.sender = direct_charlie
    direct_vm.value = STAKE
    with direct_vm.expect_revert("designated respondent"):
        c.accept_case("case-1", RESPONDENT_URL)


def test_respondent_must_match_stake(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_open_case(direct_vm, c, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    direct_vm.value = STAKE - 1
    with direct_vm.expect_revert("match the claimant stake"):
        c.accept_case("case-1", RESPONDENT_URL)


def test_all_support_resolves_supported_with_challenge_lock(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_active_case(direct_vm, c, direct_alice, direct_bob)
    mock_panel(direct_vm)
    c.resolve("case-1")

    case = c.get_case("case-1")
    assert case.status == "RESOLVED"
    assert case.verdict == "SUPPORTED"
    assert int(case.support_count) == 3
    assert int(case.contradict_count) == 0
    assert int(case.resolution_round) == 1
    assert len(case.decision_hash) == 64
    assert int(case.challenge_deadline) > int(case.resolved_at)
    assert c.is_settlement_ready("case-1") is False


def test_mixed_decisive_votes_trigger_conflict_circuit_breaker(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_active_case(direct_vm, c, direct_alice, direct_bob)
    mock_panel(direct_vm, "SUPPORT", "CONTRADICT", "SUPPORT")
    c.resolve("case-1")
    case = c.get_case("case-1")
    assert case.verdict == "CONFLICTED"
    assert int(case.support_count) == 2
    assert int(case.contradict_count) == 1


def test_low_confidence_votes_fail_closed_to_insufficient(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_active_case(direct_vm, c, direct_alice, direct_bob)

    direct_vm.clear_mocks()
    mock_vote(direct_vm, CLAIMANT_URL, "SUPPORT", 40)
    mock_vote(direct_vm, RESPONDENT_URL, "SUPPORT", 40)
    mock_vote(direct_vm, ANCHOR_URL, "SUPPORT", 91)
    c.resolve("case-1")

    case = c.get_case("case-1")
    assert case.verdict == "INSUFFICIENT"
    assert int(case.support_count) == 1
    assert int(case.insufficient_count) == 2


def test_validator_rejects_changed_source_judgments(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_active_case(direct_vm, c, direct_alice, direct_bob)
    mock_panel(direct_vm)
    c.resolve("case-1")

    mock_panel(direct_vm, "CONTRADICT", "CONTRADICT", "CONTRADICT")
    assert direct_vm.run_validator() is False


def test_challenge_requires_fresh_domain(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_active_case(direct_vm, c, direct_alice, direct_bob)
    mock_panel(direct_vm)
    c.resolve("case-1")

    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("fresh domain"):
        c.challenge("case-1", "https://www.claimant.example/new")


def test_only_case_party_can_challenge(
    direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_active_case(direct_vm, c, direct_alice, direct_bob)
    mock_panel(direct_vm)
    c.resolve("case-1")

    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("Only a case party"):
        c.challenge("case-1", CHALLENGE_URL)


def test_fresh_counterevidence_can_turn_support_into_conflict(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_active_case(direct_vm, c, direct_alice, direct_bob)
    mock_panel(direct_vm)
    c.resolve("case-1")

    direct_vm.sender = direct_bob
    c.challenge("case-1", CHALLENGE_URL)

    mock_panel(direct_vm, "SUPPORT", "SUPPORT", "SUPPORT", "CONTRADICT")
    c.resolve_challenge("case-1")

    case = c.get_case("case-1")
    assert case.verdict == "CONFLICTED"
    assert int(case.resolution_round) == 2
    assert int(case.challenge_count) == 1
    assert int(case.support_count) == 3
    assert int(case.contradict_count) == 1
    assert c.is_settlement_ready("case-1") is True


def test_supported_case_pays_claimant_after_fresh_recheck(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_active_case(direct_vm, c, direct_alice, direct_bob)
    mock_panel(direct_vm)
    c.resolve("case-1")

    direct_vm.sender = direct_alice
    c.challenge("case-1", CHALLENGE_URL)
    mock_panel(direct_vm, "SUPPORT", "SUPPORT", "SUPPORT", "SUPPORT")
    c.resolve_challenge("case-1")

    paid = c.settle_winner("case-1")
    assert int(paid) == STAKE * 2
    assert c.get_case("case-1").status == "CLAIMANT_PAID"


def test_contradicted_case_pays_respondent_after_fresh_recheck(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_active_case(direct_vm, c, direct_alice, direct_bob)
    mock_panel(direct_vm, "CONTRADICT", "CONTRADICT", "CONTRADICT")
    c.resolve("case-1")

    direct_vm.sender = direct_bob
    c.challenge("case-1", CHALLENGE_URL)
    mock_panel(
        direct_vm,
        "CONTRADICT",
        "CONTRADICT",
        "CONTRADICT",
        "CONTRADICT",
    )
    c.resolve_challenge("case-1")

    paid = c.settle_winner("case-1")
    assert int(paid) == STAKE * 2
    assert c.get_case("case-1").status == "RESPONDENT_PAID"


def test_conflict_returns_equal_stakes_after_challenge(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_active_case(direct_vm, c, direct_alice, direct_bob)
    mock_panel(direct_vm)
    c.resolve("case-1")

    direct_vm.sender = direct_bob
    c.challenge("case-1", CHALLENGE_URL)
    mock_panel(direct_vm, "SUPPORT", "SUPPORT", "SUPPORT", "CONTRADICT")
    c.resolve_challenge("case-1")

    returned = c.settle_split("case-1")
    assert int(returned) == STAKE * 2
    case = c.get_case("case-1")
    assert case.status == "SPLIT_REFUNDED"
    assert case.settled is True


def test_winner_settlement_is_locked_during_initial_challenge_window(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_active_case(direct_vm, c, direct_alice, direct_bob)
    mock_panel(direct_vm)
    c.resolve("case-1")

    with direct_vm.expect_revert("not ready for settlement"):
        c.settle_winner("case-1")


def test_unchallenged_winner_can_settle_after_window(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_active_case(direct_vm, c, direct_alice, direct_bob)
    mock_panel(direct_vm)
    c.resolve("case-1")

    direct_vm.warp((datetime.now(timezone.utc) + timedelta(hours=2)).isoformat())
    assert c.is_settlement_ready("case-1") is True
    c.settle_winner("case-1")
    assert c.get_case("case-1").status == "CLAIMANT_PAID"


def test_duplicate_case_id_is_rejected(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_open_case(direct_vm, c, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    direct_vm.value = STAKE
    with direct_vm.expect_revert("Case already exists"):
        c.open_case(
            "case-1",
            _address(direct_bob),
            "Another factual claim with sufficient detail.",
            CLAIMANT_URL,
            ANCHOR_URL,
        )


def test_unaccepted_case_can_be_cancelled_after_deadline(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_open_case(direct_vm, c, direct_alice, direct_bob)
    direct_vm.warp((datetime.now(timezone.utc) + timedelta(hours=25)).isoformat())
    direct_vm.sender = direct_alice
    refunded = c.cancel_unaccepted("case-1")
    assert int(refunded) == STAKE
    assert c.get_case("case-1").status == "CANCELLED"


def test_cancel_is_blocked_while_acceptance_window_open(
    direct_vm, direct_deploy, direct_alice, direct_bob
):
    c = direct_deploy("contracts/verdict_mesh.py")
    create_open_case(direct_vm, c, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("Acceptance window is still open"):
        c.cancel_unaccepted("case-1")
