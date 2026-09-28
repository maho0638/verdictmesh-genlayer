# VerdictMesh Reviewer Guide

VerdictMesh is one Intelligent Contracts contribution with 12 distinct evidence-consensus primitives.

## Fast review

1. Read `CONTRACTS.md` for all 12 mechanisms and their deterministic invariants.
2. Read `docs/ARCHITECTURE.md` for the shared nondeterministic/deterministic boundary.
3. Read `docs/THREAT_MODEL.md` and `DECISIONS.md`.
4. Inspect `docs/PROOF_MANIFEST.json`.
5. Inspect the canonical CI and full Studionet proof runs.

## Direct verification

```bash
python -m pip install -r requirements.txt
pytest tests/direct -v
for f in contracts/*.py; do genvm-lint check "$f"; done
```

Canonical CI:

https://github.com/maho0638/verdictmesh-genlayer/actions/runs/36484767096

Expected result:

- **98 tests PASS**
- **12 / 12 contracts pass GenVM lint**

The direct suite includes confidence fail-closed tests, independent-domain invariants, adversarial validator disagreement, temporal cutoff rules, semantic field disagreement, numeric divergence, dependency locking, baseline hash binding, provenance/correction semantics, TTL refresh, challenge timing, incompatible settlement-path rejection, and terminal settlement protection.

## Live Studionet verification

Canonical run:

https://github.com/maho0638/verdictmesh-genlayer/actions/runs/36484767134

Canonical commit:

`042ce06aa40722bb31130a5baaa5a2d0014b4cc2`

Reproduce:

```bash
gltest tests/integration/test_verdictmesh_studionet.py -v -s --network studionet
gltest tests/integration/test_verdictmesh_catalog_studionet.py -v -s --network studionet
```

Expected result:

- bonded dispute lifecycle: **1 / 1 PASS**
- expanded catalog: **11 / 11 PASS**
- total: **12 / 12 live contracts**

Flagship contract:

https://explorer-studio.genlayer.com/address/0xe3f1E70344F58C3280542dBdC6a4Bfc533C5e6B0

Flagship live path:

`open -> accept equal GEN bond -> SUPPORTED 3-0 -> settlement lock -> fresh challenge -> CONFLICTED 3-1 -> SPLIT_REFUNDED`

The expanded suite separately deploys and exercises all other 11 contracts.

All live addresses, transaction hashes, source SHA-256 hashes, and observed outputs are in `docs/PROOF_MANIFEST.json`.
