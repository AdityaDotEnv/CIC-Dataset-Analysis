from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def classification_metrics(y_true, y_pred) -> dict[str, float]:
    """Return the project-level multiclass metrics used by the notebooks."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "macro_precision": float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
        "macro_recall": float(recall_score(y_true, y_pred, average="macro", zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
    }


def per_class_metrics(y_true, y_pred, labels: Sequence | None = None) -> pd.DataFrame:
    """Return one row per traffic class; aggregate rows are removed."""
    report = classification_report(
        y_true,
        y_pred,
        labels=labels,
        output_dict=True,
        zero_division=0,
    )
    frame = pd.DataFrame(report).T.reset_index(names="label")
    return frame[~frame["label"].isin(["accuracy", "macro avg", "weighted avg"])].reset_index(drop=True)


def confusion_matrix_frame(y_true, y_pred, labels: Sequence | None = None) -> pd.DataFrame:
    """Return a labelled confusion matrix suitable for CSV/dashboard export."""
    if labels is None:
        labels = sorted(set(pd.Series(y_true).dropna()) | set(pd.Series(y_pred).dropna()))
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    return pd.DataFrame(cm, index=labels, columns=labels)


def confusion_matrix_long(matrix: pd.DataFrame) -> pd.DataFrame:
    """Convert a matrix-shaped confusion matrix to Power BI/Tableau-friendly long form."""
    work = matrix.copy()
    if work.index.name is None:
        work.index.name = "true_label"
    long = work.reset_index().melt(id_vars=work.index.name, var_name="predicted_label", value_name="count")
    long["count"] = pd.to_numeric(long["count"], errors="coerce").fillna(0).astype(np.int64)
    return long
