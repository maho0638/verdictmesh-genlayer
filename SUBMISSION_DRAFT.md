# VerdictMesh — Conflict-Aware Bonded Disputes for GenLayer

## Submission status

READY FOR FINAL PORTAL REVIEW

## Summary

VerdictMesh is a native-GEN bonded factual-dispute primitive. A claimant and designated respondent post equal stakes, contribute independent public evidence, and let GenLayer validators classify each source separately before deterministic conflict-aware settlement.

This is not a generic "AI decides X" wrapper. The economic result is derived from a structured state machine, independent per-source consensus, hostname diversity, confidence floors, a material-conflict circuit breaker, a guaranteed challenge window, fresh counterevidence, full re-resolution, and terminal settlement rules.

## Why GenLayer is necessary

The decisive question is semantic: does each live public webpage support, contradict, or fail to establish the frozen claim?

A traditional deterministic contract cannot read and semantically interpret arbitrary public webpages. VerdictMesh uses GenLayer web access and LLM-capable nondeterministic execution for the bounded source judgments, then moves all economic consequences back into deterministic contract logic.

## Consensus model

Initial evidence comes from three distinct normalized hostnames:

- claimant source;
- respondent source;
- precommitted anchor source.

Each source is rendered and judged independently.

Allowed source votes:

- SUPPORT
- CONTRADICT
- INSUFFICIENT

Confidence below 65 becomes INSUFFICIENT.

Validators independently rerun each decisive source judgment and must agree on the normalized verdict while confidence remains within the fixed tolerance.

The contract never lets free-form rationale directly control funds.

## Conflict circuit breaker

VerdictMesh intentionally rejects ordinary majority logic for bonded disputes.

If at least one source SUPPORTS and another CONTRADICTS, the outcome is CONFLICTED even if the numerical majority is 2-to-1 or 3-to-1.

A winner is only economically actionable when decisive sources align without an opposite decisive vote.

## Challenge and settlement

Initial decisions cannot settle for one hour.

During that guaranteed window either party may submit exactly one new source from a fresh fourth hostname.

The challenged case performs a complete four-source re-resolution.

Settlement:

- SUPPORTED -> claimant receives both stakes.
- CONTRADICTED -> respondent receives both stakes.
- CONFLICTED / INSUFFICIENT -> each party receives its original stake.
- unaccepted cases -> claimant can recover after 24 hours.

Terminal state prevents double settlement.

## Verification

Canonical CI:

https://github.com/maho0638/verdictmesh-genlayer/actions/runs/36474368384

Result:

- 28 / 28 direct tests PASS
- GenVM lint PASS

Canonical Studionet proof:

https://github.com/maho0638/verdictmesh-genlayer/actions/runs/36473956643

Live contract:

https://explorer-studio.genlayer.com/address/0x00a9B05D97043b732Dfb296C7187A1E3F5617CD2

Live source SHA-256:

`b8d6f23422e5a43a263f8f715279080419af0524618bc8f7ac85b95609b95d59`

Canonical live lifecycle:

1. claimant opened case with native GEN stake;
2. respondent matched the GEN stake;
3. three-source resolution -> SUPPORTED, 3 support / 0 contradict;
4. settlement remained locked;
5. respondent submitted a fresh fourth-domain contradictory source;
6. complete re-resolution -> CONFLICTED, 3 support / 1 contradict;
7. deterministic split settlement returned both stakes;
8. terminal status -> SPLIT_REFUNDED.

All transaction hashes and decision hashes are in `docs/PROOF_MANIFEST.json`.

## Reproduction

```bash
python -m pip install -r requirements.txt
pytest tests/direct -v
genvm-lint check contracts/verdict_mesh.py
gltest tests/integration/test_verdictmesh_studionet.py -v -s --network studionet
```

## Security properties demonstrated

- independent source classification;
- substantive validator re-execution;
- low-confidence fail closed;
- normalized three-domain initial diversity;
- fresh-domain challenge requirement;
- prompt-injection-aware evidence handling;
- conflict-over-majority circuit breaker;
- one-hour settlement lock;
- challenge forces fresh consensus;
- equal native-GEN economic exposure;
- safe split refund for conflict/insufficiency;
- unaccepted-case recovery;
- terminal double-settlement protection;
- deterministic decision receipt hash.

## Explicit limitations

VerdictMesh does not prove source truth, source ownership independence, or immutable webpage bytes.

Hostname diversity blocks trivial duplicate-domain quorum construction but is not a proof that organizations are independent.

Because validators fetch live webpages independently, consensus is over bounded semantic judgments rather than byte-identical page snapshots.
