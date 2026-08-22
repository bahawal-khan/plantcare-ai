"""Stage 1 transfer-learning training loop.

Trains only the classification head on top of the frozen, ImageNet-pretrained
EfficientNetB0 backbone (``ml/src/models/efficientnet.py``, ``build_model``
with ``freeze_backbone=True``), per ML_SPEC.md "Stage 1 — Transfer Learning"
and PHASE_04_TRANSFER_LEARNING.md. Only the train and val manifests are ever
read here — the test split must stay untouched until Phase 06 evaluation.
"""

from __future__ import annotations

import json
import platform
from dataclasses import dataclass
from pathlib import Path

import tensorflow as tf
from tensorflow import keras

from ml.src.models.efficientnet import ClassificationHeadConfig, DEFAULT_IMAGE_SIZE, build_model
from ml.src.preprocessing.augmentation import AugmentationConfig, DEFAULT_AUGMENTATION_CONFIG
from ml.src.training.dataset import build_dataset

DEFAULT_ARTIFACTS_DIR = Path("ml/artifacts/stage1")
CHECKPOINT_FILENAME = "best_model.keras"
HISTORY_FILENAME = "history.json"
CONFIG_FILENAME = "config.json"


@dataclass(frozen=True)
class Stage1TrainingConfig:
    train_manifest: Path
    val_manifest: Path
    dataset_root: Path
    class_mapping_path: Path
    artifacts_dir: Path = DEFAULT_ARTIFACTS_DIR
    seed: int = 42
    image_size: tuple[int, int] = DEFAULT_IMAGE_SIZE
    batch_size: int = 32
    epochs: int = 20
    learning_rate: float = 1e-3
    dropout_rate: float = 0.3
    dense_units: int | None = None
    early_stopping_patience: int = 5
    train_limit: int | None = None
    val_limit: int | None = None
    augmentation: AugmentationConfig = DEFAULT_AUGMENTATION_CONFIG
    weights: str | None = "imagenet"


@dataclass
class Stage1TrainingResult:
    model: keras.Model
    history: dict
    checkpoint_path: Path
    config_path: Path
    history_path: Path
    num_classes: int
    num_train_samples: int
    num_val_samples: int


def run_stage1_training(config: Stage1TrainingConfig) -> Stage1TrainingResult:
    keras.utils.set_random_seed(config.seed)

    class_mapping: dict[str, int] = json.loads(
        Path(config.class_mapping_path).read_text(encoding="utf-8")
    )
    num_classes = len(class_mapping)

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

    head_config = ClassificationHeadConfig(
        dropout_rate=config.dropout_rate, dense_units=config.dense_units
    )
    model = build_model(
        num_classes=num_classes,
        image_size=config.image_size,
        head_config=head_config,
        freeze_backbone=True,
        weights=config.weights,
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

    record = {
        "stage": 1,
        "seed": config.seed,
        "image_size": list(config.image_size),
        "batch_size": config.batch_size,
        "epochs_configured": config.epochs,
        "epochs_ran": len(history.epoch),
        "learning_rate": config.learning_rate,
        "dropout_rate": config.dropout_rate,
        "dense_units": config.dense_units,
        "early_stopping_patience": config.early_stopping_patience,
        "num_classes": num_classes,
        "num_train_samples": num_train_samples,
        "num_val_samples": num_val_samples,
        "backbone_frozen": not backbone.trainable,
        "trainable_layers": trainable_layer_names,
        "train_manifest": str(config.train_manifest),
        "val_manifest": str(config.val_manifest),
        "class_mapping_path": str(config.class_mapping_path),
        "tensorflow_version": tf.__version__,
        "keras_version": keras.__version__,
        "python_version": platform.python_version(),
    }
    config_path = artifacts_dir / CONFIG_FILENAME
    config_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    return Stage1TrainingResult(
        model=model,
        history=history.history,
        checkpoint_path=checkpoint_path,
        config_path=config_path,
        history_path=history_path,
        num_classes=num_classes,
        num_train_samples=num_train_samples,
        num_val_samples=num_val_samples,
    )
