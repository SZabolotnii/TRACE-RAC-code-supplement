# SPDX-FileCopyrightText: 2026 Serhii Zabolotnii
# SPDX-License-Identifier: Apache-2.0
"""Freeze artifacts and evaluate all attempts without tuning on test labels."""
import argparse
import collections
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMPLEMENTATION = ("POLICY.md", "PROTOCOL.md", "rac.py", "baseline.py",
                  "dev.json", "development_check.py", "evaluate.py")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def freeze(name, files):
    if (ROOT / name).exists():
        raise ValueError("Do not overwrite a freeze manifest")
    write(name, {"recorded_at": datetime.now(timezone.utc).isoformat(),
                 "files": {p: digest(ROOT / p) for p in files}})


def verify(name):
    manifest = json.loads((ROOT / name).read_text())
    for p, expected in manifest["files"].items():
        if digest(ROOT / p) != expected:
            raise ValueError(f"Frozen file changed: {p}")


def labels(filename, expected):
    rows = json.loads((ROOT / filename).read_text())
    result = {}
    for row in rows:
        key = (row["id"], row["attempt"])
        assert key not in result, key
        assert row["label"] in ("allow", "review", "block", "insufficient_information")
        assert row["rationale"].strip()
        result[key] = row["label"]
    assert set(result) == expected, (filename, set(result) ^ expected)
    return result


def metrics(decisions, oracle):
    keys = set(oracle)
    prohibited = [k for k in keys if oracle[k] != "allow"]
    permitted = [k for k in keys if oracle[k] == "allow"]
    return dict(n=len(keys), exact=sum(decisions[k] == oracle[k] for k in keys),
                prohibited_n=len(prohibited),
                violating_releases=sum(decisions[k] == "allow" for k in prohibited),
                permitted_n=len(permitted),
                false_refusals=sum(decisions[k] != "allow" for k in permitted))


def evaluate():
    verify("implementation_freeze.json")
    verify("corpus_freeze.json")
    verify("labels_freeze.json")
    import rac
    import baseline
    cases = json.loads((ROOT / "test.json").read_text())
    dev = json.loads((ROOT / "dev.json").read_text())
    assert len(cases) == 24 and len({c["id"] for c in cases}) == 24
    assert not ({c["family"] for c in cases} & {c["family"] for c in dev})
    expected = {(c["id"], i) for c in cases
                for i in range(1, sum(e["op"] == "attempt" for e in c["events"]) + 1)}
    j1, j2 = labels("judge_a.json", expected), labels("judge_b.json", expected)
    consensus = {k: v for k, v in j1.items()
                 if v == j2[k] and v != "insufficient_information"}
    summary = dict(episodes=len(cases), attempts=len(expected), consensus_n=len(consensus),
                   judge_agreement=sum(j1[k] == j2[k] for k in expected),
                   consensus_distribution=dict(collections.Counter(consensus.values())),
                   disagreements=[dict(id=k[0], attempt=k[1], a=j1[k], b=j2[k])
                                  for k in sorted(expected) if j1[k] != j2[k]], arms={})
    raw = {}
    all_decisions = {}
    for arm, module in (("rac", rac), ("stateful_baseline", baseline)):
        raw[arm] = {}
        decisions, log, queues = {}, [], []
        for case in cases:
            out = module.run(case["events"])
            raw[arm][case["id"]] = out
            for d in out["decisions"]:
                decisions[(case["id"], d["attempt"])] = d["label"]
                queues.append(d["queue"])
            log.extend(out["log"])
        assert set(decisions) == expected
        counts = collections.Counter(e["event"] for e in log)
        delays = [e["delay"] for e in log if e["event"] == "review_complete"]
        transitions = collections.Counter(d["transition"] for out in raw[arm].values()
                                          for d in out["decisions"])
        summary["arms"][arm] = dict(
            consensus=metrics(decisions, consensus),
            judge_a=metrics(decisions, {k: v for k, v in j1.items() if v != "insufficient_information"}),
            judge_b=metrics(decisions, {k: v for k, v in j2.items() if v != "insufficient_information"}),
            events=dict(counts), transitions=dict(transitions),
            review_completion_delays_ticks=delays,
            mean_review_completion_delay_ticks=sum(delays)/len(delays) if delays else None,
            attempt_queue_values=queues,
            mean_attempt_queue=sum(queues)/len(queues) if queues else None,
        )
        all_decisions[arm] = decisions
    summary["arm_label_disagreements"] = [dict(id=k[0], attempt=k[1]) for k in sorted(expected)
        if all_decisions["rac"][k] != all_decisions["stateful_baseline"][k]]
    write("results.json", summary)
    write("execution_log.json", raw)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("freeze-implementation", "freeze-corpus", "freeze-labels", "evaluate"))
    action = parser.parse_args().action
    if action == "freeze-implementation":
        freeze("implementation_freeze.json", IMPLEMENTATION)
    elif action == "freeze-corpus":
        verify("implementation_freeze.json")
        freeze("corpus_freeze.json", ("test.json", "judge_packet.json"))
    elif action == "freeze-labels":
        verify("implementation_freeze.json")
        verify("corpus_freeze.json")
        freeze("labels_freeze.json", ("judge_a.json", "judge_b.json"))
    else:
        evaluate()
