# VerdictMesh Architecture

VerdictMesh is an evidence-consensus primitive suite for GenLayer. It contains 12 standalone Intelligent Contracts built around one common principle: nondeterministic web/LLM execution produces only bounded observations; deterministic contract logic decides whether those observations are sufficient to mutate durable or economic state.

See `CONTRACTS.md` for the per-contract catalog.

## Shared evidence pipeline

Most primitives use this pattern:

1. normalize and validate HTTPS inputs;
2. enforce independent hostnames where a multi-source invariant requires them;
3. render each source inside GenLayer nondeterministic execution;
4. classify or extract one narrow field from each source;
5. normalize malformed values and fail low confidence closed;
6. have validators independently reproduce the decisive semantic fields;
7. deterministically aggregate accepted fields;
8. store only bounded outcomes and compact audit data.

The suite intentionally avoids one monolithic "read all pages and decide" prompt where source-level disagreement would be invisible.

## Deterministic disagreement semantics

Different primitives use different deterministic rules:

- `EvidencePanel`: conflict circuit breaker over SUPPORT / CONTRADICT / INSUFFICIENT.
- `AsOfEvidencePanel`: date eligibility before vote aggregation.
- `ConsensusFieldExtractor`: semantic field-value agreement.
- `NumericConsensusOracle`: bounded numeric spread.
- `ClaimDependencyGraph`: prerequisite gating.
- `PrimaryCorroborationGate`: primary-source requirement plus independent corroboration.
- `ProvenanceChainAttestor`: attribution link plus origin support.
- `ExpiringEvidenceAttestor`: TTL and refresh rounds.

This is why the repository is a catalog of distinct state machines rather than repeated prompt wrappers.

## VerdictMesh bonded dispute state machine

The flagship economic primitive uses:

`OPEN -> ACTIVE -> RESOLVED -> CHALLENGED -> RESOLVED -> terminal settlement`

Terminal states:

- `CLAIMANT_PAID`
- `RESPONDENT_PAID`
- `SPLIT_REFUNDED`
- `CANCELLED`

The claimant opens with native GEN and precommits claimant evidence plus an anchor source. The designated respondent must match the stake exactly and provide a third independent domain.

Initial resolution classifies the three sources independently.

Deterministic aggregation:

- any SUPPORT + CONTRADICT mixture -> `CONFLICTED`;
- at least 2 SUPPORT and no CONTRADICT -> `SUPPORTED`;
- at least 2 CONTRADICT and no SUPPORT -> `CONTRADICTED`;
- otherwise -> `INSUFFICIENT`.

Every initial resolution opens a one-hour challenge window. Settlement is locked during that period. Either party can introduce exactly one fresh fourth-domain source and force a complete four-source re-resolution.

Settlement after the challenge path or after an unchallenged window:

- `SUPPORTED` -> claimant receives the full pot;
- `CONTRADICTED` -> respondent receives the full pot;
- `CONFLICTED` / `INSUFFICIENT` -> both parties receive their original stake.

## Live-page identity model

Caller-supplied frozen text such as a policy baseline can be SHA-256 bound exactly.

Live webpage bytes are different: validators fetch independently and pages can vary. VerdictMesh therefore does not pretend that a live-page byte hash is a cross-validator identity primitive. Consensus is over bounded semantic results, while stored hashes such as the flagship decision hash commit to frozen case inputs and normalized accepted outputs.

## Verification boundary

Canonical current verification demonstrates:

- 98 direct tests;
- 12 / 12 GenVM lints;
- all 12 contracts deployed and exercised on Studionet;
- a real native-GEN bonded dispute lifecycle with challenge and split refund;
- source hashes pinned before live execution.
