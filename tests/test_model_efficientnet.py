"""Phase 03 smoke tests: EfficientNetB0 model construction.

Uses small ``num_classes``/``image_size`` values where the criterion under
test does not depend on the real config, to keep the suite fast. The
ImageNet-weights test is the only one that needs the real download.
"""

from __future__ import annotations

import numpy as np
import pytest

from tensorflow.keras import layers as keras_layers

from ml.src.models.efficientnet import (
    DEFAULT_IMAGE_SIZE,
    ClassificationHeadConfig,
    build_model,
    load_model,
    save_model,
    unfreeze_top_layers,
)

SMALL_IMAGE_SIZE = (96, 96)
NUM_CLASSES = 5


def test_model_loads_imagenet_weights_deterministically():
    """Two independent builds with weights='imagenet' must produce
    identical backbone weights, which random initialization would not.
    """
    model_a = build_model(NUM_CLASSES, image_size=SMALL_IMAGE_SIZE, weights="imagenet")
    model_b = build_model(NUM_CLASSES, image_size=SMALL_IMAGE_SIZE, weights="imagenet")

    kernel_a = model_a.get_layer("efficientnetb0").get_layer("stem_conv").get_weights()[0]
    kernel_b = model_b.get_layer("efficientnetb0").get_layer("stem_conv").get_weights()[0]
    assert np.array_equal(kernel_a, kernel_b)


def test_backbone_is_frozen_for_stage1():
    model = build_model(NUM_CLASSES, image_size=SMALL_IMAGE_SIZE, weights=None, freeze_backbone=True)

    backbone = model.get_layer("efficientnetb0")
    assert backbone.trainable is False
    assert all(not layer.trainable for layer in backbone.layers)

    # the head must remain trainable
    assert model.get_layer("predictions").trainable is True


def test_backbone_not_frozen_when_disabled():
    model = build_model(NUM_CLASSES, image_size=SMALL_IMAGE_SIZE, weights=None, freeze_backbone=False)
    backbone = model.get_layer("efficientnetb0")
    assert backbone.trainable is True


def test_output_dimension_equals_num_classes():
    for num_classes in (2, 5, 38):
        model = build_model(num_classes, image_size=SMALL_IMAGE_SIZE, weights=None)
        assert model.output_shape == (None, num_classes)


def test_forward_pass_produces_valid_softmax_distribution():
    model = build_model(NUM_CLASSES, image_size=SMALL_IMAGE_SIZE, weights=None)
    batch = np.random.default_rng(0).random((2, *SMALL_IMAGE_SIZE, 3)).astype(np.float32)

    output = model(batch, training=False).numpy()

    assert output.shape == (2, NUM_CLASSES)
    assert np.all(output >= 0.0)
    assert np.allclose(output.sum(axis=1), 1.0, atol=1e-5)


def test_model_save_and_load_roundtrip_preserves_predictions(tmp_path):
    model = build_model(NUM_CLASSES, image_size=SMALL_IMAGE_SIZE, weights=None)
    batch = np.random.default_rng(1).random((1, *SMALL_IMAGE_SIZE, 3)).astype(np.float32)
    predictions_before = model(batch, training=False).numpy()

    save_path = save_model(model, tmp_path / "model.keras")
    assert save_path.is_file()

    reloaded = load_model(save_path)
    predictions_after = reloaded(batch, training=False).numpy()

    assert np.allclose(predictions_before, predictions_after)


def test_configurable_head_adds_dense_layer():
    head_config = ClassificationHeadConfig(dropout_rate=0.5, dense_units=64)
    model = build_model(
        NUM_CLASSES, image_size=SMALL_IMAGE_SIZE, weights=None, head_config=head_config
    )
    assert model.get_layer("head_dense").units == 64
    assert model.get_layer("head_dropout").rate == 0.5


def test_invalid_num_classes_raises():
    with pytest.raises(ValueError):
        build_model(0, image_size=SMALL_IMAGE_SIZE, weights=None)


def test_invalid_dropout_rate_raises():
    with pytest.raises(ValueError):
        ClassificationHeadConfig(dropout_rate=1.5)


def test_default_image_size_matches_config_convention():
    assert DEFAULT_IMAGE_SIZE == (224, 224)


def test_unfreeze_top_layers_unfreezes_only_upper_portion():
    model = build_model(NUM_CLASSES, image_size=SMALL_IMAGE_SIZE, weights=None, freeze_backbone=True)
    backbone = model.get_layer("efficientnetb0")

    unfreeze_top_layers(model, unfreeze_from="block6a")

    assert backbone.trainable is True
    names = [layer.name for layer in backbone.layers]
    cutoff = next(i for i, n in enumerate(names) if n.startswith("block6a"))

    for layer in backbone.layers[:cutoff]:
        assert layer.trainable is False, f"{layer.name} should stay frozen"
    for layer in backbone.layers[cutoff:]:
        if isinstance(layer, keras_layers.BatchNormalization):
            continue
        assert layer.trainable is True, f"{layer.name} should be unfrozen"


def test_unfreeze_top_layers_keeps_batchnorm_frozen_by_default():
    model = build_model(NUM_CLASSES, image_size=SMALL_IMAGE_SIZE, weights=None, freeze_backbone=True)
    backbone = model.get_layer("efficientnetb0")

    unfreeze_top_layers(model, unfreeze_from="block6a")

    bn_layers = [layer for layer in backbone.layers if isinstance(layer, keras_layers.BatchNormalization)]
    assert bn_layers, "expected at least one BatchNormalization layer in the backbone"
    assert all(not layer.trainable for layer in bn_layers)


def test_unfreeze_top_layers_can_unfreeze_batchnorm():
    model = build_model(NUM_CLASSES, image_size=SMALL_IMAGE_SIZE, weights=None, freeze_backbone=True)
    backbone = model.get_layer("efficientnetb0")

    unfreeze_top_layers(model, unfreeze_from="block6a", freeze_batchnorm=False)

    names = [layer.name for layer in backbone.layers]
    cutoff = next(i for i, n in enumerate(names) if n.startswith("block6a"))
    for layer in backbone.layers[cutoff:]:
        assert layer.trainable is True


def test_unfreeze_top_layers_invalid_prefix_raises():
    model = build_model(NUM_CLASSES, image_size=SMALL_IMAGE_SIZE, weights=None, freeze_backbone=True)
    with pytest.raises(ValueError):
        unfreeze_top_layers(model, unfreeze_from="not_a_real_block")
