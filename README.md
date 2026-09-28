# VerdictMesh — Conflict-Aware Bonded Disputes for GenLayer

VerdictMesh is a reusable GenLayer Intelligent Contract for adjudicating contested factual claims across independent public web sources with symmetric native-GEN bonds.

The contract deliberately avoids a single opaque "AI decides who wins" prompt. Each source is rendered and classified independently, validators independently reproduce every decisive source judgment, and only then does deterministic logic apply confidence floors, domain diversity, conflict detection, challenge timing, and settlement.

## Core state machine

`OPEN -> ACTIVE -> RESOLVED -> CHALLENGED -> RESOLVED -> terminal settlement`

Terminal states:

- `CLAIMANT_PAID`
- `RESPONDENT_PAID`
- `SPLIT_REFUNDED`
- `CANCELLED`

## Consensus design

Three distinct HTTPS domains form the initial panel:

- claimant evidence;
- respondent evidence;
- a precommitted anchor source.

Each source receives one bounded vote:

- `SUPPORT`
- `CONTRADICT`
- `INSUFFICIENT`

Confidence below 65 fails closed to `INSUFFICIENT`.

Validator logic independently re-runs all decisive source judgments. Accepted votes then enter deterministic aggregation.

VerdictMesh uses a conflict circuit breaker rather than ordinary majority voting:

- any SUPPORT + CONTRADICT mixture -> `CONFLICTED`;
- at least two SUPPORT and no CONTRADICT -> `SUPPORTED`;
- at least two CONTRADICT and no SUPPORT -> `CONTRADICTED`;
- otherwise -> `INSUFFICIENT`.

## Economic design

The claimant opens a case with native GEN. The designated respondent must match that stake exactly before the case activates.

Initial settlement is locked for one hour.

During that guaranteed challenge window either party may introduce one fresh fourth-domain source. The entire four-source panel is then re-evaluated.

After challenge re-resolution:

- `SUPPORTED` -> claimant receives the full pot;
- `CONTRADICTED` -> respondent receives the full pot;
- `CONFLICTED` / `INSUFFICIENT` -> both parties receive their original stake.

If the respondent never accepts, the claimant can recover the opening stake after 24 hours.

## Verification

Current canonical deterministic verification:

- 28 / 28 direct tests PASS
- GenVM lint PASS
- CI: https://github.com/maho0638/verdictmesh-genlayer/actions/runs/36474368384

Canonical live Studionet proof:

- run: https://github.com/maho0638/verdictmesh-genlayer/actions/runs/36473956643
- live commit: `329e8e8cea5c74128497f980435fb4f9ad5e0508`
- contract: `0x00a9B05D97043b732Dfb296C7187A1E3F5617CD2`
- source SHA-256: `b8d6f23422e5a43a263f8f715279080419af0524618bc8f7ac85b95609b95d59`

The live lifecycle used two real GEN bonds, resolved the initial three-source panel `SUPPORTED` 3-0, accepted a fresh contradictory fourth-domain challenge, re-resolved to `CONFLICTED` 3-1, and returned both stakes with terminal status `SPLIT_REFUNDED`.

Full addresses, transactions, decision hashes, and results are pinned in `docs/PROOF_MANIFEST.json`.

## Reviewer path

1. `docs/ARCHITECTURE.md`
2. `docs/THREAT_MODEL.md`
3. `DECISIONS.md`
4. `docs/PROOF_MANIFEST.json`
5. `docs/REVIEWER_GUIDE.md`

VerdictMesh does not claim that hostname diversity proves source independence or truth. Its safety objective is narrower: make conflicting or insufficient consensus fail safely instead of forcing an economic winner.
