from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import joblib
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.analysis.metrics import classification_metrics, confusion_matrix_frame, per_class_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Repeatable script counterpart of the baseline modelling notebook.")
    parser.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data" / "processed" / "cicids2017")
    parser.add_argument("--output-dir", type=Path, default=REPO_ROOT / "results" / "ml_baseline")
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--rf-trees", type=int, default=200)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data = args.data_dir
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    def is_lfs_pointer(path: Path) -> bool:
        try:
            return path.read_bytes()[:80].startswith(b"version https://git-lfs.github.com/spec/v1")
        except OSError:
            return False

    required = ["feature_columns.json", "label_mapping.json", "train.parquet", "validation.parquet"]
    missing = [name for name in required if not (data / name).exists()]
    if missing:
        raise FileNotFoundError(f"Missing processed artifacts: {missing}")

    pointers = [name for name in required if is_lfs_pointer(data / name)]
    if pointers:
        raise RuntimeError(
            "Processed artifacts are Git-LFS pointer files, not hydrated data: "
            + ", ".join(pointers)
            + ". Run `git lfs install` and `git lfs pull`, then rerun this script."
        )

    features = json.loads((data / "feature_columns.json").read_text(encoding="utf-8"))
    label_mapping = json.loads((data / "label_mapping.json").read_text(encoding="utf-8"))
    train = pd.read_parquet(data / "train.parquet", columns=features + ["label"])
    val = pd.read_parquet(data / "validation.parquet", columns=features + ["label"])

    models = {
        "DummyMajority": DummyClassifier(strategy="most_frequent"),
        "LogisticRegression": LogisticRegression(max_iter=1000, class_weight="balanced", random_state=args.random_state),
        "RandomForest": RandomForestClassifier(
            n_estimators=args.rf_trees,
            random_state=args.random_state,
            n_jobs=-1,
            class_weight="balanced_subsample",
            max_features="sqrt",
        ),
    }

    labels = sorted(label_mapping.values())
    comparison_rows: list[dict] = []

    for name, model in models.items():
        print(f"Training {name} ...")
        started = time.perf_counter()
        model.fit(train[features], train["label"])
        pred = model.predict(val[features])
        fit_seconds = time.perf_counter() - started

        row = classification_metrics(val["label"], pred)
        row["fit_seconds"] = fit_seconds
        row["model"] = name
        comparison_rows.append(row)

        per_class = per_class_metrics(val["label"], pred, labels=labels)
        per_class.insert(0, "model", name)
        per_class.to_csv(out / f"{name}_per_class_metrics.csv", index=False)

        cm = confusion_matrix_frame(val["label"], pred, labels=labels)
        cm.index.name = "true_label"
        cm.to_csv(out / f"{name}_confusion_matrix.csv")
        joblib.dump(model, out / f"{name}.joblib")

    comparison = pd.DataFrame(comparison_rows).sort_values("macro_f1", ascending=False)
    comparison.to_csv(out / "model_comparison.csv", index=False)
    best = comparison.iloc[0]
    (out / "selected_baseline.json").write_text(
        json.dumps({
            "model": str(best["model"]),
            "selection_metric": "validation_macro_f1",
            "validation_macro_f1": float(best["macro_f1"]),
        }, indent=2),
        encoding="utf-8",
    )
    print(f"Baseline evaluation complete. Best validation macro-F1: {best['model']} ({best['macro_f1']:.4f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
