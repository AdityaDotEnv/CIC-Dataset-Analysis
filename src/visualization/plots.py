from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _save(fig, output_path: str | Path, dpi: int = 180) -> Path:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(output, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return output


def plot_confusion_matrix(matrix: pd.DataFrame, output_path: str | Path, title: str = "Confusion Matrix") -> Path:
    fig, ax = plt.subplots(figsize=(10, 8))
    image = ax.imshow(matrix.to_numpy(), aspect="auto")
    ax.set_xlabel("Predicted label")
    ax.set_ylabel("True label")
    ax.set_title(title)
    ax.set_xticks(range(len(matrix.columns)), labels=[str(x) for x in matrix.columns], rotation=90)
    ax.set_yticks(range(len(matrix.index)), labels=[str(x) for x in matrix.index])
    fig.colorbar(image, ax=ax, label="Count")
    return _save(fig, output_path)


def plot_model_comparison(
    metrics: pd.DataFrame,
    output_path: str | Path,
    metric: str = "macro_f1",
    title: str | None = None,
) -> Path:
    if "model" not in metrics.columns or metric not in metrics.columns:
        raise KeyError(f"Expected columns 'model' and '{metric}'")
    work = metrics.sort_values(metric, ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.bar(work["model"].astype(str), pd.to_numeric(work[metric], errors="coerce"))
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_title(title or f"Model Comparison — {metric.replace('_', ' ').title()}")
    ax.tick_params(axis="x", rotation=30)
    ax.set_ylim(bottom=0)
    return _save(fig, output_path)


def plot_class_distribution(
    frame: pd.DataFrame,
    output_path: str | Path,
    label_col: str = "label",
    count_col: str = "count",
    title: str = "Class Distribution",
    top_n: int | None = 25,
) -> Path:
    if label_col not in frame.columns or count_col not in frame.columns:
        raise KeyError(f"Expected columns '{label_col}' and '{count_col}'")
    work = frame[[label_col, count_col]].copy()
    work[count_col] = pd.to_numeric(work[count_col], errors="coerce")
    work = work.dropna().sort_values(count_col, ascending=True)
    if top_n:
        work = work.tail(top_n)
    fig, ax = plt.subplots(figsize=(10, max(5, 0.32 * len(work))))
    ax.barh(work[label_col].astype(str), work[count_col])
    ax.set_xlabel("Records")
    ax.set_title(title)
    return _save(fig, output_path)


def plot_dataset_comparison(
    frame: pd.DataFrame,
    output_path: str | Path,
    metric: str,
    dataset_col: str = "dataset",
    title: str | None = None,
) -> Path:
    if dataset_col not in frame.columns or metric not in frame.columns:
        raise KeyError(f"Expected columns '{dataset_col}' and '{metric}'")
    values = pd.to_numeric(frame[metric], errors="coerce")
    mask = values.notna()
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(frame.loc[mask, dataset_col].astype(str), values[mask])
    ax.set_ylabel(metric.replace("_", " ").title())
    ax.set_title(title or f"Dataset Comparison — {metric.replace('_', ' ').title()}")
    return _save(fig, output_path)


def plot_per_class_f1(frame: pd.DataFrame, output_path: str | Path, title: str = "Per-Class F1") -> Path:
    label_col = next((c for c in ["label", "class", "traffic_class"] if c in frame.columns), None)
    f1_col = next((c for c in ["f1-score", "f1_score", "f1"] if c in frame.columns), None)
    if label_col is None or f1_col is None:
        raise KeyError("Could not identify label and F1 columns")
    work = frame[[label_col, f1_col]].copy()
    work[f1_col] = pd.to_numeric(work[f1_col], errors="coerce")
    work = work.dropna().sort_values(f1_col)
    fig, ax = plt.subplots(figsize=(10, max(5, 0.32 * len(work))))
    ax.barh(work[label_col].astype(str), work[f1_col])
    ax.set_xlabel("F1 score")
    ax.set_xlim(0, 1)
    ax.set_title(title)
    return _save(fig, output_path)
