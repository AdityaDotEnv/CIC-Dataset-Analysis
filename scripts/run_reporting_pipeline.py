from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Validate completed results and build the dashboard/reporting bundle."
    )
    p.add_argument("--results-root", type=Path, default=REPO_ROOT / "results")
    p.add_argument(
        "--data-dir",
        type=Path,
        default=REPO_ROOT / "data" / "processed" / "cicids2017",
        help="Canonical processed CIC-IDS2017 directory (only checked when --validate-processed is used).",
    )
    p.add_argument("--validate-processed", action="store_true",
                   help="Also validate train/validation/test parquet artifacts.")
    p.add_argument("--skip-figures", action="store_true")
    p.add_argument("--core-only", action="store_true")
    return p.parse_args()


def _run(script: str, *extra: str) -> int:
    command = [sys.executable, str(REPO_ROOT / "scripts" / script), *extra]
    return subprocess.run(command, cwd=REPO_ROOT, check=False).returncode


def main() -> int:
    args = parse_args()

    # Reporting is based on completed result artifacts. It must not require the
    # large processed dataset to be present, hydrated from Git LFS, or readable.
    result_rc = _run("validate_results.py", "--results-root", str(args.results_root))
    if result_rc:
        return result_rc

    if args.validate_processed:
        processed_rc = _run(
            "validate_processed_dataset.py",
            "--data-dir", str(args.data_dir),
        )
        if processed_rc:
            print(
                "\nWARNING: processed-dataset validation did not pass. "
                "The completed-result/dashboard stage is still valid and will continue."
            )

    export_args = [
        "--results-root", str(args.results_root),
        "--output-dir", str(args.results_root / "reporting" / "dashboard_data"),
        "--figures-dir", str(args.results_root / "reporting" / "figures"),
    ]
    if args.core_only:
        export_args.append("--core-only")
    if args.skip_figures:
        export_args.append("--no-figures")

    return _run("run_dashboard_export.py", *export_args)


if __name__ == "__main__":
    raise SystemExit(main())
