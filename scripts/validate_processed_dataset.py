from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

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

SPLITS = ("train", "validation", "test")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the canonical processed CIC-IDS2017 artifacts."
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=REPO_ROOT / "data" / "processed" / "cicids2017",
    )
    parser.add_argument(
        "--skip-transformers",
        action="store_true",
        help="Do not attempt to deserialize imputer.joblib/scaler.joblib.",
    )
    return parser.parse_args()


def _is_lfs_pointer(path: Path) -> bool:
    try:
        head = path.read_bytes()[:200]
    except OSError:
        return False
    return head.startswith(b"version https://git-lfs.github.com/spec/v1")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _read_json(path: Path, description: str) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"Cannot read {description}: {path} ({exc})") from exc


def _check_artifact_file(path: Path, *, required: bool = True) -> str:
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Missing processed artifact: {path}")
        return "missing"
    if path.is_dir():
        raise ValueError(f"Expected a file but found a directory: {path}")
    if _is_lfs_pointer(path):
        return "git-lfs-pointer"
    if path.stat().st_size == 0:
        raise ValueError(f"Processed artifact is empty: {path}")
    return "ok"


def _validate_transformer(path: Path, expected_features: int, name: str) -> str:
    """Best-effort transformer validation.

    Git-LFS pointer files and malformed serialized objects are warnings rather
    than reasons to block dashboard generation. The parquet artifacts and
    notebook result tables are the canonical reporting inputs.
    """
    status = _check_artifact_file(path)
    if status == "git-lfs-pointer":
        return f"{name}: Git-LFS pointer detected; real binary is not present locally"
    try:
        import joblib

        obj = joblib.load(path)
    except Exception as exc:
        return f"{name}: could not deserialize ({type(exc).__name__}: {exc})"

    n_features = getattr(obj, "n_features_in_", None)
    if n_features is not None and int(n_features) != expected_features:
        return f"{name}: n_features_in_={n_features}, expected {expected_features}"
    return f"{name}: OK"


def validate(root: Path, *, skip_transformers: bool = False) -> bool:
    root = root.resolve()
    _require(root.exists(), f"Processed dataset directory does not exist: {root}")

    statuses = {
        name: _check_artifact_file(root / name)
        for name in REQUIRED_FILES
    }

    pointer_files = [name for name, status in statuses.items() if status == "git-lfs-pointer"]
    if pointer_files:
        print("WARNING: Git-LFS pointer files detected:")
        for name in pointer_files:
            print(f"  - {name}")
        print("Install/pull Git LFS objects before validating the processed dataset:")
        print("  git lfs install")
        print("  git lfs pull")
        # Metadata files may still be real files, but parquet/joblib pointers cannot
        # be validated. Continue only for metadata; return False at the end.

    features = _read_json(root / "feature_columns.json", "feature_columns.json")
    labels = _read_json(root / "label_mapping.json", "label_mapping.json")
    manifest = _read_json(root / "manifest.json", "manifest.json")

    _require(isinstance(features, list) and features, "feature_columns.json must contain a non-empty list")
    _require(all(isinstance(x, str) and x.strip() for x in features), "feature_columns.json contains invalid feature names")
    _require(len(features) == len(set(features)), "feature_columns.json contains duplicate features")
    _require("label" not in {x.lower() for x in features}, "Target leakage: 'label' appears in feature_columns.json")
    _require(isinstance(labels, dict) and labels, "label_mapping.json must contain a non-empty mapping")

    expected_columns = features + ["label"]
    allowed_labels = set(labels.values())
    observed_splits: dict[str, int] = {}
    parquet_ok = True

    for split in SPLITS:
        path = root / f"{split}.parquet"
        if _is_lfs_pointer(path):
            parquet_ok = False
            print(f"{split:10s} SKIPPED — Git-LFS pointer; run `git lfs pull` first")
            continue
        try:
            df = pd.read_parquet(path)
            observed_splits[split] = len(df)
            _require(
                list(df.columns) == expected_columns,
                f"{split}: column order differs from feature_columns.json + label",
            )
            X = df[features]
            _require(X.isna().sum().sum() == 0, f"{split}: NaN values remain")
            _require(np.isfinite(X.to_numpy()).all(), f"{split}: infinite values remain")
            _require(df["label"].notna().all(), f"{split}: missing target labels")
            _require(
                set(df["label"].unique()).issubset(allowed_labels),
                f"{split}: unexpected label values",
            )
            print(f"{split:10s} rows={len(df):>10,} features={len(features):>3} OK")
        except Exception as exc:
            parquet_ok = False
            print(f"{split:10s} FAILED — {type(exc).__name__}: {exc}")

    transformer_warnings: list[str] = []
    if not skip_transformers:
        for filename, name in (("imputer.joblib", "Imputer"), ("scaler.joblib", "Scaler")):
            message = _validate_transformer(root / filename, len(features), name)
            if not message.endswith(": OK"):
                transformer_warnings.append(message)
                print(f"WARNING: {message}")
            else:
                print(message)

    split_manifest = root / "split_manifest.parquet"
    if split_manifest.exists() and not _is_lfs_pointer(split_manifest):
        try:
            sm = pd.read_parquet(split_manifest)
            _require(not sm.empty, "split_manifest.parquet is empty")
            print(f"split_manifest rows={len(sm):>10,} OK")
        except Exception as exc:
            print(f"WARNING: split_manifest.parquet could not be validated: {exc}")
    elif _is_lfs_pointer(split_manifest):
        print("WARNING: split_manifest.parquet is a Git-LFS pointer; skipping.")

    # Check manifest counts only when the actual parquet files were readable.
    if observed_splits:
        for split, observed in observed_splits.items():
            for key in (f"{split}_rows", f"n_{split}", split):
                if key in manifest and isinstance(manifest[key], (int, float)):
                    _require(
                        int(manifest[key]) == observed,
                        f"manifest.json {key}={manifest[key]} but {split}.parquet has {observed} rows",
                    )
                    break

    if pointer_files:
        print("Processed dataset validation incomplete: Git-LFS objects are not hydrated.")
        return False
    if not parquet_ok:
        print("Processed dataset validation failed.")
        return False
    if transformer_warnings:
        print("Processed dataset validation passed with transformer warnings.")
    else:
        print("Processed dataset validation passed.")
    return True


def main() -> int:
    args = parse_args()
    return 0 if validate(args.data_dir, skip_transformers=args.skip_transformers) else 2


if __name__ == "__main__":
    raise SystemExit(main())
