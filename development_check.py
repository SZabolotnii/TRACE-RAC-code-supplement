# SPDX-FileCopyrightText: 2026 Serhii Zabolotnii
# SPDX-License-Identifier: Apache-2.0
"""Development-only checks; no test corpus access."""
import json
from pathlib import Path
import rac
import baseline


def main():
    cases = json.loads(Path(__file__).with_name("dev.json").read_text())
    for case in cases:
        a, b = rac.run(case["events"]), baseline.run(case["events"])
        for name, out in (("rac", a), ("baseline", b)):
            assert [r["label"] for r in out["decisions"]] == case["labels"], (case["id"], name, out)
        assert a["decisions"] == b["decisions"], case["id"]
    print(f"Development: {len(cases)} episodes passed in both arms")


if __name__ == "__main__":
    main()
