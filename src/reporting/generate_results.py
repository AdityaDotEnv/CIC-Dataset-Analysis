from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.visualization.plots import (
    plot_class_distribution,
    plot_confusion_matrix,
    plot_dataset_comparison,
    plot_model_comparison,
    plot_per_class_f1,
)


def _first_existing(root: Path, patterns: list[str]) -> Path | None:
    candidates: list[Path] = []
    for pattern in patterns:
        candidates.extend(root.rglob(pattern))
    candidates = [p for p in candidates if p.is_file() and "reporting" not in p.parts]
    return sorted(candidates)[0] if candidates else None


def _read_csv(path: Path | None) -> pd.DataFrame | None:
    if path is None:
        return None
    try:
        return pd.read_csv(path)
    except Exception:
        return None


def generate_result_figures(results_root: str | Path, output_dir: str | Path) -> list[dict[str, str]]:
    """Generate reusable publication/dashboard figures from stable result CSVs."""
    root = Path(results_root)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    generated: list[dict[str, str]] = []

    model_path = _first_existing(root, [
        "final/dashboard_data/ml_metrics.csv",
        "final/ml/final_ml_metrics.csv",
        "ml_baseline/model_comparison.csv",
        "*model*comparison*.csv",
    ])
    model = _read_csv(model_path)
    if model is not None and "model" in model.columns:
        for metric in ["macro_f1", "macro_recall", "balanced_accuracy", "weighted_f1"]:
            if metric in model.columns:
                dst = out / f"model_comparison_{metric}.png"
                plot_model_comparison(model, dst, metric=metric)
                generated.append({"figure": dst.name, "source": str(model_path.relative_to(root))})

    per_class_path = _first_existing(root, [
        "final/dashboard_data/ml_per_class_metrics.csv",
        "final/ml/final_per_class_metrics.csv",
        "*per_class*metrics*.csv",
    ])
    per_class = _read_csv(per_class_path)
    if per_class is not None:
        try:
            dst = out / "final_per_class_f1.png"
            plot_per_class_f1(per_class, dst)
            generated.append({"figure": dst.name, "source": str(per_class_path.relative_to(root))})
        except KeyError:
            pass

    cm_path = _first_existing(root, [
        "final/dashboard_data/ml_confusion_matrix.csv",
        "final/ml/final_confusion_matrix.csv",
        "*confusion*matrix*.csv",
    ])
    cm = _read_csv(cm_path)
    if cm is not None:
        try:
            if cm.columns[0].lower().startswith("unnamed") or cm.columns[0].lower() in {"label", "true_label", "actual"}:
                cm = cm.set_index(cm.columns[0])
            dst = out / "final_confusion_matrix.png"
            plot_confusion_matrix(cm, dst)
            generated.append({"figure": dst.name, "source": str(cm_path.relative_to(root))})
        except Exception:
            pass

    comparison_path = _first_existing(root, [
        "cross_dataset_comparison/dataset_comparison_matrix.csv",
        "*dataset*comparison*.csv",
        "*comparison*matrix*.csv",
    ])
    comparison = _read_csv(comparison_path)
    if comparison is not None:
        dataset_col = next((c for c in comparison.columns if c.lower() in {"dataset", "dataset_name", "name"}), None)
        if dataset_col:
            preferred = [
                "total_rows", "records", "row_count", "n_rows",
                "num_classes", "class_count", "missing_percentage", "duplicate_percentage",
            ]
            for metric in preferred:
                if metric in comparison.columns:
                    try:
                        dst = out / f"dataset_comparison_{metric}.png"
                        plot_dataset_comparison(comparison, dst, metric=metric, dataset_col=dataset_col)
                        generated.append({"figure": dst.name, "source": str(comparison_path.relative_to(root))})
                    except Exception:
                        pass

    class_paths = sorted(root.rglob("*class_distribution*.csv"))
    for path in class_paths:
        if "reporting" in path.parts:
            continue
        frame = _read_csv(path)
        if frame is None:
            continue
        label_col = next((c for c in frame.columns if c.lower() in {"label", "class", "traffic_class", "attack"}), None)
        count_col = next((c for c in frame.columns if c.lower() in {"count", "records", "frequency", "row_count"}), None)
        if label_col and count_col:
            slug = "_".join(path.relative_to(root).with_suffix("").parts).replace(" ", "_")
            dst = out / f"{slug}.png"
            try:
                plot_class_distribution(frame, dst, label_col=label_col, count_col=count_col, title=path.parent.name.replace("_", " ").title())
                generated.append({"figure": dst.name, "source": str(path.relative_to(root))})
            except Exception:
                pass

    pd.DataFrame(generated).to_csv(out / "figure_manifest.csv", index=False)
    (out / "figure_manifest.json").write_text(json.dumps(generated, indent=2), encoding="utf-8")
    return generated
