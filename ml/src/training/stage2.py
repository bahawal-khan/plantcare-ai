"""Stage 2 fine-tuning training loop.

Loads the best Stage 1 checkpoint (``ml/src/training/stage1.py``), unfreezes
a controlled upper portion of the EfficientNetB0 backbone
(``ml/src/models/efficientnet.py``'s ``unfreeze_top_layers``), and continues
training at a substantially lower learning rate, per ML_SPEC.md
"Stage 2 — Fine-Tuning" and PHASE_05_FINE_TUNING.md. Only the train and val
manifests are ever read here — the test split must stay untouched until
Phase 06 evaluation.
"""

from __future__ import annotations

import json
import platform
from dataclasses import dataclass
from pathlib import Path

import tensorflow as tf
from tensorflow import keras

from ml.src.models.efficientnet import DEFAULT_IMAGE_SIZE, load_model, unfreeze_top_layers
from ml.src.preprocessing.augmentation import AugmentationConfig, DEFAULT_AUGMENTATION_CONFIG
from ml.src.training.dataset import build_dataset

DEFAULT_ARTIFACTS_DIR = Path("ml/artifacts/stage2")
DEFAULT_STAGE1_CHECKPOINT = Path("ml/artifacts/stage1/best_model.keras")
DEFAULT_UNFREEZE_FROM = "block6a"
CHECKPOINT_FILENAME = "best_model.keras"
HISTORY_FILENAME = "history.json"
CONFIG_FILENAME = "config.json"


@dataclass(frozen=True)
class Stage2TrainingConfig:
    train_manifest: Path
    val_manifest: Path
    dataset_root: Path
    class_mapping_path: Path
    stage1_checkpoint_path: Path = DEFAULT_STAGE1_CHECKPOINT
    artifacts_dir: Path = DEFAULT_ARTIFACTS_DIR
    seed: int = 42
    image_size: tuple[int, int] = DEFAULT_IMAGE_SIZE
    batch_size: int = 32
    epochs: int = 10
    learning_rate: float = 1e-5
    unfreeze_from: str = DEFAULT_UNFREEZE_FROM
    freeze_batchnorm: bool = True
    early_stopping_patience: int = 5
    train_limit: int | None = None
    val_limit: int | None = None
    augmentation: AugmentationConfig = DEFAULT_AUGMENTATION_CONFIG


@dataclass
class Stage2TrainingResult:
    model: keras.Model
    history: dict
    checkpoint_path: Path
    config_path: Path
    history_path: Path
    num_classes: int
    num_train_samples: int
    num_val_samples: int


def _stage1_learning_rate(stage1_checkpoint_path: Path) -> float | None:
    """Best-effort read of the Stage 1 learning rate from its config.json,
    to validate that fine-tuning uses a lower rate. Returns None if the
    Stage 1 config record is not found, so callers can skip the check
    rather than fail on an unusual checkpoint layout.
    """
    stage1_config_path = Path(stage1_checkpoint_path).parent / CONFIG_FILENAME
    if not stage1_config_path.is_file():
        return None
    record = json.loads(stage1_config_path.read_text(encoding="utf-8"))
    return record.get("learning_rate")


def run_stage2_training(config: Stage2TrainingConfig) -> Stage2TrainingResult:
    keras.utils.set_random_seed(config.seed)

    class_mapping: dict[str, int] = json.loads(
        Path(config.class_mapping_path).read_text(encoding="utf-8")
    )
    num_classes = len(class_mapping)

    stage1_learning_rate = _stage1_learning_rate(config.stage1_checkpoint_path)
    if stage1_learning_rate is not None and config.learning_rate >= stage1_learning_rate:
        raise ValueError(
            f"Stage 2 learning_rate ({config.learning_rate}) must be lower than the "
            f"Stage 1 learning_rate ({stage1_learning_rate}) recorded in "
            f"{Path(config.stage1_checkpoint_path).parent / CONFIG_FILENAME}"
        )

    model = load_model(config.stage1_checkpoint_path)
    if model.output_shape[-1] != num_classes:
        raise ValueError(
            f"Stage 1 checkpoint {config.stage1_checkpoint_path} has "
            f"{model.output_shape[-1]} output classes, but class mapping "
            f"{config.class_mapping_path} has {num_classes}"
        )

    train_ds, num_train_samples = build_dataset(
        manifest_path=config.train_manifest,
        dataset_root=config.dataset_root,
        class_mapping=class_mapping,
        split="train",
        image_size=config.image_size,
        batch_size=config.batch_size,
        seed=config.seed,
        shuffle=True,
        limit=config.train_limit,
        augmentation_config=config.augmentation,
    )
    val_ds, num_val_samples = build_dataset(
        manifest_path=config.val_manifest,
        dataset_root=config.dataset_root,
        class_mapping=class_mapping,
        split="val",
        image_size=config.image_size,
        batch_size=config.batch_size,
        seed=config.seed,
        shuffle=False,
        limit=config.val_limit,
    )

    unfreeze_top_layers(
        model,
        unfreeze_from=config.unfreeze_from,
        freeze_batchnorm=config.freeze_batchnorm,
    )
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=config.learning_rate),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    artifacts_dir = Path(config.artifacts_dir)
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    checkpoint_path = artifacts_dir / CHECKPOINT_FILENAME

    callbacks = [
        keras.callbacks.ModelCheckpoint(
            filepath=str(checkpoint_path),
            monitor="val_accuracy",
            mode="max",
            save_best_only=True,
        ),
        keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=config.early_stopping_patience,
            restore_best_weights=True,
        ),
    ]

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=config.epochs,
        callbacks=callbacks,
        shuffle=False,  # already shuffled by build_dataset's tf.data .shuffle()
    )

    history_path = artifacts_dir / HISTORY_FILENAME
    history_path.write_text(json.dumps(history.history, indent=2) + "\n", encoding="utf-8")

    backbone = model.get_layer("efficientnetb0")
    trainable_layer_names = [layer.name for layer in model.layers if layer.trainable]
    trainable_backbone_layers = [layer.name for layer in backbone.layers if layer.trainable]
    frozen_backbone_layers = [layer.name for layer in backbone.layers if not layer.trainable]

    record = {
        "stage": 2,
        "seed": config.seed,
        "image_size": list(config.image_size),
        "batch_size": config.batch_size,
        "epochs_configured": config.epochs,
        "epochs_ran": len(history.epoch),
        "learning_rate": config.learning_rate,
        "stage1_learning_rate": stage1_learning_rate,
        "unfreeze_from": config.unfreeze_from,
        "freeze_batchnorm": config.freeze_batchnorm,
        "early_stopping_patience": config.early_stopping_patience,
        "num_classes": num_classes,
        "num_train_samples": num_train_samples,
        "num_val_samples": num_val_samples,
        "backbone_trainable": backbone.trainable,
        "trainable_layers": trainable_layer_names,
        "trainable_backbone_layers": trainable_backbone_layers,
        "frozen_backbone_layers": frozen_backbone_layers,
        "stage1_checkpoint_path": str(config.stage1_checkpoint_path),
        "train_manifest": str(config.train_manifest),
        "val_manifest": str(config.val_manifest),
        "class_mapping_path": str(config.class_mapping_path),
        "tensorflow_version": tf.__version__,
        "keras_version": keras.__version__,
        "python_version": platform.python_version(),
    }
    config_path = artifacts_dir / CONFIG_FILENAME
    config_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    return Stage2TrainingResult(
        model=model,
        history=history.history,
        checkpoint_path=checkpoint_path,
        config_path=config_path,
        history_path=history_path,
        num_classes=num_classes,
        num_train_samples=num_train_samples,
        num_val_samples=num_val_samples,
    )
