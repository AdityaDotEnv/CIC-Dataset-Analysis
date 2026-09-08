from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

FILES = (
    "feature_columns.json",
    "label_mapping.json",
    "manifest.json",
    "imputer.joblib",
    "scaler.joblib",
    "train.parquet",
    "validation.parquet",
    "test.parquet",
    "split_manifest.parquet",
)


def lfs_info(path: Path):
    raw = path.read_bytes()
    if not raw.startswith(b"version https://git-lfs.github.com/spec/v1"):
        return None
    text = raw.decode("utf-8", errors="replace")
    oid = re.search(r"oid sha256:([0-9a-f]{64})", text)
    size = re.search(r"size (\d+)", text)
    return (oid.group(1) if oid else None, int(size.group(1)) if size else None)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser(description="Diagnose processed CIC-IDS2017 artifacts, including Git-LFS pointers.")
    p.add_argument("--data-dir", type=Path, default=REPO_ROOT / "data" / "processed" / "cicids2017")
    args = p.parse_args()

    root = args.data_dir.resolve()
    if not root.exists():
        print(f"Missing directory: {root}")
        print("The repository archive does not contain processed artifacts. Restore them locally or run the preprocessing notebook.")
        return 2

    pointer_count = 0
    for name in FILES:
        path = root / name
        if not path.exists():
            print(f"MISSING  {name}")
            continue
        info = lfs_info(path)
        if info:
            pointer_count += 1
            oid, expected_size = info
            print(f"LFS      {name:22s} expected_size={expected_size:,} oid={oid}")
        else:
            print(f"LOCAL    {name:22s} size={path.stat().st_size:,} sha256={sha256(path)[:16]}...")

    if pointer_count:
        print("\nGit-LFS objects are not hydrated.")
        print("Run from the repository root:")
        print("  git lfs install")
        print("  git lfs pull")
        print("\nThen rerun:")
        print("  python scripts/diagnose_processed_artifacts.py")
        return 1

    print("\nNo Git-LFS pointer files detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
