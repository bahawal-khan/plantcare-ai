"""Phase 02 tests: dataset discovery/inspection on small synthetic
fixtures. Per TESTING_SPEC.md, unit tests never touch the full dataset.
"""

from pathlib import Path

import numpy as np
from PIL import Image

from ml.src.data.inventory import (
    class_distribution,
    discover_images,
    find_corrupt_images,
    find_duplicate_content,
    find_duplicate_filenames,
    inspect_dataset,
    is_corrupt_image,
    sha256_of_file,
)


def _make_image(path: Path, color: tuple[int, int, int], size=(16, 16)) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    array = np.full((size[1], size[0], 3), color, dtype=np.uint8)
    Image.fromarray(array).save(path)


def _make_fixture_dataset(root: Path) -> None:
    _make_image(root / "ClassA" / "a1.jpg", (255, 0, 0))
    _make_image(root / "ClassA" / "a2.jpg", (0, 255, 0))
    # duplicate content of a1.jpg, different filename
    _make_image(root / "ClassA" / "a3_dup.jpg", (255, 0, 0))
    _make_image(root / "ClassB" / "b1.jpg", (0, 0, 255))
    # corrupt file with an image-like extension
    corrupt_path = root / "ClassB" / "b2_corrupt.jpg"
    corrupt_path.parent.mkdir(parents=True, exist_ok=True)
    corrupt_path.write_bytes(b"not a real image")


def test_discover_images_counts_and_classes(tmp_path: Path):
    _make_fixture_dataset(tmp_path)
    records = discover_images(tmp_path)
    assert len(records) == 5
    counts = class_distribution(records)
    assert counts == {"ClassA": 3, "ClassB": 2}


def test_corrupt_image_detection(tmp_path: Path):
    _make_fixture_dataset(tmp_path)
    records = discover_images(tmp_path)
    corrupt = find_corrupt_images(records)
    assert len(corrupt) == 1
    assert corrupt[0].name == "b2_corrupt.jpg"


def test_valid_image_is_not_corrupt(tmp_path: Path):
    path = tmp_path / "ok.jpg"
    _make_image(path, (10, 20, 30))
    assert is_corrupt_image(path) is False


def test_duplicate_content_detection(tmp_path: Path):
    _make_fixture_dataset(tmp_path)
    records = discover_images(tmp_path)
    duplicates = find_duplicate_content(records)
    assert len(duplicates) == 1
    (group,) = duplicates.values()
    names = sorted(p.name for p in group)
    assert names == ["a1.jpg", "a3_dup.jpg"]


def test_duplicate_filename_detection_no_false_positives(tmp_path: Path):
    _make_fixture_dataset(tmp_path)
    records = discover_images(tmp_path)
    assert find_duplicate_filenames(records) == {}


def test_sha256_is_stable_for_identical_content(tmp_path: Path):
    p1, p2 = tmp_path / "x.jpg", tmp_path / "y.jpg"
    _make_image(p1, (1, 2, 3))
    _make_image(p2, (1, 2, 3))
    assert sha256_of_file(p1) == sha256_of_file(p2)


def test_inspect_dataset_report(tmp_path: Path):
    _make_fixture_dataset(tmp_path)
    report = inspect_dataset(tmp_path)
    assert report.total_images == 5
    assert report.num_classes == 2
    assert len(report.corrupt_files) == 1
    assert len(report.duplicate_content_groups) == 1


def test_discover_images_on_missing_root_returns_empty(tmp_path: Path):
    assert discover_images(tmp_path / "does_not_exist") == []
