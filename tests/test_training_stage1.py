"""Phase 04 tests: Stage 1 transfer-learning training loop.

Uses ``weights=None`` and tiny synthetic data/image sizes to keep the smoke
run fast and network-free; the ImageNet-weights contract itself is already
covered by ``tests/test_model_efficientnet.py``.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from ml.src.data.class_mapping import build_class_mapping, save_class_mapping
from ml.src.training.stage1 import Stage1TrainingConfig, run_stage1_training

IMAGE_SIZE = (32, 32)
CLASS_NAMES = ("ClassA", "ClassB", "ClassC")


def _make_image(path: Path, color: tuple[int, int, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    array = np.full((16, 16, 3), color, dtype=np.uint8)
    Image.fromarray(array).save(path)


def _write_manifest(path: Path, entries: list[dict]) -> Path:
    path.write_text(json.dumps(entries), encoding="utf-8")
    return path


@pytest.fixture
def training_setup(tmp_path: Path):
    dataset_root = tmp_path / "dataset"
    colors = {"ClassA": (200, 0, 0), "ClassB": (0, 200, 0), "ClassC": (0, 0, 200)}

    train_entries, val_entries, test_entries = [], [], []
    for class_name in CLASS_NAMES:
        for split, entries, n in (("train", train_entries, 4), ("val", val_entries, 2), ("test", test_entries, 2)):
            for i in range(n):
                rel_path = f"{class_name}/{split}_{i}.png"
                _make_image(dataset_root / rel_path, colors[class_name])
                entries.append({"path": rel_path, "class": class_name})

    train_manifest = _write_manifest(tmp_path / "train.json", train_entries)
    val_manifest = _write_manifest(tmp_path / "val.json", val_entries)
    test_manifest = _write_manifest(tmp_path / "test.json", test_entries)

    class_mapping_path = tmp_path / "class_mapping.json"
    save_class_mapping(build_class_mapping(CLASS_NAMES), class_mapping_path)

    return {
        "dataset_root": dataset_root,
        "train_manifest": train_manifest,
        "val_manifest": val_manifest,
        "test_manifest": test_manifest,
        "class_mapping_path": class_mapping_path,
        "artifacts_dir": tmp_path / "artifacts",
    }


def _make_config(setup: dict, **overrides) -> Stage1TrainingConfig:
    defaults = dict(
        train_manifest=setup["train_manifest"],
        val_manifest=setup["val_manifest"],
        dataset_root=setup["dataset_root"],
        class_mapping_path=setup["class_mapping_path"],
        artifacts_dir=setup["artifacts_dir"],
        image_size=IMAGE_SIZE,
        batch_size=4,
        epochs=1,
        early_stopping_patience=1,
        weights=None,
    )
    defaults.update(overrides)
    return Stage1TrainingConfig(**defaults)


def test_stage1_training_completes_and_freezes_backbone(training_setup):
    result = run_stage1_training(_make_config(training_setup))

    backbone = result.model.get_layer("efficientnetb0")
    assert backbone.trainable is False
    assert all(not layer.trainable for layer in backbone.layers)
    assert result.model.get_layer("predictions").trainable is True


def test_stage1_training_saves_best_checkpoint(training_setup):
    result = run_stage1_training(_make_config(training_setup))
    assert result.checkpoint_path.is_file()


def test_stage1_training_saves_history_and_config(training_setup):
    result = run_stage1_training(_make_config(training_setup))

    assert result.history_path.is_file()
    history = json.loads(result.history_path.read_text(encoding="utf-8"))
    assert "loss" in history
    assert "val_loss" in history
    assert len(history["loss"]) == 1

    assert result.config_path.is_file()
    config_record = json.loads(result.config_path.read_text(encoding="utf-8"))
    assert config_record["backbone_frozen"] is True
    assert "efficientnetb0" not in config_record["trainable_layers"]
    assert config_record["seed"] == 42
    assert config_record["num_train_samples"] == 12
    assert config_record["num_val_samples"] == 6


def test_stage1_training_uses_separate_train_and_val_data(training_setup):
    result = run_stage1_training(_make_config(training_setup))
    assert result.num_train_samples == 12
    assert result.num_val_samples == 6


def test_stage1_training_never_touches_test_manifest(training_setup, monkeypatch):
    original_load = Path.read_text
    accessed_paths: list[str] = []

    def spy_read_text(self, *args, **kwargs):
        accessed_paths.append(str(self))
        return original_load(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", spy_read_text)

    run_stage1_training(_make_config(training_setup))

    test_manifest_str = str(training_setup["test_manifest"])
    assert not any(p == test_manifest_str for p in accessed_paths)


def test_stage1_training_respects_sample_limits(training_setup):
    result = run_stage1_training(_make_config(training_setup, train_limit=6, val_limit=3))
    assert result.num_train_samples == 6
    assert result.num_val_samples == 3
