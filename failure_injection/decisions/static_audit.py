# SPDX-FileCopyrightText: 2026 Serhii Zabolotnii
# SPDX-License-Identifier: Apache-2.0
"""Sanitize and audit the published single-step decision logs (arXiv v2).

Three logs, one per run reported in Section 7:
  decisions_mechanisms_first_run.jsonl  174 mechanisms, before the guard change
  decisions_mechanisms.jsonl            174 mechanisms, after the guard change
  decisions_independent.jsonl           124 cases written blind by another model

Each log holds four rows per case: rac, protocol, and the score arm at the
published configuration (tau=0.60) and at its best point (tau=0.05). The logs
support recalculation of the paper's tables; the private gate source and its
fixtures are not part of this package.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED = {"acted", "arm", "case_class", "case_id", "corpus", "detail", "positive"}
REVIEW_CLASSES = {"test-moved-in-scope", "test-skip-marker", "ext-supervision"}
LOGS = (
    "decisions_mechanisms_first_run.jsonl",
    "decisions_mechanisms.jsonl",
    "decisions_independent.jsonl",
)


def sanitized_rows(source: Path) -> list[dict]:
    rows = [json.loads(line) for line in source.read_text().splitlines() if line]
    clean = [{key: row[key] for key in sorted(ALLOWED) if key in row} for row in rows]
    for row in clean:
        if set(row) != ALLOWED:
            raise ValueError(f"missing public fields in {row.get('case_id')}")
        if any(marker in row["detail"] for marker in ("/Users/", "sk_test_", "Bearer ")):
            raise ValueError("private path or token-shaped text in decision log")
    return clean


def audit(rows: list[dict]) -> dict:
    cases = {r["case_id"] for r in rows}
    result = {"cases": len(cases)}
    for name, subset in (
        ("rac", [r for r in rows if r["arm"] == "rac"]),
        ("protocol", [r for r in rows if r["arm"] == "protocol"]),
        ("score_vendor", [r for r in rows if r["arm"] == "score" and "tau=0.60" in r["detail"]]),
        ("score_best", [r for r in rows if r["arm"] == "score" and "tau=0.05" in r["detail"]]),
    ):
        if {r["case_id"] for r in subset} != cases or len(subset) != len(cases):
            raise ValueError(f"incomplete paired cases in {name}")
        positives = [r for r in subset if r["positive"]]
        controls = [r for r in subset if not r["positive"]]
        review = [r for r in positives if r["case_class"] in REVIEW_CLASSES]
        blocked = [r for r in positives if r["case_class"] not in REVIEW_CLASSES]
        result[name] = {
            "unauthorized_action": [sum(r["acted"] for r in blocked), len(blocked)],
            "admitted_injections": [sum(r["acted"] for r in positives), len(positives)],
            "auto_admitted_review": [sum(r["acted"] for r in review), len(review)],
            "false_refusal": [sum(not r["acted"] for r in controls), len(controls)],
        }
    rac = {r["case_id"]: r["acted"] for r in rows if r["arm"] == "rac"}
    best = {r["case_id"]: r["acted"] for r in rows if r["arm"] == "score" and "tau=0.05" in r["detail"]}
    result["best_score_matches_rac_on_every_case"] = rac == best
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", type=Path, default=Path(__file__).parent)
    args = parser.parse_args()
    print(json.dumps({log: audit(sanitized_rows(args.dir / log)) for log in LOGS},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
