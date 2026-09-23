# SPDX-FileCopyrightText: 2026 Serhii Zabolotnii
# SPDX-License-Identifier: Apache-2.0
"""Structural integrity only; does not execute either policy or infer labels."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FIELDS = {
    "change": {"commit", "base", "policy", "component", "input", "pusher"},
    "settings": {"scope", "eligible", "review_required", "queue", "capacity", "deadline", "review_ttl"},
    "ci": {"status"}, "failure": {"active"},
    "review": {"outcome", "reviewer", "qualified"}, "attempt": set(),
}


def main():
    cases = json.loads((ROOT / "test.json").read_text())
    packet = json.loads((ROOT / "judge_packet.json").read_text())
    assert len(cases) == 24
    assert {c["id"] for c in cases} == {f"H{i:02}" for i in range(1, 25)}
    assert packet == [{k: c[k] for k in ("id", "description", "events")} for c in cases]
    attempts = 0
    for case in cases:
        assert set(case) == {"id", "family", "split", "description", "events"}
        assert case["split"] == "test"
        previous = 0
        n = 0
        for e in case["events"]:
            assert isinstance(e["t"], int) and e["t"] >= previous
            previous = e["t"]
            assert set(e) <= FIELDS[e["op"]] | {"op", "t"}
            if e["op"] in ("ci", "failure", "review"):
                assert FIELDS[e["op"]] <= set(e)
            if e["op"] == "ci":
                assert e["status"] in ("pass", "fail", "unknown")
            if e["op"] == "review":
                assert e["outcome"] in ("approve", "reject", "revoke")
                assert e["reviewer"] in ("author", "maintainer")
                assert type(e["qualified"]) is bool
            if e["op"] == "failure":
                assert type(e["active"]) is bool
            if e["op"] == "change":
                for key in FIELDS["change"] & set(e):
                    assert isinstance(e[key], str) and e[key]
                if "pusher" in e:
                    assert e["pusher"] in ("author", "maintainer")
            if e["op"] == "settings":
                for key in {"scope", "eligible", "review_required"} & set(e):
                    assert type(e[key]) is bool
                for key in {"queue", "capacity", "deadline", "review_ttl"} & set(e):
                    assert type(e[key]) is int and e[key] >= 0
            n += e["op"] == "attempt"
        assert 1 <= n <= 4
        attempts += n
    print(f"Structural checks: {len(cases)} episodes, {attempts} attempts; packet exact")


if __name__ == "__main__":
    main()
