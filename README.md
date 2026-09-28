# VerdictMesh — Evidence Consensus Primitives for GenLayer

VerdictMesh is a catalog of 12 standalone GenLayer Intelligent Contracts for conflict-aware public-web evidence, provenance, temporal validity, structured extraction, dependency gating, and native-GEN bonded disputes.

Sightline focuses on visual evidence. VerdictMesh is deliberately different: its security boundary is **multi-source public-web evidence and disagreement semantics**.

## Catalog

1. `EvidencePanel` — three independent sources with deterministic conflict preservation.
2. `AsOfEvidencePanel` — only pre-cutoff dated evidence may count.
3. `ConsensusFieldExtractor` — three-source semantic agreement on one named field.
4. `NumericConsensusOracle` — numeric extraction plus deterministic spread tolerance.
5. `ClaimDependencyGraph` — downstream claims remain locked until prerequisites are supported.
6. `PolicyChangeAttestor` — frozen baseline SHA-256 plus current semantic change detection.
7. `StatementConflictAttestor` — detects materially conflicting factual statements between sources.
8. `PrimaryCorroborationGate` — primary evidence must be independently corroborated.
9. `ProvenanceChainAttestor` — verifies attribution to an origin plus origin support.
10. `CorrectionStatusAttestor` — CURRENT / CORRECTED / RETRACTED status.
11. `ExpiringEvidenceAttestor` — TTL-bounded consensus that must be refreshed.
12. `VerdictMesh` — equal native-GEN bonds, conflict-aware adjudication, challenge, re-resolution, and terminal settlement.

See `CONTRACTS.md` for the invariant and failure semantics of each primitive.

## Shared safety design

- webpage text is untrusted evidence, never instructions;
- sources are judged independently where source-level attribution matters;
- validators independently reproduce decisive semantic fields;
- low confidence fails closed;
- duplicate-domain quorum construction is blocked by normalized hostname rules;
- material contradiction is preserved rather than averaged away;
- free-form explanatory text is audit-only;
- deterministic rules gate storage and economic consequences;
- live webpage bytes are not assumed identical across validators.

## Current verification

VerdictMesh is fully live-verified on Studionet:

- **98 / 98 direct tests PASS**
- **12 / 12 GenVM lints PASS**
- **12 / 12 contracts deployed and exercised on Studionet**
- canonical CI: https://github.com/maho0638/verdictmesh-genlayer/actions/runs/36484767096
- canonical Studionet proof: https://github.com/maho0638/verdictmesh-genlayer/actions/runs/36484767134
- canonical live commit: `042ce06aa40722bb31130a5baaa5a2d0014b4cc2`

The live workflow pins SHA-256 for all 12 contract sources before execution.

The flagship bonded lifecycle used real native GEN:

`open -> equal respondent bond -> 3-source SUPPORTED 3-0 -> settlement locked -> fresh fourth-domain challenge -> 4-source CONFLICTED 3-1 -> SPLIT_REFUNDED`

Every live address, transaction hash, source hash, and observed result is pinned in `docs/PROOF_MANIFEST.json`.

## Reviewer path

1. `CONTRACTS.md`
2. `docs/ARCHITECTURE.md`
3. `docs/THREAT_MODEL.md`
4. `DECISIONS.md`
5. `docs/PROOF_MANIFEST.json`
6. `docs/REVIEWER_GUIDE.md`

VerdictMesh does not claim that a webpage is truthful or that hostname diversity proves organizational independence. Its goal is narrower and auditable: expose disagreement, provenance, timing, and confidence explicitly so uncertain evidence fails safely rather than being forced into a winner.
