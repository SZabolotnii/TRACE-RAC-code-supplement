# Synthetic release-workflow policy v1 — English translation

> Translation of `../POLICY.md`. The Ukrainian original is the frozen,
> SHA-256-hashed version (`implementation_freeze.json`) that the
> implementations and both LLM judges used. If the two differ, the original
> governs.

Domain: agentic coding — permission to merge into a protected branch. This is a local research policy, not a full emulation of GitHub. Source of the domain requirements: [GitHub, About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches), checked on 23.09.2026: required status checks, required reviews, dismissal of stale approvals, approval by someone other than the last pusher. Everything else (the full version tuple, queue, TTL, retry) consists of explicitly stated research extensions, not GitHub requirements.

## State and records

Each episode is independent. Initial state: commit=c1, base=b1, policy=p1, component=m1, input=i1, pusher=author; scope=true, eligible=true; budget=1; queue=0, capacity=1; review_required=true; review_ttl=10; deadline=20; failure=false. There is no CI result, review request, approval, or rejection. t starts at 0. Time is measured in notional simulated ticks, not seconds.

Episode JSON: `id`, `family`, `split`, `description`, `events`. Events have `t` (non-negative, non-decreasing), `op`, and the fields listed below. Evidence identity is the six fields commit/base/policy/component/input/pusher. Any change to at least one of these fields invalidates CI, the request, the approval, and the rejection, even if the field later returns to its previous value (ABA protection).

- `change`: one or more of the six fields. Only an actual change invalidates evidence.
- `settings`: scope, eligible, review_required, queue, capacity, deadline, review_ttl; fields not listed are unchanged. These fields do not themselves invalidate records; whether the constraints hold is checked at attempt time.
- `ci`: `status` = pass/fail/unknown; the result for the current state. The latest record replaces the previous one. This is a shared idealised detector, not a measurement of real testing.
- `failure`: `active` = true/false; false means that the failure has been recorded as resolved. The budget is not replenished.
- `review`: `outcome` = approve/reject/revoke, `reviewer` = author or maintainer, `qualified` = true/false. Approve/reject is accepted only if there is a current request, qualified=true, reviewer != pusher, t <= deadline, and t-request_time <= review_ttl. Revoke always cancels the approval and the pending request regardless of the other fields (fail closed). An event without valid preconditions is ignored and recorded as invalid_review.
- `attempt`: evaluate permission and record the decision. No real action is performed. A review request / simulated release / retry is written to the log as described below. An episode may contain several attempts; each is evaluated.

## Decision at an attempt: order of reasons

1. scope=false → block/stop; eligible=false → block/switch. t > deadline → block/stop (expiry of the whole action, not only of the review).
2. CI != pass → block/verify (fail and unknown never count as pass).
3. failure=true → block/retry if budget>0, consuming 1 budget. Otherwise block/stop. A retry does not by itself resolve the failure.
4. A valid reject → block/stop (a new request under the same version does not cancel the reject).
5. review_required=false → allow/act. Otherwise a valid approval (t-approval_time <= review_ttl) → allow/act. A reviewer leaving the queue does not cancel a completed approval.
6. Without a valid approval, review is required. If capacity<=queue → review/defer (zero capacity also means unavailability); in this branch NO new request is created. Otherwise review/escalate: if there is no current, unexpired request, record a new review_request at t; if there is one, do not duplicate it. A request expires when t-request_time > review_ttl. Queue is a given external load, not the number of requests in this episode.

Every allow records a simulated release. A validly accepted approval/reject completes the pending request; an approval stores the time of acceptance. A reject remains in force until a change or a revoke. When an approval is absent or expired, the old approval does not substitute for a new request. All rules are identical for RAC and the stateful baseline.

Labels: allow/review/block; if the given facts do not permit an assessment — insufficient_information. A judge labels all attempts and explains each; the judge must not see the implementations, the author's expectations, or other judges' answers. This is an assessment of the rules of a synthetic coding workflow, not human expertise and not a check of detector truthfulness.
