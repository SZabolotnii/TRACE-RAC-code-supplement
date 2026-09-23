# SPDX-License-Identifier: Apache-2.0
"""Independent stateful release-workflow implementation of POLICY.md."""

from dataclasses import dataclass, field
from typing import Any


IDENTITY_FIELDS = ("commit", "base", "policy", "component", "input", "pusher")
SETTING_FIELDS = (
    "scope", "eligible", "review_required", "queue", "capacity", "deadline",
    "review_ttl",
)


@dataclass
class Workflow:
    identity: dict[str, Any] = field(default_factory=lambda: dict(zip(
        IDENTITY_FIELDS, ("c1", "b1", "p1", "m1", "i1", "author")
    )))
    settings: dict[str, Any] = field(default_factory=lambda: {
        "scope": True, "eligible": True, "review_required": True,
        "queue": 0, "capacity": 1, "deadline": 20, "review_ttl": 10,
    })
    epoch: int = 0
    ci: tuple[int, str] | None = None
    pending: tuple[int, int] | None = None
    approval: tuple[int, int] | None = None
    rejection: int | None = None
    failure: bool = False
    budget: int = 1
    decisions: list[dict] = field(default_factory=list)
    log: list[dict] = field(default_factory=list)

    def emit(self, event: str, t: int, **details: Any) -> None:
        self.log.append({"event": event, "t": t, **details})

    def fresh(self, record: tuple[int, int] | None, t: int) -> bool:
        return (record is not None and record[0] == self.epoch
                and t - record[1] <= self.settings["review_ttl"])

    def review(self, event: dict) -> None:
        t, outcome = event["t"], event["outcome"]
        if outcome == "revoke":
            self.approval = None
            self.pending = None
            self.rejection = None
            return
        valid = (
            outcome in ("approve", "reject")
            and self.fresh(self.pending, t)
            and event.get("qualified") is True
            and event.get("reviewer") in ("author", "maintainer")
            and event["reviewer"] != self.identity["pusher"]
            and t <= self.settings["deadline"]
        )
        if not valid:
            self.emit("invalid_review", t, outcome=outcome)
            return
        request_time = self.pending[1]
        self.pending = None
        if outcome == "approve":
            self.approval = (self.epoch, t)
        else:
            self.rejection = self.epoch
            self.approval = None
        self.emit("review_complete", t, outcome=outcome, delay=t-request_time)

    def attempt(self, t: int) -> None:
        s = self.settings
        if not s["scope"]:
            label, transition = "block", "stop"
        elif not s["eligible"]:
            label, transition = "block", "switch"
        elif t > s["deadline"]:
            label, transition = "block", "stop"
        elif self.ci != (self.epoch, "pass"):
            label, transition = "block", "verify"
        elif self.failure:
            label = "block"
            transition = "retry" if self.budget > 0 else "stop"
            if transition == "retry":
                self.budget -= 1
        elif self.rejection == self.epoch:
            label, transition = "block", "stop"
        elif not s["review_required"] or self.fresh(self.approval, t):
            label, transition = "allow", "act"
        else:
            label = "review"
            transition = "defer" if s["capacity"] <= s["queue"] else "escalate"

        decision = {
            "attempt": len(self.decisions) + 1, "t": t,
            "label": label, "transition": transition, "queue": s["queue"],
        }
        self.decisions.append(decision)
        self.emit("decision", **decision)
        if label == "allow":
            self.emit("release", t)
        elif transition == "retry":
            self.emit("retry", t)
        elif transition == "escalate" and not self.fresh(self.pending, t):
            self.pending = (self.epoch, t)
            self.emit("review_request", t)

    def accept(self, event: dict) -> None:
        op = event["op"]
        if op == "change":
            changed = any(key in event and event[key] != self.identity[key]
                          for key in IDENTITY_FIELDS)
            if changed:
                self.identity.update({key: event[key] for key in IDENTITY_FIELDS
                                      if key in event})
                self.epoch += 1
                self.ci = self.pending = self.approval = None
                self.rejection = None
        elif op == "settings":
            self.settings.update({key: event[key] for key in SETTING_FIELDS
                                  if key in event})
        elif op == "ci":
            self.ci = (self.epoch, event["status"])
        elif op == "failure":
            self.failure = event["active"]
        elif op == "review":
            self.review(event)
        elif op == "attempt":
            self.attempt(event["t"])
        else:
            raise ValueError(f"Unknown workflow operation: {op!r}")


def run(events: list[dict]) -> dict:
    """Evaluate one independent episode without modifying its event records."""
    workflow = Workflow()
    for event in events:
        workflow.accept(event)
    return {"decisions": workflow.decisions, "log": workflow.log}
