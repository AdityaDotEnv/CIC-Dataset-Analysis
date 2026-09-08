from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


def clean_numeric_features(frame: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
    """Notebook-equivalent numeric coercion before fitted transformations are applied."""
    missing = [c for c in feature_columns if c not in frame.columns]
    if missing:
        raise KeyError(f"Missing required feature columns: {missing[:10]}")

    X = frame.loc[:, feature_columns].copy()
    for column in feature_columns:
        X[column] = pd.to_numeric(X[column], errors="coerce")
    return X.replace([np.inf, -np.inf], np.nan)


def fit_train_transformers(X_train: pd.DataFrame):
    """Fit imputation/scaling on training data only."""
    imputer = SimpleImputer(strategy="median")
    X_imp = imputer.fit_transform(X_train)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imp)
    return imputer, scaler, X_scaled


def transform_with_fitted_objects(X: pd.DataFrame, imputer, scaler):
    return scaler.transform(imputer.transform(X))


def save_preprocessing_objects(
    output_dir: str | Path,
    feature_columns: list[str],
    label_mapping: dict,
    imputer,
    scaler,
    manifest: dict,
) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "feature_columns.json").write_text(json.dumps(feature_columns, indent=2), encoding="utf-8")
    (out / "label_mapping.json").write_text(json.dumps(label_mapping, indent=2), encoding="utf-8")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    joblib.dump(imputer, out / "imputer.joblib")
    joblib.dump(scaler, out / "scaler.joblib")
