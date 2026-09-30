# Result of the LLM held-out study, 23.09.2026 — English translation

> Translation of `../REPORT.md`. The Ukrainian original is the record written
> at the time of the study. If the two differ, the original governs.

**RAC and the full stateful baseline gave identical decisions on all 72 attempts in 24 new synthetic coding episodes. Both matched the consensus of two blinded LLM judges. No advantage for RAC was found.**

## What was done

Domain: permission to merge into a protected branch. Required CI/reviews, stale approvals, and independence of the reviewer from the pusher are based on the [official GitHub documentation](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches); the version tuple, TTL, capacity, deadline, and retry are defined as research extensions. The data are not real pull requests. The judges checked the consequences of this explicit policy, not its sufficiency for production safety.

After 8 development episodes, the policy, both implementations, and the evaluator were frozen with SHA-256 (`implementation_freeze.json`). Only then did a separate LLM session create 24 episodes / 179 events / 72 attempts without reading the implementations or dev (`corpus_freeze.json`). Two new `gpt-6-sol` subagents with `fork_turns=none` independently read POLICY and the packet without family names, expected labels, or the arms' decisions. Each saved 72 labels with rationales. Both files were frozen (`labels_freeze.json`) before the first test execution. The implementations were not changed after the freeze. This is a local prospective freeze, not an external preregistration.

| Role | Session | Access |
| --- | --- | --- |
| RAC and evaluator | GPT-6 coordinator | policy, dev; test only after freeze |
| Stateful baseline | `/root/stateful_baseline` | policy/protocol; not RAC, dev, or test |
| Test author | `/root/heldout_cases` | policy/protocol; not implementations/dev/labels |
| Judge A | `/root/holdout_judge_a`, gpt-6-sol | policy and anonymised packet; not arms/other labels |
| Judge B | `/root/holdout_judge_b`, gpt-6-sol | the same, in a separate context |
| Code review | `/root/holdout_method_review` | policy/code; not test/labels/results |

Access was restricted by instructions, not by a separate file-system sandbox. Exact API snapshots and sampling parameters are unavailable. All code, the corpus, and the labels were produced with LLM assistance; the paper's author still has to check them.

## Results

The judges agreed in 72/72 cases: 30 allow, 30 review, 12 block. Disagreements: 0; insufficient_information for each judge: 0, shared: 0; no attempt was excluded from the primary denominator. Sensitivity against each judge separately gives the same numbers.

| Measure | RAC | Stateful baseline |
| --- | ---: | ---: |
| Agreement with LLM consensus | 72/72 | 72/72 |
| Simulated release despite block/review | 0/42 | 0/42 |
| False refusal where allow | 0/30 | 0/30 |
| Review requests created | 28 | 28 |
| Valid completed reviews | 25 | 25 |
| Rejected invalid review events | 5 | 5 |
| Simulated releases | 30 | 30 |
| Retries consumed | 2 | 2 |
| Stop / defer | 4 / 0 | 4 / 0 |
| Mean delay of completed reviews | 1.84 ticks | 1.84 ticks |

Delays of completed reviews range from 1 to 10 simulated ticks, denominator 25. The mean given external queue per attempt is 0.375, the maximum 8. This is not a real queue of people; its dynamics are supplied by the corpus. The mean delay does not include unfinished, cancelled, or expired requests. The difference between 28 requests and 25 completions is not by itself an estimate of the outstanding queue: invalidations may occur between them.

Full log: `execution_log.json`; counts: `results.json`. No confidence intervals or p-values: attempts within an episode are dependent, and the episodes are not a random sample. The correct wording is "observed equivalence on this corpus", not proven equivalence of the programs for all inputs.

## What closing the gates means

At the author's request, an **LLM-only alternative** to two research tasks was carried out: (1) separate blinded labelling sessions for a synthetic coding domain; (2) a prospective held-out run against a full stateful baseline with identical detector inputs. These tasks are complete; demanding them again as unfinished would be incorrect.

The original readiness standard — two qualified human reviewers and independent domain ground truth — is not met by this. The substitution is a change in the level of evidence, not a way to obtain human expertise from an LLM. Agreement between two judges of the same model family does not calibrate them and does not remove shared error. The holdout is separated from the implementers in time, but not from the shared specification or from LLM generation.

## Limits and an open coverage gap

- Both arms implement the same normative policy. The study checks that the policy can be implemented and followed, not that the rule set is independently correct. The stateful baseline is not an ablation, but neither is it an external production system.
- CI outputs and reviewer responses are given as events. There are no raw patches, real CI, people, noisy detectors, or deployment consequences. No cross-domain claim should be made.
- The test contains no final defer. The queue/capacity changes present do not guarantee a check of the branch in which a new review is unavailable: some attempts already have a completed approval. Basic absence of capacity was checked only on dev. After this gap was found, the test was not extended and the implementations were not retuned.
- Unique family tags do not prove semantic independence; the test compositions use the same policy primitives. 72/72 should not be called accuracy for a real population.

Conclusion for the paper: new synthetic held-out evidence with blinded LLM labels and an honest null result can be added. The paper remains a mechanism study; neither "100% readiness" nor superiority over full stateful systems is established by these numbers.
