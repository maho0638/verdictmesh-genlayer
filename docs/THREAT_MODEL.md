# VerdictMesh Threat Model

VerdictMesh treats both web content and AI interpretation as untrusted inputs. Economic state changes occur only after GenLayer consensus accepts bounded per-source judgments and deterministic settlement rules are satisfied.

## Threats and controls

| Threat | Control |
| --- | --- |
| One source dominates a combined prompt | Every source is rendered and classified independently. |
| Prompt injection in a webpage | Prompts explicitly treat page text as evidence only and forbid following page instructions. |
| Hallucinated certainty | Confidence below 65 is deterministically converted to INSUFFICIENT. |
| Duplicate-domain sybil evidence | Initial evidence requires three normalized independent hostnames; challenge requires a fourth fresh hostname. |
| Majority hides material counterevidence | Any decisive SUPPORT/CONTRADICT mixture triggers CONFLICTED instead of winner-takes-all majority. |
| Leader invents a decisive vote | Validators independently rerun every source judgment and compare normalized verdicts plus bounded confidence tolerance. |
| One party posts no economic risk | Respondent must match the claimant's native-GEN stake exactly before activation. |
| Winner settles before counterevidence can be submitted | Initial resolution has a guaranteed one-hour challenge window with settlement lock. |
| Reusing an existing source as a challenge | Challenge hostname must be fresh relative to all initial sources. |
| Challenge exists only as metadata | Challenge forces a new four-source consensus evaluation before settlement. |
| Ambiguous evidence causes fund loss | CONFLICTED and INSUFFICIENT return each party's original stake. |
| Respondent never accepts | Claimant can cancel after a 24-hour acceptance deadline. |
| Double settlement | Terminal settled state blocks every later payout/refund path. |
| URL userinfo/backslash/trailing-dot tricks | Hostnames are normalized; userinfo and backslash forms are rejected; www and trailing dots normalize before diversity checks. |
| Unbounded model/state data | Claim IDs, claims, enum outputs, confidence values, and notes are bounded/normalized. |
| Nondeterministic side effects | Web/LLM work stays inside nondeterministic blocks; storage and GEN transfers occur afterward. |

## Explicit limitations

VerdictMesh does not prove that a web source is truthful, authoritative, independent in ownership, immutable, or free from coordinated misinformation.

Hostname diversity is a resistance mechanism against trivial duplicate-source voting, not a proof of organizational independence.

The contract does not freeze webpage bytes. Validators fetch live sources independently, so content can change between requests. Consensus is therefore over bounded semantic source judgments, not byte-identical page snapshots.

The decision hash commits to case inputs and accepted normalized votes; it is not a cryptographic commitment to the historical webpage content.

VerdictMesh is best suited to disputes where parties can precommit public evidence and where conflict/insufficiency should fail safely rather than force a winner.
