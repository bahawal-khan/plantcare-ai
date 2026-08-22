"""EfficientNetB0 model construction.

Single source of truth for building the PlantCare AI classifier, per
ARCHITECTURE.md ("ML code never lives inside route functions") and
CLAUDE.md rule 8 (training code stays separate from FastAPI). Both the
Phase 04 training script and the Phase 08 inference service must build
the model through this module rather than reimplementing the graph.

Stage 1 (this phase): ImageNet-pretrained EfficientNetB0 backbone, frozen,
with a configurable classification head on top (``build_model`` with the
default ``freeze_backbone=True``). Unfreezing an upper portion for Stage 2
fine-tuning is implemented in Phase 05 per ML_SPEC.md and is out of scope
here.

Note on input range: ``ml/src/preprocessing/image.py`` normalizes decoded
images to float32 in ``[0, 1]`` (the shared contract used by both training
and inference, per CLAUDE.md rule 11). Keras' ``EfficientNetB0`` expects
raw ``[0, 255]`` pixel values and rescales/normalizes internally, so the
model graph built here starts with a ``Rescaling(255.0)`` layer to convert
from the pipeline's ``[0, 1]`` convention back to the range EfficientNet
expects, keeping both preprocessing stages consistent with each other.

Stage 2 (Phase 05): ``unfreeze_top_layers`` unfreezes a controlled upper
portion of an already-built backbone in place, for fine-tuning on top of
the Stage 1 checkpoint, per ML_SPEC.md "Stage 2 — Fine-Tuning".
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tensorflow import keras
from tensorflow.keras import layers

DEFAULT_IMAGE_SIZE = (224, 224)


@dataclass(frozen=True)
class ClassificationHeadConfig:
    """Configuration for the classification head placed on the backbone."""

    dropout_rate: float = 0.3
    dense_units: int | None = None
    dense_activation: str = "relu"

    def __post_init__(self) -> None:
        if not 0.0 <= self.dropout_rate < 1.0:
            raise ValueError(f"dropout_rate must be in [0, 1), got {self.dropout_rate}")
        if self.dense_units is not None and self.dense_units < 1:
            raise ValueError(f"dense_units must be >= 1, got {self.dense_units}")


DEFAULT_HEAD_CONFIG = ClassificationHeadConfig()


def build_efficientnet_backbone(
    image_size: tuple[int, int] = DEFAULT_IMAGE_SIZE,
    weights: str | None = "imagenet",
) -> keras.Model:
    """Return the EfficientNetB0 feature-extractor backbone (no top)."""
    return keras.applications.EfficientNetB0(
        include_top=False,
        weights=weights,
        input_shape=(*image_size, 3),
        pooling=None,
    )


def build_model(
    num_classes: int,
    image_size: tuple[int, int] = DEFAULT_IMAGE_SIZE,
    head_config: ClassificationHeadConfig = DEFAULT_HEAD_CONFIG,
    freeze_backbone: bool = True,
    weights: str | None = "imagenet",
) -> keras.Model:
    """Build the EfficientNetB0 classifier: backbone + classification head.

    ``freeze_backbone=True`` (the Stage 1 default) makes the entire
    pretrained backbone non-trainable so only the head is trained.
    """
    if num_classes < 1:
        raise ValueError(f"num_classes must be >= 1, got {num_classes}")

    backbone = build_efficientnet_backbone(image_size=image_size, weights=weights)
    backbone.trainable = not freeze_backbone

    inputs = keras.Input(shape=(*image_size, 3), name="image")
    x = layers.Rescaling(255.0, name="restore_pixel_range")(inputs)
    x = backbone(x, training=False if freeze_backbone else None)
    x = layers.GlobalAveragePooling2D(name="global_average_pooling")(x)
    if head_config.dense_units is not None:
        x = layers.Dense(
            head_config.dense_units,
            activation=head_config.dense_activation,
            name="head_dense",
        )(x)
    x = layers.Dropout(head_config.dropout_rate, name="head_dropout")(x)
    outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)

    return keras.Model(inputs=inputs, outputs=outputs, name="plantcare_efficientnetb0")


def unfreeze_top_layers(
    model: keras.Model,
    unfreeze_from: str,
    backbone_layer_name: str = "efficientnetb0",
    freeze_batchnorm: bool = True,
) -> keras.Model:
    """Unfreeze a controlled upper portion of the backbone, in place.

    Layers up to and excluding the first backbone layer whose name starts
    with ``unfreeze_from`` stay frozen, per ML_SPEC.md Stage 2 "keep lower
    feature layers frozen". ``BatchNormalization`` layers stay frozen even
    within the unfrozen portion when ``freeze_batchnorm`` is True (the
    default): their running statistics were collected over the full
    ImageNet pretraining run, and updating them from the much smaller
    fine-tuning batches would destabilize training. This is the fine-tuning
    practice documented in the official Keras transfer-learning guide.

    Mutates ``model`` (via the nested backbone layer's ``trainable`` flags)
    and returns it. The caller must recompile the model afterwards for the
    trainability change to take effect, per Keras semantics.
    """
    backbone = model.get_layer(backbone_layer_name)
    backbone.trainable = True

    reached_cutoff = False
    matched = False
    for layer in backbone.layers:
        if layer.name.startswith(unfreeze_from):
            reached_cutoff = True
            matched = True
        if not reached_cutoff:
            layer.trainable = False
        elif freeze_batchnorm and isinstance(layer, layers.BatchNormalization):
            layer.trainable = False
        else:
            layer.trainable = True

    if not matched:
        raise ValueError(
            f"No layer in backbone {backbone_layer_name!r} has a name starting with "
            f"{unfreeze_from!r}"
        )

    return model


def save_model(model: keras.Model, path: str | Path) -> Path:
    """Save the model in the native Keras v3 format (``.keras``)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    model.save(path)
    return path


def load_model(path: str | Path) -> keras.Model:
    """Load a model previously saved with :func:`save_model`."""
    return keras.models.load_model(Path(path))
