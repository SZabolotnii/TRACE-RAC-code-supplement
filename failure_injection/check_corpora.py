# SPDX-FileCopyrightText: 2026 Serhii Zabolotnii
# SPDX-License-Identifier: Apache-2.0
"""Check that the published case files agree with the published decision logs.

For each corpus, the set of case identifiers in the case file must equal the
set in every decision log of that corpus, and each case's label (injected or
control) must agree with the log. Prints PASS or FAIL per check and exits
non-zero on any failure. Python 3.10 or newer, no third-party packages.
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
PAIRS = {
    "corpora/mechanisms_174/cases.jsonl": [
        "decisions/decisions_mechanisms_first_run.jsonl",
        "decisions/decisions_mechanisms.jsonl",
    ],
    "corpora/independent_124/cases.jsonl": ["decisions/decisions_independent.jsonl"],
}


def rows(path: str) -> list[dict]:
    text = (HERE / path).read_text(encoding="utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


ok = True
for case_file, logs in PAIRS.items():
    cases = {c["case_id"]: c["required"] != "none" for c in rows(case_file)}
    for log in logs:
        decided: dict[str, bool] = {}
        for d in rows(log):
            decided.setdefault(d["case_id"], d["positive"])
        passed = set(cases) == set(decided) and all(cases[k] == decided[k] for k in cases)
        ok &= passed
        print(f"{'PASS' if passed else 'FAIL'}  {case_file} vs {log}: "
              f"{len(cases)} cases, {sum(cases.values())} injected")
raise SystemExit(0 if ok else 1)
