from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


REQUIRED_FILES = {
    "feature_columns.json",
    "label_mapping.json",
    "manifest.json",
    "imputer.joblib",
    "scaler.joblib",
    "train.parquet",
    "validation.parquet",
    "test.parquet",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate the canonical processed CIC-IDS2017 dataset produced by Notebook 14.")
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data" / "processed" / "cicids2017")
    return parser.parse_args()


def _assert(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate(root: Path) -> None:
    _assert(root.exists(), f"Processed dataset directory does not exist: {root}")
    missing_files = sorted(name for name in REQUIRED_FILES if not (root / name).exists())
    _assert(not missing_files, f"Missing required processed artifacts: {missing_files}")

    features = json.loads((root / "feature_columns.json").read_text(encoding="utf-8"))
    labels = json.loads((root / "label_mapping.json").read_text(encoding="utf-8"))
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    imputer = joblib.load(root / "imputer.joblib")
    scaler = joblib.load(root / "scaler.joblib")

    _assert(isinstance(features, list) and features, "feature_columns.json must contain a non-empty list")
    _assert(len(features) == len(set(features)), "feature_columns.json contains duplicate features")
    _assert("label" not in features, "Target leakage: 'label' appears in feature_columns.json")
    _assert(isinstance(labels, dict) and labels, "label_mapping.json must contain a non-empty mapping")

    observed_splits: dict[str, int] = {}
    expected_columns = features + ["label"]
    allowed_labels = set(labels.values())

    for split in ["train", "validation", "test"]:
        df = pd.read_parquet(root / f"{split}.parquet")
        observed_splits[split] = len(df)
        _assert(list(df.columns) == expected_columns, f"{split}: column order differs from feature_columns.json + label")
        X = df[features]
        _assert(X.isna().sum().sum() == 0, f"{split}: NaN values remain")
        _assert(np.isfinite(X.to_numpy()).all(), f"{split}: infinite values remain")
        _assert(set(df["label"].dropna().unique()).issubset(allowed_labels), f"{split}: unexpected label values")
        _assert(df["label"].notna().all(), f"{split}: missing target labels")
        print(f"{split:10s} rows={len(df):>10,} features={len(features):>3} OK")

    n_features_in_imputer = getattr(imputer, "n_features_in_", len(features))
    n_features_in_scaler = getattr(scaler, "n_features_in_", len(features))
    _assert(n_features_in_imputer == len(features), "Imputer was fit on a different number of features")
    _assert(n_features_in_scaler == len(features), "Scaler was fit on a different number of features")

    # Manifest keys varied slightly during notebook development, so validate any
    # split counts that are actually present instead of assuming one schema.
    for split, observed in observed_splits.items():
        candidates = [f"{split}_rows", f"n_{split}", split]
        for key in candidates:
            if key in manifest and isinstance(manifest[key], (int, float)):
                _assert(int(manifest[key]) == observed, f"manifest.json {key}={manifest[key]} but {split}.parquet has {observed} rows")
                break

    split_manifest = root / "split_manifest.parquet"
    if split_manifest.exists():
        sm = pd.read_parquet(split_manifest)
        _assert(not sm.empty, "split_manifest.parquet is empty")
        print(f"split_manifest rows={len(sm):>10,} OK")

    print("Processed dataset validation passed.")


def main() -> int:
    args = parse_args()
    validate(args.data_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
