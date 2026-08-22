"""Build reproducible, leakage-safe train/val/test splits and the class
mapping from the acquired PlantVillage dataset.

Usage:
    python ml/scripts/build_splits.py

Writes:
    data/class_mapping.json
    data/processed/splits/{train,val,test}.json   (path/class manifests)
    data/processed/metadata/split_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path

from ml.src.data.class_mapping import build_class_mapping, save_class_mapping
from ml.src.data.inventory import discover_images, sha256_of_file
from ml.src.data.splits import SplitRatios, save_split_manifests, stratified_group_split, verify_no_overlap

ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = ROOT / "data" / "raw" / "plantvillage" / "raw" / "color"
CLASS_MAPPING_PATH = ROOT / "data" / "class_mapping.json"
SPLITS_DIR = ROOT / "data" / "processed" / "splits"
SPLIT_SUMMARY_PATH = ROOT / "data" / "processed" / "metadata" / "split_summary.json"

SEED = 42
RATIOS = SplitRatios(train=0.70, val=0.15, test=0.15)


def main() -> None:
    if not DATASET_ROOT.is_dir():
        raise SystemExit(
            f"Dataset not found at {DATASET_ROOT}. Run ml/scripts/acquire_dataset.py first."
        )

    records = discover_images(DATASET_ROOT)
    if not records:
        raise SystemExit(f"No images discovered under {DATASET_ROOT}.")

    class_mapping = build_class_mapping(r.class_name for r in records)
    save_class_mapping(class_mapping, CLASS_MAPPING_PATH)

    content_hashes = {r.path: sha256_of_file(r.path) for r in records}

    splits = stratified_group_split(records, RATIOS, seed=SEED, content_hashes=content_hashes)

    if not verify_no_overlap(splits, content_hashes=content_hashes):
        raise SystemExit("Split overlap detected — refusing to write manifests.")

    written = save_split_manifests(splits, SPLITS_DIR, DATASET_ROOT)

    summary = {
        "seed": SEED,
        "ratios": {"train": RATIOS.train, "val": RATIOS.val, "test": RATIOS.test},
        "num_classes": len(class_mapping),
        "total_images": len(records),
        "split_counts": {name: len(records_) for name, records_ in splits.items()},
        "no_overlap_verified": True,
        "manifest_paths": {name: str(p.relative_to(ROOT).as_posix()) for name, p in written.items()},
    }
    SPLIT_SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SPLIT_SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(summary, indent=2))
    print(f"\nClass mapping written to {CLASS_MAPPING_PATH}")


if __name__ == "__main__":
    main()
