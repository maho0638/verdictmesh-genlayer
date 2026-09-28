# VerdictMesh Reviewer Guide

## Fast review

1. Read `docs/ARCHITECTURE.md` for the state machine and deterministic settlement rules.
2. Read `docs/THREAT_MODEL.md` for explicit safety boundaries and limitations.
3. Read `DECISIONS.md` for the rationale behind per-source classification and the conflict circuit breaker.
4. Inspect `docs/PROOF_MANIFEST.json` for canonical run IDs, source hash, contract address, transaction hashes, and decision hashes.
5. Inspect the live contract on GenLayer Explorer.

## Direct verification

```bash
python -m pip install -r requirements.txt
pytest tests/direct -v
genvm-lint check contracts/verdict_mesh.py
```

Canonical CI:

https://github.com/maho0638/verdictmesh-genlayer/actions/runs/36474368384

Expected result:

- 28 tests PASS
- GenVM lint PASS

The direct suite covers:

- equal claimant/respondent GEN bonds;
- role authorization;
- HTTPS and normalized independent-domain enforcement;
- SUPPORT / CONTRADICT / CONFLICTED / INSUFFICIENT aggregation;
- low-confidence fail-closed behavior;
- adversarial validator disagreement rejection;
- one-hour initial settlement lock;
- challenge expiry;
- fresh fourth-domain requirement;
- one-shot challenge semantics;
- complete four-source re-resolution;
- claimant and respondent winner payouts;
- neutral split refunds;
- incompatible settlement-path rejection;
- unaccepted-case recovery;
- duplicate case protection;
- deterministic decision-hash change after challenge.

## Live Studionet verification

Canonical run:

https://github.com/maho0638/verdictmesh-genlayer/actions/runs/36473956643

Contract:

https://explorer-studio.genlayer.com/address/0x00a9B05D97043b732Dfb296C7187A1E3F5617CD2

Source SHA-256:

`b8d6f23422e5a43a263f8f715279080419af0524618bc8f7ac85b95609b95d59`

Reproduce:

```bash
gltest tests/integration/test_verdictmesh_studionet.py -v -s --network studionet
```

Canonical live behavior:

- open native-GEN bonded case;
- respondent matches stake;
- resolve 3 independent public sources;
- observe SUPPORTED 3-0;
- confirm settlement remains locked;
- add a fresh contradictory fourth-domain challenge source;
- re-run all 4 source judgments;
- observe CONFLICTED 3-1;
- settle through split refund;
- verify terminal SPLIT_REFUNDED state.

The challenge fixture is intentionally controlled and clearly labeled as a test fixture. Its purpose is to prove that material counterevidence changes the consensus path and economic outcome rather than being ignored as metadata.
