# VerdictMesh — Conflict-Aware Evidence Consensus Primitives for GenLayer

VerdictMesh is a set of reusable GenLayer Intelligent Contracts for adjudicating contested web evidence without collapsing every source into one opaque LLM answer.

The core design classifies independent HTTPS sources separately, validates the decisive classifications through GenLayer's Equivalence Principle, and only then applies deterministic quorum, conflict, time-cutoff, dependency, and settlement rules.

Planned primitives:

1. `EvidencePanel` — three-domain source panel with deterministic SUPPORT / CONTRADICT / CONFLICT / INSUFFICIENT aggregation.
2. `AsOfEvidencePanel` — excludes evidence that is undated or newer than a frozen cutoff before aggregation.
3. `ClaimDependencyGraph` — resolves dependent claims only after prerequisite claims are supported.
4. `BondedVerdictEscrow` — symmetric two-party native-GEN bonds settled from a conflict-aware evidence panel with a guaranteed challenge window.

This repository is under active verification. Portal submission is blocked until direct tests, GenVM lint, live Studionet proofs, addresses, transactions, source hashes, and reviewer reproduction steps are complete.
