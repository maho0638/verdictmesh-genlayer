# VerdictMesh Architecture

VerdictMesh is a single deep Intelligent Contract primitive for symmetric, evidence-backed factual disputes.

## State machine

`OPEN -> ACTIVE -> RESOLVED -> CHALLENGED -> RESOLVED -> terminal settlement`

Terminal states:

- `CLAIMANT_PAID`
- `RESPONDENT_PAID`
- `SPLIT_REFUNDED`
- `CANCELLED`

## Evidence roles

A case begins with:

- claimant evidence URL;
- a precommitted anchor URL;
- a designated respondent;
- a native-GEN claimant stake.

The respondent sees the claim, anchor, and claimant source before accepting. Acceptance requires:

- an equal GEN stake;
- a respondent evidence URL;
- a third independent hostname.

This creates a symmetric bonded case with three distinct web domains before any semantic resolution.

## Per-source consensus

VerdictMesh deliberately does not concatenate all sources into one prompt.

For each source independently:

1. render the HTTPS page inside a nondeterministic block;
2. ask for exactly one bounded vote: `SUPPORT`, `CONTRADICT`, or `INSUFFICIENT`;
3. normalize malformed labels;
4. fail confidence below 65 to `INSUFFICIENT`;
5. have validators independently rerun every decisive source judgment;
6. require the same normalized vote and confidence within a fixed tolerance.

Only accepted structured votes leave the nondeterministic boundary.

## Deterministic conflict circuit breaker

Initial three-source resolution:

- any mix of SUPPORT and CONTRADICT -> `CONFLICTED`;
- at least 2 SUPPORT and 0 CONTRADICT -> `SUPPORTED`;
- at least 2 CONTRADICT and 0 SUPPORT -> `CONTRADICTED`;
- otherwise -> `INSUFFICIENT`.

This is intentionally stricter than ordinary majority voting. A material counter-source prevents a winner payout.

## Guaranteed challenge window

Every initial resolution opens a one-hour challenge window.

During that window:

- no winner payout;
- no split refund;
- either party may provide one fresh HTTPS source;
- the challenge hostname must differ from all three initial hostnames.

The challenged case is then fully re-evaluated across all four sources.

Four-source resolution requires at least three aligned decisive votes with no opposite decisive vote. Any SUPPORT/CONTRADICT mixture remains `CONFLICTED`.

After the fresh re-resolution, settlement may proceed immediately.

## Economic settlement

Both parties post equal native-GEN stakes.

- `SUPPORTED` -> claimant receives the full pot.
- `CONTRADICTED` -> respondent receives the full pot.
- `CONFLICTED` or `INSUFFICIENT` -> each party receives its original stake back.

An unaccepted case can be cancelled after 24 hours and returns the claimant stake.

Settlement is terminal and cannot be repeated.

## Audit receipt

Each resolution stores:

- source URLs;
- normalized source votes;
- confidence values;
- vote counts;
- resolution round;
- challenge metadata;
- policy version;
- a deterministic SHA-256 decision hash over the frozen case inputs and normalized verdict.

The decision hash binds the on-chain receipt to the adjudication inputs and accepted vote structure. It is not presented as a hash of live webpage bytes, because independently rendered webpages may legitimately differ across validators.
