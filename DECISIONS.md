# VerdictMesh Engineering Decisions

## Sources are judged separately

A monolithic prompt over three pages would make it difficult to know which source drove a result and would let one adversarial page influence interpretation of the others.

VerdictMesh instead performs one bounded semantic classification per source and aggregates only after GenLayer consensus accepts those classifications.

## Conflict beats simple majority

The contract is designed for bonded disputes, not casual summarization. A 2-to-1 majority is not automatically economically safe when the minority source directly contradicts the claim.

Therefore a mixed SUPPORT/CONTRADICT panel becomes `CONFLICTED`. Decisive payout requires aligned evidence with no opposite decisive vote.

## Low confidence does not count as a vote

A model output below 65 confidence becomes `INSUFFICIENT` even if the model labels it SUPPORT or CONTRADICT.

This prevents weak semantic guesses from satisfying the deterministic quorum.

## Domain diversity is normalized before comparison

`www.example.com` and `example.com` are treated as the same hostname. Trailing dots normalize away. URLs containing userinfo or backslashes are rejected.

The purpose is to prevent trivial duplicate-domain quorum construction.

## Live page bytes are not hashed as evidence identity

Unlike caller-supplied raw bytes, independent validators can receive different live webpage bytes because pages change, personalize, or render differently.

VerdictMesh therefore does not claim exact webpage-byte identity. Validators independently reproduce the semantic judgment, while the stored decision hash binds immutable case inputs and normalized accepted votes.

## The challenge must change the evidence set

The challenge path requires a fourth fresh hostname and then re-runs the whole panel. It is not a note-only appeal.

This gives the one-hour challenge window an actual consensus and economic effect.

## Neutral outcomes return principal

`CONFLICTED` and `INSUFFICIENT` do not transfer the other party's stake. Both original stakes are returned.

This keeps uncertain consensus from becoming a forced economic winner.

## No full application wrapper

VerdictMesh is intentionally submitted as an Intelligent Contract primitive rather than a Project. The repository focuses on consensus logic, state transitions, tests, live proof, and reviewer reproducibility.
