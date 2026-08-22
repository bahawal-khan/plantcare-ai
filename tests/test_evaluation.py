"""Phase 06 tests: final test-set evaluation.

Uses ``weights=None`` and tiny synthetic data/image sizes to keep the smoke
run fast and network-free, mirroring ``tests/test_training_stage1.py`` /
``tests/test_training_stage2.py``. Never runs against the real 8,147-image
test set -- that only happens in the one real evaluation run.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from ml.src.data.class_mapping import build_class_mapping, save_class_mapping
from ml.src.evaluation.evaluate import (
    EvaluationConfig,
    GeneralizationAnalysis,
    analyze_generalization,
    render_overfitting_report,
    run_evaluation,
    write_overfitting_report,
)
from ml.src.models.efficientnet import build_model, save_model

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
def evaluation_setup(tmp_path: Path):
    dataset_root = tmp_path / "dataset"
    colors = {"ClassA": (200, 0, 0), "ClassB": (0, 200, 0), "ClassC": (0, 0, 200)}

    test_entries: list[dict] = []
    for class_name in CLASS_NAMES:
        for i in range(3):
            rel_path = f"{class_name}/test_{i}.png"
            _make_image(dataset_root / rel_path, colors[class_name])
            test_entries.append({"path": rel_path, "class": class_name})

    test_manifest = _write_manifest(tmp_path / "test.json", test_entries)

    class_mapping_path = tmp_path / "class_mapping.json"
    class_mapping = build_class_mapping(CLASS_NAMES)
    save_class_mapping(class_mapping, class_mapping_path)

    model = build_model(len(CLASS_NAMES), image_size=IMAGE_SIZE, weights=None, freeze_backbone=True)
    model_path = save_model(model, tmp_path / "model" / "best_model.keras")

    return {
        "dataset_root": dataset_root,
        "test_manifest": test_manifest,
        "class_mapping_path": class_mapping_path,
        "model_path": model_path,
        "artifacts_dir": tmp_path / "artifacts" / "evaluation",
    }


def _make_config(setup: dict, **overrides) -> EvaluationConfig:
    defaults = dict(
        test_manifest=setup["test_manifest"],
        dataset_root=setup["dataset_root"],
        class_mapping_path=setup["class_mapping_path"],
        model_path=setup["model_path"],
        artifacts_dir=setup["artifacts_dir"],
        image_size=IMAGE_SIZE,
        batch_size=4,
    )
    defaults.update(overrides)
    return EvaluationConfig(**defaults)


def test_evaluation_predicts_every_test_image(evaluation_setup):
    result = run_evaluation(_make_config(evaluation_setup))
    assert result.num_samples == 9
    assert result.num_classes == 3


def test_evaluation_does_not_modify_model_weights(evaluation_setup):
    from ml.src.models.efficientnet import load_model

    before = [w.copy() for w in load_model(evaluation_setup["model_path"]).get_weights()]
    run_evaluation(_make_config(evaluation_setup))
    after = load_model(evaluation_setup["model_path"]).get_weights()

    assert len(before) == len(after)
    for b, a in zip(before, after):
        np.testing.assert_array_equal(b, a)


def test_evaluation_saves_all_required_artifacts(evaluation_setup):
    result = run_evaluation(_make_config(evaluation_setup))

    for path in (
        result.metrics_path,
        result.per_class_metrics_path,
        result.classification_report_path,
        result.confusion_matrix_json_path,
        result.confusion_matrix_image_path,
        result.predictions_path,
        result.config_path,
    ):
        assert path.is_file(), f"missing artifact: {path}"


def test_evaluation_metrics_include_overall_and_averaging_strategy(evaluation_setup):
    result = run_evaluation(_make_config(evaluation_setup))
    metrics = json.loads(result.metrics_path.read_text(encoding="utf-8"))

    assert metrics["num_samples"] == 9
    assert 0.0 <= metrics["accuracy"] <= 1.0
    assert "macro" in metrics and "weighted" in metrics
    for group in ("macro", "weighted"):
        for key in ("precision", "recall", "f1"):
            assert 0.0 <= metrics[group][key] <= 1.0
    assert "averaging_strategy" in metrics and metrics["averaging_strategy"]


def test_evaluation_per_class_metrics_cover_every_class(evaluation_setup):
    result = run_evaluation(_make_config(evaluation_setup))
    per_class = json.loads(result.per_class_metrics_path.read_text(encoding="utf-8"))

    assert set(per_class.keys()) == set(CLASS_NAMES)
    for class_name in CLASS_NAMES:
        entry = per_class[class_name]
        assert entry["support"] == 3
        for key in ("precision", "recall", "f1"):
            assert 0.0 <= entry[key] <= 1.0


def test_evaluation_confusion_matrix_shape_matches_class_count(evaluation_setup):
    result = run_evaluation(_make_config(evaluation_setup))
    cm_record = json.loads(result.confusion_matrix_json_path.read_text(encoding="utf-8"))

    assert cm_record["labels"] == list(CLASS_NAMES)
    matrix = cm_record["matrix"]
    assert len(matrix) == 3
    assert all(len(row) == 3 for row in matrix)
    assert sum(sum(row) for row in matrix) == 9


def test_evaluation_predictions_have_true_predicted_and_confidence(evaluation_setup):
    result = run_evaluation(_make_config(evaluation_setup))
    predictions = json.loads(result.predictions_path.read_text(encoding="utf-8"))

    assert len(predictions) == 9
    seen_paths = set()
    for record in predictions:
        assert record["true_class"] in CLASS_NAMES
        assert record["predicted_class"] in CLASS_NAMES
        assert 0.0 <= record["confidence"] <= 1.0
        assert isinstance(record["correct"], bool)
        seen_paths.add(record["path"])
    assert len(seen_paths) == 9


def test_evaluation_respects_sample_limit(evaluation_setup):
    result = run_evaluation(_make_config(evaluation_setup, limit=4))
    assert result.num_samples == 4
    predictions = json.loads(result.predictions_path.read_text(encoding="utf-8"))
    assert len(predictions) == 4


def test_evaluation_rejects_class_count_mismatch(evaluation_setup, tmp_path):
    mismatched_mapping_path = tmp_path / "mismatched_class_mapping.json"
    save_class_mapping(build_class_mapping(("OnlyOneClass",)), mismatched_mapping_path)

    with pytest.raises(ValueError):
        run_evaluation(
            _make_config(evaluation_setup, class_mapping_path=mismatched_mapping_path)
        )


def _history(accuracy: list[float], val_accuracy: list[float]) -> dict:
    return {
        "accuracy": accuracy,
        "val_accuracy": val_accuracy,
        "loss": [1.0 / (i + 1) for i in range(len(accuracy))],
        "val_loss": [1.0 / (i + 1) for i in range(len(val_accuracy))],
    }


def test_analyze_generalization_picks_best_val_accuracy_epoch():
    stage1_history = _history(accuracy=[0.5, 0.7, 0.8], val_accuracy=[0.4, 0.6, 0.55])
    stage2_history = _history(accuracy=[0.9, 0.95, 0.99], val_accuracy=[0.85, 0.9, 0.88])

    analysis = analyze_generalization(
        stage1_history=stage1_history,
        stage2_history=stage2_history,
        test_accuracy=0.87,
        test_macro_f1=0.86,
        test_weighted_f1=0.87,
    )

    # Stage 1 best val_accuracy is epoch 2 (index 1, 0-indexed) -> 0.6
    assert analysis.stage1_best.epoch == 2
    assert analysis.stage1_best.val_accuracy == pytest.approx(0.6)
    # Stage 2 best val_accuracy is epoch 2 (index 1) -> 0.9, train accuracy 0.95
    assert analysis.stage2_best.epoch == 2
    assert analysis.stage2_best.val_accuracy == pytest.approx(0.9)
    assert analysis.stage2_best.train_accuracy == pytest.approx(0.95)
    assert analysis.stage2_train_val_gap == pytest.approx(0.95 - 0.9)
    assert analysis.val_test_gap == pytest.approx(0.9 - 0.87)


def test_render_overfitting_report_includes_key_numbers():
    analysis = GeneralizationAnalysis(
        stage1_best=analyze_generalization(
            _history([0.8], [0.7]), _history([0.9], [0.85]), 0.83, 0.82, 0.83
        ).stage1_best,
        stage2_best=analyze_generalization(
            _history([0.8], [0.7]), _history([0.9], [0.85]), 0.83, 0.82, 0.83
        ).stage2_best,
        test_accuracy=0.83,
        test_macro_f1=0.82,
        test_weighted_f1=0.83,
        stage2_train_val_gap=0.05,
        val_test_gap=0.02,
    )
    report = render_overfitting_report(analysis)

    assert "Stage 1" in report
    assert "Stage 2" in report
    assert "0.8300" in report  # test accuracy
    assert "Interpretation" in report


def test_write_overfitting_report_saves_file(tmp_path):
    analysis = analyze_generalization(
        _history([0.8, 0.85], [0.7, 0.75]),
        _history([0.9, 0.95], [0.85, 0.9]),
        test_accuracy=0.88,
        test_macro_f1=0.87,
        test_weighted_f1=0.88,
    )
    out_path = tmp_path / "overfitting_analysis.md"
    written = write_overfitting_report(analysis, out_path)

    assert written == out_path
    assert out_path.is_file()
    assert "0.8800" in out_path.read_text(encoding="utf-8")
