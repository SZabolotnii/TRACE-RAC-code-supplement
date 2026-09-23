# SPDX-FileCopyrightText: 2026 Serhii Zabolotnii
# SPDX-License-Identifier: Apache-2.0
"""Package the synthetic artifact and verify replay in a clean directory."""
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent


def main():
    archive = ROOT.parent / "llm_holdout_TAAS_2026-09-23.zip"
    files = sorted(p for p in ROOT.iterdir() if p.is_file() and (p.suffix in (".py", ".json", ".md") or p.name == "LICENSE"))
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        for path in files:
            bundle.write(path, f"llm_holdout/{path.name}")
    with tempfile.TemporaryDirectory(prefix="trace-llm-replay-") as tmp:
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(tmp)
        clean = Path(tmp) / "llm_holdout"
        for command in (("check_data.py",), ("development_check.py",), ("evaluate.py", "evaluate")):
            result = subprocess.run([sys.executable, *command], cwd=clean,
                                    text=True, capture_output=True)
            if result.returncode:
                raise RuntimeError(result.stdout + result.stderr)
        for name in ("results.json", "execution_log.json"):
            assert (ROOT / name).read_bytes() == (clean / name).read_bytes(), name
    print(f"Packaged {len(files)} files; clean replay byte-identical")
    print(archive.name)
    print("sha256", hashlib.sha256(archive.read_bytes()).hexdigest())


if __name__ == "__main__":
    main()
