# SPDX-FileCopyrightText: 2026 Serhii Zabolotnii
# SPDX-License-Identifier: Apache-2.0
"""Research RAC interpreter for POLICY.md; not the private production gate."""
from dataclasses import dataclass, field

IDENTITY = ("commit", "base", "policy", "component", "input", "pusher")


@dataclass
class Contract:
    identity: dict = field(default_factory=lambda: dict(zip(
        IDENTITY, ("c1", "b1", "p1", "m1", "i1", "author"))))
    epoch: int = 0
    settings: dict = field(default_factory=lambda: dict(
        scope=True, eligible=True, review_required=True, queue=0,
        capacity=1, deadline=20, review_ttl=10))
    ci: str | None = None
    failure: bool = False
    budget: int = 1
    request: tuple | None = None
    approval: tuple | None = None
    rejected: bool = False
    decisions: list = field(default_factory=list)
    log: list = field(default_factory=list)

    def emit(self, event, t, **fields):
        self.log.append(dict(event=event, t=t, **fields))

    def current(self, record, t):
        return (record is not None and record[0] == self.epoch
                and t - record[1] <= self.settings["review_ttl"])

    def decide(self, t):
        s = self.settings
        if not s["scope"]:
            return "block", "stop"
        if not s["eligible"]:
            return "block", "switch"
        if t > s["deadline"]:
            return "block", "stop"
        if self.ci != "pass":
            return "block", "verify"
        if self.failure:
            if self.budget > 0:
                self.budget -= 1
                self.emit("retry", t, remaining=self.budget)
                return "block", "retry"
            return "block", "stop"
        if self.rejected:
            return "block", "stop"
        if not s["review_required"] or self.current(self.approval, t):
            self.emit("release", t)
            return "allow", "act"
        if s["capacity"] <= s["queue"]:
            return "review", "defer"
        if not self.current(self.request, t):
            self.request = (self.epoch, t)
            self.emit("review_request", t, epoch=self.epoch)
        return "review", "escalate"

    def ingest(self, e):
        op, t = e["op"], e["t"]
        if op == "change":
            changes = {k: e[k] for k in IDENTITY if k in e}
            if any(self.identity[k] != v for k, v in changes.items()):
                self.epoch += 1
                self.ci = self.request = self.approval = None
                self.rejected = False
                self.identity.update(changes)
        elif op == "settings":
            self.settings.update({k: v for k, v in e.items() if k not in ("op", "t")})
        elif op == "ci":
            self.ci = e["status"]
        elif op == "failure":
            self.failure = e["active"]
        elif op == "review":
            if e["outcome"] == "revoke":
                self.approval = self.request = None
                self.rejected = False
            elif (self.current(self.request, t) and e["qualified"]
                  and e["reviewer"] != self.identity["pusher"]
                  and t <= self.settings["deadline"]):
                self.emit("review_complete", t, outcome=e["outcome"],
                          delay=t - self.request[1])
                self.request = None
                if e["outcome"] == "approve":
                    self.approval = (self.epoch, t)
                else:
                    self.approval = None
                    self.rejected = True
            else:
                self.emit("invalid_review", t, outcome=e["outcome"])
        elif op == "attempt":
            label, transition = self.decide(t)
            row = dict(attempt=len(self.decisions) + 1, t=t, label=label,
                       transition=transition, queue=self.settings["queue"])
            self.decisions.append(row)
            self.emit("decision", **row)
        else:
            raise ValueError(op)


def run(events):
    contract = Contract()
    previous = 0
    for event in events:
        if event["t"] < previous:
            raise ValueError("Nonmonotone time")
        previous = event["t"]
        contract.ingest(event)
    return dict(decisions=contract.decisions, log=contract.log)
