from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.dashboard import build_dashboard


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the interactive HTML dashboard from final analysis artifacts.")
    parser.add_argument("--results-root", type=Path, default=REPO_ROOT / "results")
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "results" / "reporting" / "CIC_Dataset_Analysis_Dashboard.html")
    args = parser.parse_args()
    path = build_dashboard(args.results_root, args.output)
    print(f"Dashboard generated: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
