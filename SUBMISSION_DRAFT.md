# VerdictMesh — Evidence Consensus Primitives for GenLayer

## Submission status

READY FOR FINAL PORTAL REVIEW

## Summary

VerdictMesh is a catalog of 12 reusable GenLayer Intelligent Contracts for conflict-aware public-web evidence.

The suite covers independent source panels, historical "as-of" evidence, structured field consensus, numeric tolerance, prerequisite claim graphs, policy-change detection, direct statement-conflict detection, primary-source corroboration, provenance chains, correction/retraction status, expiring evidence, and a symmetric native-GEN bonded dispute lifecycle.

VerdictMesh is intentionally distinct from Sightline: Sightline evaluates visual evidence; VerdictMesh focuses on **live public-web evidence, source disagreement, temporal eligibility, provenance, and economic adjudication**.

## Why GenLayer is necessary

Traditional deterministic smart contracts cannot fetch arbitrary live webpages and semantically determine whether a source supports a claim, contradicts another source, attributes a claim to an origin, represents a correction, or expresses a value within a semantic field.

VerdictMesh uses GenLayer nondeterministic web + LLM execution only for bounded observations. Validators independently reproduce the decisive fields. Deterministic contract code then performs quorum, conflict, cutoff, tolerance, dependency, expiry, challenge, and settlement logic.

## What makes the suite distinct

This is not one prompt copied 12 times.

The contracts have different state models and deterministic invariants:

- source-vote conflict circuit breaking;
- pre-cutoff temporal eligibility;
- semantic field equality;
- numeric spread tolerance;
- prerequisite graph locking;
- frozen-baseline change detection;
- pairwise statement conflict classification;
- primary-source plus corroborator requirements;
- provenance attribution plus origin verification;
- current/corrected/retracted state;
- TTL expiry and refresh rounds;
- equal-GEN bonded dispute settlement with challenge.

## Security model

- source text is explicitly treated as untrusted evidence;
- decisive outputs are bounded labels or values;
- low confidence fails closed;
- validators independently re-run decisive semantic judgments;
- normalized hostname checks prevent trivial duplicate-domain quorum construction;
- contradictory evidence is preserved rather than hidden by simple majority;
- free-form text does not directly control funds;
- live webpage byte equality is not assumed;
- caller-frozen baselines can be SHA-256 bound exactly;
- economic settlement happens only after deterministic state checks;
- terminal states block double settlement.

## Verification

Canonical CI:

https://github.com/maho0638/verdictmesh-genlayer/actions/runs/36484767096

Result:

- 98 / 98 direct tests PASS
- 12 / 12 GenVM lints PASS

Canonical full Studionet proof:

https://github.com/maho0638/verdictmesh-genlayer/actions/runs/36484767134

Live commit:

`042ce06aa40722bb31130a5baaa5a2d0014b4cc2`

Result:

- flagship bonded lifecycle: 1 / 1 PASS
- expanded evidence catalog: 11 / 11 PASS
- total: 12 / 12 contracts live

The workflow pins SHA-256 hashes of every contract source before live execution.

## Flagship native-GEN lifecycle

The live VerdictMesh dispute demonstrates:

1. claimant opens with native GEN;
2. respondent matches the stake exactly;
3. three independent sources resolve SUPPORTED, 3-0;
4. settlement remains locked for one hour;
5. respondent supplies fresh fourth-domain counterevidence;
6. the full four-source panel is re-evaluated;
7. result becomes CONFLICTED, 3-1;
8. deterministic split settlement returns both principals;
9. final state is SPLIT_REFUNDED.

Live flagship contract:

https://explorer-studio.genlayer.com/address/0xe3f1E70344F58C3280542dBdC6a4Bfc533C5e6B0

## Expanded live mechanisms

The same canonical run also proves:

- EvidencePanel -> SUPPORTED 3-0
- AsOfEvidencePanel -> post-cutoff evidence excluded
- ConsensusFieldExtractor -> AGREED 3-of-3
- NumericConsensusOracle -> CONSENSUS with spread 2
- ClaimDependencyGraph -> supported prerequisite unlocks supported child
- PolicyChangeAttestor -> frozen baseline remains UNCHANGED
- StatementConflictAttestor -> conflicting facts are surfaced
- PrimaryCorroborationGate -> VERIFIED
- ProvenanceChainAttestor -> PROVENANCE_CONFIRMED
- CorrectionStatusAttestor -> CURRENT
- ExpiringEvidenceAttestor -> SUPPORTED with bounded valid-until time

Addresses, transactions, source hashes, decision hashes, and observed outputs:

`docs/PROOF_MANIFEST.json`

## Reproduction

```bash
python -m pip install -r requirements.txt
pytest tests/direct -v
for f in contracts/*.py; do genvm-lint check "$f"; done
gltest tests/integration/test_verdictmesh_studionet.py -v -s --network studionet
gltest tests/integration/test_verdictmesh_catalog_studionet.py -v -s --network studionet
```

## Explicit limitations

VerdictMesh does not prove that public sources are truthful, organizationally independent, immutable, or free from coordinated misinformation.

Hostname diversity is a resistance mechanism against trivial duplicate-source voting, not proof of ownership independence.

Validators fetch live webpages independently, so consensus is over bounded semantic judgments rather than byte-identical page snapshots.
