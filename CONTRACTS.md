# VerdictMesh contract catalog

VerdictMesh is one Intelligent Contracts contribution composed of 12 evidence-consensus primitives. They share a bounded semantic-consensus safety model but expose different APIs, state machines, and deterministic invariants.

## 1. EvidencePanel
Three independent HTTPS sources are classified separately as SUPPORT / CONTRADICT / INSUFFICIENT. Any material SUPPORT/CONTRADICT mixture becomes CONFLICTED; aligned 2-of-3 evidence can resolve decisively.

## 2. AsOfEvidencePanel
A time-bounded panel. Only evidence visibly dated on or before a frozen YYYY-MM-DD cutoff may count toward the final verdict. Post-cutoff and unknown-date evidence is excluded deterministically.

## 3. ConsensusFieldExtractor
Extracts one bounded named field independently from three sources and requires semantic value agreement. Competing values produce conflict rather than arbitrary selection.

## 4. NumericConsensusOracle
Extracts one integer metric from three independent sources and applies a deterministic maximum-spread tolerance. Values outside the tolerance resolve DIVERGENT instead of averaging away disagreement.

## 5. ClaimDependencyGraph
Builds evidence-backed claim dependencies. A child claim cannot resolve until its prerequisite claim is supported, preventing downstream state from treating an unresolved premise as true.

## 6. PolicyChangeAttestor
Compares a caller-frozen baseline statement with the current semantics of one public page. The baseline is SHA-256 bound and the output is UNCHANGED / CHANGED / UNDETERMINED.

## 7. StatementConflictAttestor
Compares two independent sources about one topic and records whether their factual statements are CONSISTENT, CONFLICTING, UNRELATED, or UNDETERMINED.

## 8. PrimaryCorroborationGate
Requires a designated primary source to support the claim and independent corroborators to agree. A contradictory corroborator forces conflict instead of letting primary-source authority override disagreement.

## 9. ProvenanceChainAttestor
Checks whether a primary source actually attributes a claim to a named origin and whether that origin independently supports the claim. This separates attribution provenance from mere factual agreement.

## 10. CorrectionStatusAttestor
Determines whether a frozen public statement is CURRENT, CORRECTED, RETRACTED, or UNDETERMINED based on the current source.

## 11. ExpiringEvidenceAttestor
Creates a two-source consensus attestation with a bounded TTL. The attestation becomes stale and must be refreshed after expiry, producing a new resolution round.

## 12. VerdictMesh
A symmetric native-GEN bonded dispute state machine. Claimant and respondent post equal stakes, a three-source panel resolves the claim, settlement is locked for one hour, either party can add one fresh fourth-domain challenge source, and the full panel is re-resolved before winner payout or split refund.

## Shared safety boundary

- public webpage text is treated as untrusted evidence, not instructions;
- decisive model outputs are reduced to bounded labels/values;
- validators independently rerun decisive semantic judgments;
- low confidence fails closed;
- independent-domain checks block trivial duplicate-source voting;
- material contradiction is preserved rather than averaged away;
- free-form explanatory text is audit-only and does not directly control settlement;
- live webpage bytes are not assumed identical across validators;
- economic transfers occur only after deterministic state checks.
