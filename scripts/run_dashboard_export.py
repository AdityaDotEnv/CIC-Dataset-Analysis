from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.reporting import build_dashboard_data, generate_result_figures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Power BI/Tableau-ready CSV exports and static result figures from completed analysis artifacts."
    )
    parser.add_argument("--results-root", type=Path, default=REPO_ROOT / "results")
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "results" / "reporting" / "dashboard_data")
    parser.add_argument("--figures-dir", type=Path, default=REPO_ROOT / "results" / "reporting" / "figures")
    parser.add_argument("--core-only", action="store_true", help="Exclude unclassified/supporting CSV artifacts from the dashboard bundle.")
    parser.add_argument("--no-figures", action="store_true", help="Export dashboard CSVs only.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    records = build_dashboard_data(
        args.results_root,
        args.output_dir,
        include_supporting=not args.core_only,
    )
    exported = sum(record.status == "exported" for record in records)
    failed = sum(record.status == "error" for record in records)

    figure_count = 0
    if not args.no_figures:
        figure_count = len(generate_result_figures(args.results_root, args.figures_dir))

    print(f"Dashboard export complete: {exported} tables exported, {failed} failed, {figure_count} figures generated.")
    print(f"Dashboard data: {args.output_dir}")
    if not args.no_figures:
        print(f"Figures:        {args.figures_dir}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
