"""Inspect the acquired PlantVillage dataset and write a report.

Usage:
    python ml/scripts/inspect_dataset.py

Writes data/processed/metadata/dataset_report.json and prints a summary.
Does not assume any expected counts; it reports exactly what the pipeline
observes on disk (PHASE_02_DATASET_PIPELINE.md: "Do not blindly assume the
image count from a webpage; report the count actually observed").
"""

from __future__ import annotations

import json
from pathlib import Path

from ml.src.data.inventory import inspect_dataset

ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = ROOT / "data" / "raw" / "plantvillage" / "raw" / "color"
REPORT_PATH = ROOT / "data" / "processed" / "metadata" / "dataset_report.json"

EXPECTED_PLANTVILLAGE_CLASS_COUNT = 38


def main() -> None:
    if not DATASET_ROOT.is_dir():
        raise SystemExit(
            f"Dataset not found at {DATASET_ROOT}. Run ml/scripts/acquire_dataset.py first."
        )

    report = inspect_dataset(DATASET_ROOT, compute_hashes=True)

    total_bytes = sum(f.stat().st_size for f in DATASET_ROOT.rglob("*") if f.is_file())

    summary = {
        "dataset_root": str(DATASET_ROOT.relative_to(ROOT).as_posix()),
        "total_images": report.total_images,
        "num_classes": report.num_classes,
        "expected_class_count": EXPECTED_PLANTVILLAGE_CLASS_COUNT,
        "class_count_matches_expected": report.num_classes == EXPECTED_PLANTVILLAGE_CLASS_COUNT,
        "class_counts": report.class_counts,
        "corrupt_file_count": len(report.corrupt_files),
        "corrupt_files": [str(p.relative_to(ROOT).as_posix()) for p in report.corrupt_files],
        "duplicate_content_group_count": len(report.duplicate_content_groups),
        "duplicate_filename_group_count": len(report.duplicate_filename_groups),
        "local_size_bytes": total_bytes,
        "local_size_mib": round(total_bytes / (1024 ** 2), 2),
    }

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2)[:4000])
    print(f"\nFull report written to {REPORT_PATH}")


if __name__ == "__main__":
    main()
