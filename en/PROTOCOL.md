# LLM held-out protocol v1 — 23.09.2026 — English translation

> Translation of `../PROTOCOL.md`. The Ukrainian original is the frozen,
> SHA-256-hashed version (`implementation_freeze.json`). If the two differ,
> the original governs.

Aim: compare a new research implementation of RAC with a full stateful workflow engine on new synthetic coding traces, using two blinded LLM labellings. This is not a rerun of the private TRACE-AI-gate. A null difference is acceptable; superiority is not a condition of success. LLMs are not to be called human domain experts.

Sequence: (1) fix POLICY and the protocol; (2) create separate RAC and baseline implementations and development traces; (3) check them on development and record SHA-256 hashes of the implementations and the policy; (4) only then does a separate agent create 24 test episodes without reading the implementations or development traces; (5) two new judges independently read only POLICY and the anonymised test traces, without family/split/expected; (6) freeze the labels before executing the test; (7) run both arms; (8) report all disagreements, with no changes made for the test. If a change is needed after the test, report the original result and call the repeat exploratory.

The baseline has an independent reducer/state, the full six-field version tuple with ABA invalidation, the review lifecycle, capacity, TTL/deadline, a retry budget, and all the same detector outputs. Importing RAC or implementing the baseline as an ablation of it is prohibited. A shared runner may only feed identical events and collect outputs.

Train/dev covers simple single functions. Test contains new combinations and orderings of events, not copies of the 18 earlier traces or of dev with renamed fields. This is a prospective holdout from the implementers, not a random sample from a real population; the primitive rules are shared deliberately. The test generator runs after the implementations are frozen. One coding domain, 24 episodes, all attempts analysed; no confidence intervals or p-values for this synthetic set.

Two separate LLM judges without history, forbidden to read the implementations or the other judge's labels. The model family may coincide: this is session independence, not independence of errors. Exact snapshots and sampling parameters are unavailable. Store the requests, labels, and rationales. The primary oracle is only the consensus allow/review/block of both judges; disagreements and insufficient_information are stored, excluded from the primary denominator, and shown as a sensitivity analysis against each judge. The consensus must not be fitted to the systems' results by voting.

Primary outcomes: allow where the consensus is block/review (policy-violating simulated release); non-allow where the consensus is allow (false refusal); full agreement on the three labels. Separately: review_request events, valid completed reviews, invalid_review, simulated releases, retries, simulated request-to-completion delays, queue at each attempt, defer/stop. Show the denominators. These outcomes are observed only inside the simulator; real harm or delay is not measured.

Score-only is not an arm of this new experiment: thresholds are not tuned, so there is no train/test leakage through tuning. This completes the LLM-only version of the experiment that can be carried out here, but it does not replace the original requirement of two humans or deployment external validity. The change in evidential standard must be recorded explicitly in the readiness notes.
