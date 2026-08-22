"""Reproducible, leakage-safe train/validation/test splitting.

Per PHASE_02_DATASET_PIPELINE.md / ML_SPEC.md:
- split before augmentation (this module only ever produces file-path
  manifests; augmentation is applied later, at load time, train-split only)
- stratified per class so class balance is preserved across splits
- images sharing identical content (duplicates) are kept together in a
  single split so the same physical image never crosses splits
- fixed seed for reproducibility
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from ml.src.data.inventory import ImageRecord

SPLIT_NAMES = ("train", "val", "test")


@dataclass(frozen=True)
class SplitRatios:
    train: float
    val: float
    test: float

    def __post_init__(self) -> None:
        total = self.train + self.val + self.test
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Split ratios must sum to 1.0, got {total}")
        if min(self.train, self.val, self.test) < 0:
            raise ValueError("Split ratios must be non-negative")


def _group_key(record: ImageRecord, content_hashes: dict[Path, str] | None) -> str:
    if content_hashes is not None:
        return content_hashes[record.path]
    return str(record.path)


def stratified_group_split(
    records: list[ImageRecord],
    ratios: SplitRatios,
    seed: int = 42,
    content_hashes: dict[Path, str] | None = None,
) -> dict[str, list[ImageRecord]]:
    """Split records per class, assigning whole duplicate-content groups
    to a single split so no physical image crosses splits.
    """
    rng = random.Random(seed)
    result: dict[str, list[ImageRecord]] = {name: [] for name in SPLIT_NAMES}

    records_by_class: dict[str, list[ImageRecord]] = {}
    for record in records:
        records_by_class.setdefault(record.class_name, []).append(record)

    for class_name in sorted(records_by_class):
        class_records = records_by_class[class_name]

        groups: dict[str, list[ImageRecord]] = {}
        for record in class_records:
            key = _group_key(record, content_hashes)
            groups.setdefault(key, []).append(record)

        group_keys = sorted(groups.keys())
        rng.shuffle(group_keys)

        n_total = len(class_records)
        target_train = round(n_total * ratios.train)
        target_val = round(n_total * ratios.val)

        assigned_train = assigned_val = 0
        for key in group_keys:
            group = groups[key]
            if assigned_train < target_train:
                result["train"].extend(group)
                assigned_train += len(group)
            elif assigned_val < target_val:
                result["val"].extend(group)
                assigned_val += len(group)
            else:
                result["test"].extend(group)

    for name in SPLIT_NAMES:
        result[name].sort(key=lambda r: str(r.path))
    return result


def verify_no_overlap(
    splits: dict[str, list[ImageRecord]],
    content_hashes: dict[Path, str] | None = None,
) -> bool:
    """Return True iff no path (and, if hashes given, no content hash)
    appears in more than one split.
    """
    path_sets = {name: {r.path for r in records} for name, records in splits.items()}
    names = list(path_sets)
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if path_sets[names[i]] & path_sets[names[j]]:
                return False

    if content_hashes is not None:
        hash_sets = {
            name: {content_hashes[r.path] for r in records} for name, records in splits.items()
        }
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                if hash_sets[names[i]] & hash_sets[names[j]]:
                    return False
    return True


def save_split_manifests(
    splits: dict[str, list[ImageRecord]], out_dir: Path, dataset_root: Path
) -> dict[str, Path]:
    """Write one JSON manifest per split: a list of
    ``{"path": "<relative to dataset_root>", "class": "<class_name>"}``.

    Only manifests (file lists) are written, not copies of the images
    themselves, per the phase's "do not duplicate the dataset" rule.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dataset_root = Path(dataset_root)

    written: dict[str, Path] = {}
    for name, records in splits.items():
        entries = [
            {
                "path": str(r.path.relative_to(dataset_root).as_posix()),
                "class": r.class_name,
            }
            for r in records
        ]
        out_path = out_dir / f"{name}.json"
        out_path.write_text(json.dumps(entries, indent=2) + "\n", encoding="utf-8")
        written[name] = out_path
    return written


def load_split_manifest(path: Path) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
