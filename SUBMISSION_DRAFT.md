# VerdictMesh — Conflict-Aware Evidence Consensus for GenLayer

## Status

DRAFT — DO NOT SUBMIT UNTIL LIVE PROOF IS PINNED

## Summary

VerdictMesh is a symmetric native-GEN bonded dispute primitive that adjudicates a factual claim across independent public web sources.

It does not ask one model to read all evidence and choose a winner. Each source is rendered and classified independently under GenLayer consensus, then deterministic logic applies source diversity, confidence floors, conflict detection, challenge timing, and GEN settlement.

## Distinctive mechanisms

- three independent initial HTTPS domains;
- equal claimant/respondent GEN bonds;
- one semantic vote per source;
- validator re-execution for every decisive source vote;
- low-confidence fail-closed behavior;
- material-conflict circuit breaker instead of simple 2-of-3 winner logic;
- one-hour guaranteed challenge window;
- fresh fourth-domain challenge evidence;
- complete four-source re-resolution;
- winner payout only for aligned decisive evidence;
- split principal refund for CONFLICTED / INSUFFICIENT;
- 24-hour unaccepted-case recovery;
- terminal double-settlement protection;
- deterministic decision receipt hash.

## Submission gate

Do not submit until:

- direct tests are green;
- GenVM lint is green;
- live Studionet open -> accept -> resolve -> challenge -> re-resolve -> settlement succeeds;
- contract address and every canonical transaction hash are pinned;
- contract source SHA-256 is pinned;
- proof manifest status is LIVE_VERIFIED;
- reviewer reproduction guide is final.
