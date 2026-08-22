"""Phase 06 final evaluation: Stage 2 checkpoint on the untouched test split.

Loads ``ml/artifacts/stage2/best_model.keras`` (or a given checkpoint) and
runs inference over every image in a test manifest using the same
resize-only preprocessing the Stage 1/2 training pipeline applies to
val/test splits (``ml/src/training/dataset.py`` -> ``ml/src/preprocessing
/augmentation.py``'s ``get_transform``, which is a no-op augmentation for
any split other than "train" and calls the shared
``ml/src/preprocessing/image.py`` decode/resize used by inference too),
per ML_SPEC.md "Leakage Rules" and PHASE_06_EVALUATION.md. This module only
predicts and measures -- it never calls ``model.fit`` or mutates weights.

Also provides ``analyze_generalization``/``render_overfitting_report`` to
compare Stage 1/2 training histories against the final test performance,
per PHASE_06_EVALUATION.md requirements 7-9.
"""

from __future__ import annotations

import json
import platform
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_recall_fscore_support,
)
from tensorflow import keras

from ml.src.data.splits import load_split_manifest
from ml.src.models.efficientnet import DEFAULT_IMAGE_SIZE, load_model
from ml.src.training.dataset import build_dataset

DEFAULT_MODEL_PATH = Path("ml/artifacts/stage2/best_model.keras")
DEFAULT_ARTIFACTS_DIR = Path("ml/artifacts/evaluation")

METRICS_FILENAME = "metrics.json"
PER_CLASS_METRICS_FILENAME = "per_class_metrics.json"
CLASSIFICATION_REPORT_FILENAME = "classification_report.txt"
CONFUSION_MATRIX_JSON_FILENAME = "confusion_matrix.json"
CONFUSION_MATRIX_IMAGE_FILENAME = "confusion_matrix.png"
PREDICTIONS_FILENAME = "predictions.json"
CONFIG_FILENAME = "config.json"
OVERFITTING_REPORT_FILENAME = "overfitting_analysis.md"

AVERAGING_STRATEGY_NOTE = (
    "Overall precision/recall/F1 are reported two ways: 'macro' (unweighted "
    "mean across all classes -- every class counts equally regardless of "
    "how many test images it has) and 'weighted' (mean weighted by each "
    "class's test support -- tracks overall accuracy more closely). "
    "Per-class precision/recall/F1/support come from sklearn's "
    "precision_recall_fscore_support(..., average=None), one value per "
    "class with no averaging."
)


@dataclass(frozen=True)
class EvaluationConfig:
    test_manifest: Path
    dataset_root: Path
    class_mapping_path: Path
    model_path: Path = DEFAULT_MODEL_PATH
    artifacts_dir: Path = DEFAULT_ARTIFACTS_DIR
    image_size: tuple[int, int] = DEFAULT_IMAGE_SIZE
    batch_size: int = 32
    limit: int | None = None


@dataclass
class EvaluationResult:
    num_samples: int
    num_classes: int
    accuracy: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    weighted_precision: float
    weighted_recall: float
    weighted_f1: float
    metrics_path: Path
    per_class_metrics_path: Path
    classification_report_path: Path
    confusion_matrix_json_path: Path
    confusion_matrix_image_path: Path
    predictions_path: Path
    config_path: Path


def _save_confusion_matrix_image(cm: np.ndarray, class_names: list[str], path: Path) -> None:
    n = len(class_names)
    side = max(8.0, n * 0.35)
    fig, ax = plt.subplots(figsize=(side, side))
    im = ax.imshow(cm, cmap="Blues")
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(class_names, rotation=90, fontsize=6)
    ax.set_yticklabels(class_names, fontsize=6)
    ax.set_xlabel("Predicted class")
    ax.set_ylabel("True class")
    ax.set_title("Stage 2 test-set confusion matrix")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run_evaluation(config: EvaluationConfig) -> EvaluationResult:
    """Predict on every image in ``config.test_manifest`` and save metrics.

    Read-only with respect to the model: only ``model.predict`` is called,
    never ``model.fit``, so evaluation cannot modify weights.
    """
    class_mapping: dict[str, int] = json.loads(
        Path(config.class_mapping_path).read_text(encoding="utf-8")
    )
    num_classes = len(class_mapping)
    index_to_class = {idx: name for name, idx in class_mapping.items()}
    class_names_by_index = [index_to_class[i] for i in range(num_classes)]

    model = load_model(config.model_path)
    if model.output_shape[-1] != num_classes:
        raise ValueError(
            f"Model {config.model_path} has {model.output_shape[-1]} output classes, "
            f"but class mapping {config.class_mapping_path} has {num_classes}"
        )

    entries = load_split_manifest(Path(config.test_manifest))
    if config.limit is not None:
        entries = entries[: config.limit]

    test_ds, num_samples = build_dataset(
        manifest_path=config.test_manifest,
        dataset_root=config.dataset_root,
        class_mapping=class_mapping,
        split="test",
        image_size=config.image_size,
        batch_size=config.batch_size,
        shuffle=False,
        limit=config.limit,
    )
    if num_samples != len(entries):
        raise ValueError(
            f"Dataset produced {num_samples} samples but manifest has {len(entries)} entries"
        )

    probabilities = model.predict(test_ds, verbose=0)
    predicted_labels = np.argmax(probabilities, axis=1)
    confidences = np.max(probabilities, axis=1)
    true_labels = np.array([class_mapping[entry["class"]] for entry in entries])

    label_indices = list(range(num_classes))

    accuracy = float(np.mean(predicted_labels == true_labels))
    macro_p, macro_r, macro_f1, _ = precision_recall_fscore_support(
        true_labels, predicted_labels, labels=label_indices, average="macro", zero_division=0
    )
    weighted_p, weighted_r, weighted_f1, _ = precision_recall_fscore_support(
        true_labels, predicted_labels, labels=label_indices, average="weighted", zero_division=0
    )
    per_class_p, per_class_r, per_class_f1, per_class_support = precision_recall_fscore_support(
        true_labels, predicted_labels, labels=label_indices, average=None, zero_division=0
    )
    report_text = classification_report(
        true_labels,
        predicted_labels,
        labels=label_indices,
        target_names=class_names_by_index,
        zero_division=0,
    )
    cm = confusion_matrix(true_labels, predicted_labels, labels=label_indices)

    artifacts_dir = Path(config.artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    config_record = {
        "model_path": str(config.model_path),
        "test_manifest": str(config.test_manifest),
        "dataset_root": str(config.dataset_root),
        "class_mapping_path": str(config.class_mapping_path),
        "image_size": list(config.image_size),
        "batch_size": config.batch_size,
        "limit": config.limit,
        "num_classes": num_classes,
        "num_test_samples": int(num_samples),
        "tensorflow_version": tf.__version__,
        "keras_version": keras.__version__,
        "python_version": platform.python_version(),
    }
    config_path = artifacts_dir / CONFIG_FILENAME
    config_path.write_text(json.dumps(config_record, indent=2) + "\n", encoding="utf-8")

    metrics_record = {
        "num_samples": int(num_samples),
        "num_classes": num_classes,
        "accuracy": accuracy,
        "averaging_strategy": AVERAGING_STRATEGY_NOTE,
        "macro": {"precision": float(macro_p), "recall": float(macro_r), "f1": float(macro_f1)},
        "weighted": {
            "precision": float(weighted_p),
            "recall": float(weighted_r),
            "f1": float(weighted_f1),
        },
        "config_path": str(config_path),
    }
    metrics_path = artifacts_dir / METRICS_FILENAME
    metrics_path.write_text(json.dumps(metrics_record, indent=2) + "\n", encoding="utf-8")

    per_class_record = {
        class_names_by_index[i]: {
            "precision": float(per_class_p[i]),
            "recall": float(per_class_r[i]),
            "f1": float(per_class_f1[i]),
            "support": int(per_class_support[i]),
        }
        for i in range(num_classes)
    }
    per_class_metrics_path = artifacts_dir / PER_CLASS_METRICS_FILENAME
    per_class_metrics_path.write_text(
        json.dumps(per_class_record, indent=2) + "\n", encoding="utf-8"
    )

    classification_report_path = artifacts_dir / CLASSIFICATION_REPORT_FILENAME
    classification_report_path.write_text(report_text, encoding="utf-8")

    confusion_matrix_json_path = artifacts_dir / CONFUSION_MATRIX_JSON_FILENAME
    confusion_matrix_json_path.write_text(
        json.dumps({"labels": class_names_by_index, "matrix": cm.tolist()}, indent=2) + "\n",
        encoding="utf-8",
    )

    confusion_matrix_image_path = artifacts_dir / CONFUSION_MATRIX_IMAGE_FILENAME
    _save_confusion_matrix_image(cm, class_names_by_index, confusion_matrix_image_path)

    predictions = [
        {
            "path": entries[i]["path"],
            "true_class": entries[i]["class"],
            "predicted_class": class_names_by_index[int(predicted_labels[i])],
            "confidence": float(confidences[i]),
            "correct": bool(predicted_labels[i] == true_labels[i]),
        }
        for i in range(num_samples)
    ]
    predictions_path = artifacts_dir / PREDICTIONS_FILENAME
    predictions_path.write_text(json.dumps(predictions, indent=2) + "\n", encoding="utf-8")

    return EvaluationResult(
        num_samples=int(num_samples),
        num_classes=num_classes,
        accuracy=accuracy,
        macro_precision=float(macro_p),
        macro_recall=float(macro_r),
        macro_f1=float(macro_f1),
        weighted_precision=float(weighted_p),
        weighted_recall=float(weighted_r),
        weighted_f1=float(weighted_f1),
        metrics_path=metrics_path,
        per_class_metrics_path=per_class_metrics_path,
        classification_report_path=classification_report_path,
        confusion_matrix_json_path=confusion_matrix_json_path,
        confusion_matrix_image_path=confusion_matrix_image_path,
        predictions_path=predictions_path,
        config_path=config_path,
    )


@dataclass(frozen=True)
class EpochSnapshot:
    epoch: int
    train_accuracy: float
    val_accuracy: float
    train_loss: float
    val_loss: float


def _best_epoch_snapshot(history: dict) -> EpochSnapshot:
    """Snapshot the epoch ModelCheckpoint(monitor="val_accuracy") would have
    saved -- i.e. the epoch of maximum val_accuracy, matching how
    ``run_stage1_training``/``run_stage2_training`` pick ``best_model.keras``.
    """
    val_accuracy = history["val_accuracy"]
    idx = int(np.argmax(val_accuracy))
    return EpochSnapshot(
        epoch=idx + 1,
        train_accuracy=float(history["accuracy"][idx]),
        val_accuracy=float(history["val_accuracy"][idx]),
        train_loss=float(history["loss"][idx]),
        val_loss=float(history["val_loss"][idx]),
    )


@dataclass(frozen=True)
class GeneralizationAnalysis:
    stage1_best: EpochSnapshot
    stage2_best: EpochSnapshot
    test_accuracy: float
    test_macro_f1: float
    test_weighted_f1: float
    stage2_train_val_gap: float
    val_test_gap: float


def analyze_generalization(
    stage1_history: dict,
    stage2_history: dict,
    test_accuracy: float,
    test_macro_f1: float,
    test_weighted_f1: float,
) -> GeneralizationAnalysis:
    """Compare Stage 1/2 best-checkpoint train/val accuracy against the
    final test accuracy, per PHASE_06_EVALUATION.md requirements 7-8.
    """
    stage1_best = _best_epoch_snapshot(stage1_history)
    stage2_best = _best_epoch_snapshot(stage2_history)
    return GeneralizationAnalysis(
        stage1_best=stage1_best,
        stage2_best=stage2_best,
        test_accuracy=test_accuracy,
        test_macro_f1=test_macro_f1,
        test_weighted_f1=test_weighted_f1,
        stage2_train_val_gap=stage2_best.train_accuracy - stage2_best.val_accuracy,
        val_test_gap=stage2_best.val_accuracy - test_accuracy,
    )


def render_overfitting_report(analysis: GeneralizationAnalysis) -> str:
    lines = [
        "# PlantCare AI -- Validation vs. Test & Overfitting Analysis (Phase 06)",
        "",
        "## Best-checkpoint epoch summary",
        "",
        "Epoch selected is the one `ModelCheckpoint(monitor=\"val_accuracy\")` "
        "saved as `best_model.keras` for that stage.",
        "",
        "| Stage | Epoch | Train accuracy | Val accuracy | Train loss | Val loss |",
        "|---|---|---|---|---|---|",
        f"| Stage 1 | {analysis.stage1_best.epoch} | {analysis.stage1_best.train_accuracy:.4f} | "
        f"{analysis.stage1_best.val_accuracy:.4f} | {analysis.stage1_best.train_loss:.4f} | "
        f"{analysis.stage1_best.val_loss:.4f} |",
        f"| Stage 2 | {analysis.stage2_best.epoch} | {analysis.stage2_best.train_accuracy:.4f} | "
        f"{analysis.stage2_best.val_accuracy:.4f} | {analysis.stage2_best.train_loss:.4f} | "
        f"{analysis.stage2_best.val_loss:.4f} |",
        "",
        "## Final test-set performance (Stage 2 checkpoint, 8,147 test images)",
        "",
        f"- Test accuracy: {analysis.test_accuracy:.4f}",
        f"- Test macro F1: {analysis.test_macro_f1:.4f}",
        f"- Test weighted F1: {analysis.test_weighted_f1:.4f}",
        "",
        "## Gaps",
        "",
        f"- Stage 2 train accuracy minus val accuracy (at best checkpoint): "
        f"{analysis.stage2_train_val_gap:+.4f}",
        f"- Stage 2 val accuracy minus test accuracy: {analysis.val_test_gap:+.4f}",
        "",
        "As a rough rule of thumb, gaps beyond roughly 2-3 percentage points are "
        "worth investigating further; this is a heuristic for where to look, not "
        "a pass/fail rule.",
        "",
    ]
    if analysis.stage2_train_val_gap > 0.03 or analysis.val_test_gap > 0.02:
        lines.append(
            "Interpretation: the gap(s) above are large enough to be worth watching. "
            "Possible future fixes (to be applied in a future training phase, never by "
            "modifying this evaluated checkpoint): stronger regularization or "
            "augmentation, earlier stopping, a lower fine-tuning learning rate, or "
            "unfreezing less of the backbone."
        )
    else:
        lines.append(
            "Interpretation: the train/val and val/test gaps are small, consistent with "
            "the model generalizing from validation to the held-out test set rather than "
            "overfitting to the training or validation data."
        )
    return "\n".join(lines) + "\n"


def write_overfitting_report(analysis: GeneralizationAnalysis, path: Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_overfitting_report(analysis), encoding="utf-8")
    return path
