"""Acquire the PlantVillage dataset (Phase 02).

Source (documented per PHASE_02_DATASET_PIPELINE.md acquisition rules):
    Repository : https://github.com/spMohanty/PlantVillage-Dataset
    Commit     : 7f7ecc7e1eaca78107e3affe7cb5abd9427e139a  (pinned, immutable)
    Subfolder  : raw/color   (RGB leaf images; the repo also contains
                 raw/grayscale and raw/segmented derivatives of the same
                 photographs, which are not needed for this project and
                 are intentionally excluded from the download)
    License    : none declared by the upstream repository at the pinned
                 commit (GitHub's license API returns null / no LICENSE
                 file present). Data originates from the PlantVillage
                 project / Mohanty, Hughes & Salathe (2016) and is widely
                 used for research and benchmarking; verify redistribution
                 terms before any use beyond research/education.

This is the canonical, most-cited source for the PlantVillage dataset and
provides raw per-class image folders, which this project's pipeline
(ml/src/data, ml/src/preprocessing) is built around. TensorFlow Datasets'
`plant_village` was considered first but repackages the same imagery into
TFRecord shards, which is a worse fit for the raw-folder pipeline described
in ML_SPEC.md / PHASE_02_DATASET_PIPELINE.md.

Method: a git partial clone (`--filter=blob:none`) + cone-mode sparse
checkout restricted to `raw/color`, so only the objects actually needed are
downloaded (no full repository history, no grayscale/segmented blobs).

Re-run this script to reproduce the acquisition:
    python ml/scripts/acquire_dataset.py
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import urllib.request
from pathlib import Path

REPO_URL = "https://github.com/spMohanty/PlantVillage-Dataset.git"
PINNED_COMMIT = "7f7ecc7e1eaca78107e3affe7cb5abd9427e139a"
SPARSE_PATH = "raw/color"

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "data" / "raw" / "plantvillage"


def check_network(url: str = "https://github.com", timeout: float = 10.0) -> bool:
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except Exception:
        return False


def run(cmd: list[str], cwd: Path) -> None:
    print(f"$ {' '.join(cmd)}  (cwd={cwd})")
    subprocess.run(cmd, cwd=str(cwd), check=True)


def acquire(commit: str = PINNED_COMMIT, dest: Path = DEST) -> Path:
    if not check_network():
        print(
            "BLOCKER: no network access to github.com from this environment.\n"
            "Reproduce manually once network access is available:\n\n"
            f"  git init {dest}\n"
            f"  git -C {dest} remote add origin {REPO_URL}\n"
            f"  git -C {dest} sparse-checkout init --cone\n"
            f"  git -C {dest} sparse-checkout set {SPARSE_PATH}\n"
            f"  git -C {dest} fetch --depth 1 --filter=blob:none origin {commit}\n"
            f"  git -C {dest} checkout FETCH_HEAD -- .\n",
            file=sys.stderr,
        )
        raise SystemExit(1)

    dest.mkdir(parents=True, exist_ok=True)
    if not (dest / ".git").exists():
        run(["git", "init", "-q"], cwd=dest)
        run(["git", "remote", "add", "origin", REPO_URL], cwd=dest)

    run(["git", "sparse-checkout", "init", "--cone"], cwd=dest)
    run(["git", "sparse-checkout", "set", SPARSE_PATH], cwd=dest)
    run(["git", "fetch", "--depth", "1", "--filter=blob:none", "origin", commit], cwd=dest)
    run(["git", "checkout", "FETCH_HEAD", "--", "."], cwd=dest)

    image_root = dest / SPARSE_PATH
    if not image_root.is_dir():
        raise SystemExit(f"Acquisition finished but {image_root} was not created.")
    return image_root


def report_size(path: Path) -> int:
    return sum(f.stat().st_size for f in path.rglob("*") if f.is_file())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", default=PINNED_COMMIT)
    parser.add_argument("--dest", default=str(DEST))
    args = parser.parse_args()

    image_root = acquire(commit=args.commit, dest=Path(args.dest))
    total_bytes = report_size(image_root)
    print(f"Acquired dataset at: {image_root}")
    print(f"Local size: {total_bytes / (1024 ** 2):.2f} MiB ({total_bytes} bytes)")
