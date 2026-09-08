from __future__ import annotations

import argparse
import json
import sys
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
        model.fit(train[features], train["label"])
        pred = model.predict(val[features])

        row = classification_metrics(val["label"], pred)
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
    print(f"Baseline evaluation complete. Best validation macro-F1: {comparison.iloc[0]['model']} ({comparison.iloc[0]['macro_f1']:.4f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
