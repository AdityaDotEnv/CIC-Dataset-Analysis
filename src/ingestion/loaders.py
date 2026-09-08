from __future__ import annotations

from collections.abc import Iterable, Iterator
from pathlib import Path

import pandas as pd


def discover_csv_files(data_dir: str | Path) -> list[Path]:
    root = Path(data_dir)
    files = sorted(p for p in root.rglob("*.csv") if p.is_file())
    if not files:
        raise FileNotFoundError(f"No CSV files found under {root}")
    return files


def iter_csv_chunks(
    file: str | Path,
    chunksize: int = 100_000,
    usecols: Iterable[str] | None = None,
) -> Iterator[pd.DataFrame]:
    yield from pd.read_csv(file, chunksize=chunksize, usecols=usecols, low_memory=False)


def read_headers(files: Iterable[str | Path]) -> dict[str, list[str]]:
    return {Path(f).name: list(pd.read_csv(f, nrows=0).columns) for f in files}


def read_table(path: str | Path, **kwargs) -> pd.DataFrame:
    """Read a CSV or parquet project artifact using one shared entry point."""
    path = Path(path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(path, **kwargs)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(path, **kwargs)
    raise ValueError(f"Unsupported tabular artifact: {path}")
