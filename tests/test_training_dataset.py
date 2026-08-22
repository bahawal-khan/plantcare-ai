"""Phase 04 tests: tf.data pipeline built from split manifests."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import tensorflow as tf
from PIL import Image

from ml.src.training.dataset import build_dataset, load_manifest_records

CLASS_MAPPING = {"ClassA": 0, "ClassB": 1}


def _make_image(path: Path, color: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    array = np.full((16, 16, 3), color, dtype=np.uint8)
    Image.fromarray(array).save(path)


@pytest.fixture
def dataset_root(tmp_path: Path) -> Path:
    root = tmp_path / "dataset"
    for i in range(4):
        _make_image(root / "ClassA" / f"a_{i}.png", (200, 0, 0))
    for i in range(4):
        _make_image(root / "ClassB" / f"b_{i}.png", (0, 0, 200))
    return root


@pytest.fixture
def manifest_path(tmp_path: Path, dataset_root: Path) -> Path:
    entries = [
        {"path": f"ClassA/a_{i}.png", "class": "ClassA"} for i in range(4)
    ] + [{"path": f"ClassB/b_{i}.png", "class": "ClassB"} for i in range(4)]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(entries), encoding="utf-8")
    return path


def test_load_manifest_records_resolves_paths_and_labels(manifest_path, dataset_root):
    paths, labels = load_manifest_records(manifest_path, dataset_root, CLASS_MAPPING)
    assert len(paths) == 8
    assert len(labels) == 8
    assert set(labels) == {0, 1}
    assert all(Path(p).is_file() for p in paths)


def test_load_manifest_records_respects_limit(manifest_path, dataset_root):
    paths, labels = load_manifest_records(manifest_path, dataset_root, CLASS_MAPPING, limit=3)
    assert len(paths) == 3
    assert len(labels) == 3


def test_build_dataset_produces_correctly_shaped_batches(manifest_path, dataset_root):
    ds, num_samples = build_dataset(
        manifest_path=manifest_path,
        dataset_root=dataset_root,
        class_mapping=CLASS_MAPPING,
        split="val",
        image_size=(32, 32),
        batch_size=4,
        shuffle=False,
    )
    assert num_samples == 8
    images, labels = next(iter(ds))
    assert images.shape == (4, 32, 32, 3)
    assert images.dtype == tf.float32
    assert labels.dtype == tf.int64
    assert float(tf.reduce_min(images)) >= 0.0
    assert float(tf.reduce_max(images)) <= 1.0


def test_build_dataset_val_split_is_deterministic_across_epochs(manifest_path, dataset_root):
    ds, _ = build_dataset(
        manifest_path=manifest_path,
        dataset_root=dataset_root,
        class_mapping=CLASS_MAPPING,
        split="val",
        image_size=(32, 32),
        batch_size=8,
        shuffle=False,
    )
    images_epoch1, _ = next(iter(ds))
    images_epoch2, _ = next(iter(ds))
    assert np.array_equal(images_epoch1.numpy(), images_epoch2.numpy())


def test_build_dataset_empty_manifest_raises(tmp_path, dataset_root):
    empty_manifest = tmp_path / "empty.json"
    empty_manifest.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError):
        build_dataset(
            manifest_path=empty_manifest,
            dataset_root=dataset_root,
            class_mapping=CLASS_MAPPING,
            split="train",
        )
