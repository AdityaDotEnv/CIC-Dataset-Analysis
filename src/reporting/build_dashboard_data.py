from __future__ import annotations

import json
import re
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd

from src.analysis.metrics import confusion_matrix_long
from src.ingestion.loaders import read_table


@dataclass
class ArtifactRecord:
    name: str
    source: str
    output: str
    category: str
    rows: int | None
    columns: int | None
    status: str
    note: str = ""


CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("final_decision", ("final_dataset", "dataset_decision", "recommendation", "selection")),
    ("ml", ("model_comparison", "test_metrics", "per_class", "confusion", "baseline", "evaluation")),
    ("dataset_comparison", ("final_comparison", "dataset_comparison", "comparison_matrix", "cross_dataset")),
    ("class_analysis", ("class_distribution", "class_balance", "class_presence", "rare_class", "attack_distribution", "benign")),
    ("feature_analysis", ("feature_quality", "feature_distribution", "correlation", "skew", "kurt", "percentile", "extreme", "constant", "redund")),
    ("dataset_quality", ("dataset_summary", "data_quality", "missing", "infinite", "duplicate", "schema", "dtype", "inventory")),
    ("preprocessing", ("preprocessing", "feature_selection", "selected_features", "split_manifest")),
]


def _slug(value: str) -> str:
    value = value.lower().replace("\\", "/")
    value = re.sub(r"[^a-z0-9]+", "_", value).strip("_")
    return value or "artifact"


def _classify(path: Path) -> str:
    text = _slug(path.as_posix())
    for category, needles in CATEGORY_RULES:
        if any(needle in text for needle in needles):
            return category
    return "supporting"


def _discover_tabular_artifacts(results_root: Path) -> list[Path]:
    if not results_root.exists():
        raise FileNotFoundError(f"Results directory does not exist: {results_root}")
    ignored_parts = {"reporting", "dashboard_data", "dashboard", "figures"}
    files: list[Path] = []
    for path in results_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".csv", ".parquet", ".pq"}:
            continue
        rel_parts = set(path.relative_to(results_root).parts[:-1])
        if rel_parts & ignored_parts:
            continue
        files.append(path)
    return sorted(files)


def _normalise_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Make notebook-produced tables safer for Power BI/Tableau ingestion."""
    out = frame.copy()
    out.columns = [str(c).strip() for c in out.columns]
    unnamed = [c for c in out.columns if c.lower().startswith("unnamed:")]
    if unnamed:
        out = out.drop(columns=unnamed)
    for column in out.select_dtypes(include=["object"]).columns:
        out[column] = out[column].map(lambda x: x.strip() if isinstance(x, str) else x)
    return out


def _is_confusion_matrix(path: Path, frame: pd.DataFrame) -> bool:
    name = _slug(path.stem)
    if "confusion" not in name:
        return False
    return frame.shape[0] > 1 and frame.shape[1] > 1


def _prepare_confusion_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    work = frame.copy()
    if work.columns[0].lower().startswith("unnamed") or work.columns[0].lower() in {"label", "true_label", "actual"}:
        work = work.set_index(work.columns[0])
    elif isinstance(work.index, pd.RangeIndex):
        # Some notebook exports omit the explicit index column. Preserve the matrix
        # shape while still producing long-form data.
        work.index = work.columns[: len(work.index)] if len(work.columns) == len(work.index) else work.index
    return confusion_matrix_long(work)


def build_dashboard_data(
    results_root: str | Path,
    output_dir: str | Path,
    *,
    include_supporting: bool = True,
) -> list[ArtifactRecord]:
    """
    Export stable notebook/result artifacts into a dashboard-ready staging area.

    The function intentionally consumes already-generated analysis tables. It never
    reloads raw CIC datasets, so the dashboard remains lightweight and reproducible.
    """
    root = Path(results_root)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    records: list[ArtifactRecord] = []
    name_counts: dict[str, int] = {}

    for src in _discover_tabular_artifacts(root):
        category = _classify(src)
        if category == "supporting" and not include_supporting:
            continue

        rel = src.relative_to(root)
        base = _slug("__".join(rel.with_suffix("").parts))
        name_counts[base] = name_counts.get(base, 0) + 1
        exported_name = base if name_counts[base] == 1 else f"{base}_{name_counts[base]}"
        dst = out / category / f"{exported_name}.csv"
        dst.parent.mkdir(parents=True, exist_ok=True)

        try:
            frame = read_table(src)
            frame = _normalise_frame(frame)
            if _is_confusion_matrix(src, frame):
                frame = _prepare_confusion_matrix(frame)
            frame.to_csv(dst, index=False)
            records.append(
                ArtifactRecord(
                    name=exported_name,
                    source=rel.as_posix(),
                    output=dst.relative_to(out).as_posix(),
                    category=category,
                    rows=len(frame),
                    columns=len(frame.columns),
                    status="exported",
                )
            )
        except Exception as exc:  # manifest should expose bad artifacts instead of silently hiding them
            records.append(
                ArtifactRecord(
                    name=exported_name,
                    source=rel.as_posix(),
                    output="",
                    category=category,
                    rows=None,
                    columns=None,
                    status="error",
                    note=f"{type(exc).__name__}: {exc}",
                )
            )

    manifest = pd.DataFrame([asdict(record) for record in records])
    manifest.to_csv(out / "dashboard_manifest.csv", index=False)

    category_summary = (
        manifest.groupby(["category", "status"], dropna=False)
        .size()
        .reset_index(name="artifact_count")
        if not manifest.empty
        else pd.DataFrame(columns=["category", "status", "artifact_count"])
    )
    category_summary.to_csv(out / "dashboard_category_summary.csv", index=False)

    metadata = {
        "results_root": str(root),
        "output_dir": str(out),
        "exported_artifacts": int((manifest["status"] == "exported").sum()) if not manifest.empty else 0,
        "failed_artifacts": int((manifest["status"] == "error").sum()) if not manifest.empty else 0,
        "categories": sorted(manifest["category"].dropna().unique().tolist()) if not manifest.empty else [],
        "design": "artifact-driven; consumes notebook/result tables without reloading raw datasets",
    }
    (out / "dashboard_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    return records


def copy_dashboard_bundle(source_dir: str | Path, destination: str | Path) -> Path:
    """Copy an already-built dashboard staging directory for external BI tooling."""
    source = Path(source_dir)
    destination = Path(destination)
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(source, destination)
    return destination
