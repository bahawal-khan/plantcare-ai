"""Phase 02 tests: split logic on small synthetic fixtures — reproducible
seeding, stratification, and no-overlap/leakage guarantees.
"""

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from ml.src.data.inventory import ImageRecord, discover_images, sha256_of_file
from ml.src.data.splits import (
    SplitRatios,
    load_split_manifest,
    save_split_manifests,
    stratified_group_split,
    verify_no_overlap,
)


def _make_image(
    path: Path, color: tuple[int, int, int], size=(8, 8)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    array = np.full((size[1], size[0], 3), color, dtype=np.uint8)
    Image.fromarray(array).save(path)


def _make_class_images(root: Path, class_name: str, n: int) -> None:
    for i in range(n):
        _make_image(root / class_name / f"{class_name}_{i:03d}.jpg", (i % 256, 0, 0))


@pytest.fixture
def fixture_records(tmp_path: Path) -> list[ImageRecord]:
    _make_class_images(tmp_path, "ClassA", 20)
    _make_class_images(tmp_path, "ClassB", 20)
    return discover_images(tmp_path)


def test_split_ratios_reject_invalid_sum():
    with pytest.raises(ValueError):
        SplitRatios(train=0.8, val=0.1, test=0.2)


def test_split_sizes_approximate_ratios(fixture_records):
    ratios = SplitRatios(train=0.7, val=0.15, test=0.15)
    splits = stratified_group_split(fixture_records, ratios, seed=42)
    total = sum(len(v) for v in splits.values())
    assert total == len(fixture_records)
    assert len(splits["train"]) == 28  # 0.7 * 40
    assert len(splits["val"]) == 6
    assert len(splits["test"]) == 6


def test_split_is_stratified_per_class(fixture_records):
    ratios = SplitRatios(train=0.7, val=0.15, test=0.15)
    splits = stratified_group_split(fixture_records, ratios, seed=42)
    for split_name, records in splits.items():
        counts = {"ClassA": 0, "ClassB": 0}
        for r in records:
            counts[r.class_name] += 1
        assert counts["ClassA"] == counts["ClassB"], split_name


def test_split_is_deterministic_for_fixed_seed(fixture_records):
    ratios = SplitRatios(train=0.7, val=0.15, test=0.15)
    splits_a = stratified_group_split(fixture_records, ratios, seed=42)
    splits_b = stratified_group_split(fixture_records, ratios, seed=42)
    assert [r.path for r in splits_a["train"]] == [r.path for r in splits_b["train"]]
    assert [r.path for r in splits_a["test"]] == [r.path for r in splits_b["test"]]


def test_no_overlap_between_splits(fixture_records):
    ratios = SplitRatios(train=0.7, val=0.15, test=0.15)
    splits = stratified_group_split(fixture_records, ratios, seed=42)
    assert verify_no_overlap(splits) is True


def test_duplicate_content_stays_in_one_split(tmp_path: Path):
    _make_image(tmp_path / "ClassA" / "orig.jpg", (5, 5, 5))
    _make_image(tmp_path / "ClassA" / "dup1.jpg", (5, 5, 5))
    _make_image(tmp_path / "ClassA" / "dup2.jpg", (5, 5, 5))
    for i in range(17):
        _make_image(tmp_path / "ClassA" / f"other_{i}.jpg", (i, 1, 1))

    records = discover_images(tmp_path)
    hashes = {r.path: sha256_of_file(r.path) for r in records}
    ratios = SplitRatios(train=0.7, val=0.15, test=0.15)
    splits = stratified_group_split(records, ratios, seed=42, content_hashes=hashes)

    assert verify_no_overlap(splits, content_hashes=hashes) is True

    dup_hash = hashes[tmp_path / "ClassA" / "orig.jpg"]
    containing_splits = [
        name for name, recs in splits.items() if any(hashes[r.path] == dup_hash for r in recs)
    ]
    assert len(containing_splits) == 1


def test_verify_no_overlap_detects_injected_leakage(fixture_records):
    ratios = SplitRatios(train=0.7, val=0.15, test=0.15)
    splits = stratified_group_split(fixture_records, ratios, seed=42)
    leaked = dict(splits)
    leaked["val"] = list(leaked["val"]) + [leaked["train"][0]]
    assert verify_no_overlap(leaked) is False


def test_save_and_load_split_manifests(tmp_path: Path, fixture_records):
    ratios = SplitRatios(train=0.7, val=0.15, test=0.15)
    splits = stratified_group_split(fixture_records, ratios, seed=42)
    out_dir = tmp_path / "_out"
    written = save_split_manifests(splits, out_dir, dataset_root=tmp_path)

    train_manifest = load_split_manifest(written["train"])
    assert len(train_manifest) == len(splits["train"])
    assert all("path" in e and "class" in e for e in train_manifest)

    raw = json.loads(written["test"].read_text(encoding="utf-8"))
    assert isinstance(raw, list)
