# VerdictMesh Reviewer Guide

## What to inspect first

1. `docs/ARCHITECTURE.md` — state machine, source panel, challenge, settlement.
2. `docs/THREAT_MODEL.md` — explicit attack model and limitations.
3. `DECISIONS.md` — why conflict beats simple majority and why live page bytes are not treated as immutable evidence.
4. `docs/PROOF_MANIFEST.json` — canonical CI and Studionet evidence once live verification is complete.

## Direct verification

```bash
python -m pip install -r requirements.txt
pytest tests/direct -v
genvm-lint check contracts/verdict_mesh.py
```

The direct suite is expected to cover:

- equal GEN bonds;
- role authorization;
- independent-domain enforcement;
- support / contradiction / conflict / insufficient aggregation;
- low-confidence fail-closed behavior;
- validator disagreement rejection;
- guaranteed challenge-window settlement lock;
- fresh-domain challenge requirement;
- full four-source re-resolution;
- claimant and respondent winner payouts;
- neutral split refunds;
- unaccepted-case recovery;
- duplicate-case and terminal-state protections.

## Live Studionet verification

The canonical live workflow will be pinned here after it succeeds.

The live test is designed to exercise real GEN escrow and a challenge that changes the evidence set before deterministic settlement.
