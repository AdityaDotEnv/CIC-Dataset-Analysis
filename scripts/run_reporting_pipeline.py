from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def run(command: list[str]) -> int:
    return subprocess.run(command, cwd=REPO_ROOT, check=False).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate result artifacts and build dashboard/reporting outputs.")
    parser.add_argument("--validate-processed", action="store_true", help="Also validate data/processed/cicids2017. Requires hydrated Git-LFS artifacts.")
    parser.add_argument("--core-only", action="store_true", help="Exclude supporting tables from the BI staging bundle.")
    args = parser.parse_args()

    commands = []
    if args.validate_processed:
        commands.append([sys.executable, str(REPO_ROOT / "scripts" / "validate_processed_dataset.py")])
    commands.extend([
        [sys.executable, str(REPO_ROOT / "scripts" / "validate_results.py")],
        [sys.executable, str(REPO_ROOT / "scripts" / "run_dashboard_export.py")] + (["--core-only"] if args.core_only else []),
        [sys.executable, str(REPO_ROOT / "scripts" / "build_dashboard.py")],
    ])

    for command in commands:
        code = run(command)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
