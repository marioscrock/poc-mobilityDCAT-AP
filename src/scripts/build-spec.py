#!/usr/bin/env python3
"""Build ReSpec spec to dist/index.html.

Uses respec's built-in --localhost server so data-include paths resolve
correctly.
Run from repo root: python src/scripts/build-spec.py [--verbose]
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SRC = Path("src/index.html")    # relative — required by respec --localhost
OUT = Path("dist/index.html")   # relative — required by respec --localhost
DEFAULT_TIMEOUT_MS = "30000"


def main() -> None:
    (REPO_ROOT / OUT).parent.mkdir(parents=True, exist_ok=True)

    timeout_ms = os.getenv("RESPEC_TIMEOUT_MS", DEFAULT_TIMEOUT_MS)
    runner = ["respec"] if shutil.which("respec") else ["npx", "respec"]
    cmd = [
        *runner,
        "--localhost",
        "--timeout",
        timeout_ms,
        "-s",
        str(SRC),
        "-o",
        str(OUT),
    ]
    if "--verbose" in sys.argv:
        cmd.append("--verbose")

    result = subprocess.run(cmd, cwd=REPO_ROOT, shell=(sys.platform == "win32"))
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
