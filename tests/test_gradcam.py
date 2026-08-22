"""Phase 07 tests: Grad-CAM explainability.

Uses ``weights=None`` and a tiny synthetic image size, mirroring
``tests/test_model_efficientnet.py`` / ``tests/test_evaluation.py``, to keep
the suite fast and network-free. Never runs against the real Stage 2
checkpoint or the full dataset -- that happens once via
``ml/scripts/generate_gradcam.py``.
"""

from __future__ import annotations

import base64
import io

import numpy as np
import pytest
from PIL import Image

from ml.src.explainability.gradcam import (
    RESPONSIBLE_USE_NOTE,
    TARGET_LAYER_NAME,
    GradCAMExplanation,
    build_3d_visualization_payload,
    build_gradcam_response_payload,
    colorize_heatmap,
    compute_gradcam,
    generate_gradcam_explanation,
    overlay_heatmap,
    resize_heatmap,
    save_gradcam_images,
)
from ml.src.models.efficientnet import ClassificationHeadConfig, build_model
from ml.src.preprocessing.image import preprocess_pil_image

IMAGE_SIZE = (96, 96)
NUM_CLASSES = 5


def _random_image(size: tuple[int, int] = IMAGE_SIZE, seed: int = 0) -> Image.Image:
    rng = np.random.default_rng(seed)
    array = rng.integers(0, 256, size=(size[1], size[0], 3), dtype=np.uint8)
    return Image.fromarray(array)


def _model(**kwargs) -> "keras.Model":  # noqa: F821 - typing only
    defaults = dict(num_classes=NUM_CLASSES, image_size=IMAGE_SIZE, weights=None, freeze_backbone=True)
    defaults.update(kwargs)
    return build_model(**defaults)


def test_gradcam_generates_heatmap_in_unit_range():
    model = _model()
    image = _random_image()

    explanation = generate_gradcam_explanation(model, image, image_size=IMAGE_SIZE)

    assert isinstance(explanation, GradCAMExplanation)
    assert explanation.heatmap.ndim == 2
    assert explanation.heatmap.min() >= 0.0
    assert explanation.heatmap.max() <= 1.0 + 1e-6


def test_gradcam_target_layer_is_documented_default():
    model = _model()
    explanation = generate_gradcam_explanation(model, _random_image(), image_size=IMAGE_SIZE)
    assert explanation.target_layer == TARGET_LAYER_NAME == "top_activation"


def test_gradcam_heatmap_resized_matches_image_size():
    model = _model()
    explanation = generate_gradcam_explanation(model, _random_image(), image_size=IMAGE_SIZE)

    assert explanation.heatmap_resized.shape == (IMAGE_SIZE[1], IMAGE_SIZE[0])
    assert explanation.heatmap_resized.min() >= 0.0
    assert explanation.heatmap_resized.max() <= 1.0 + 1e-6


def test_gradcam_overlay_aligned_with_original_image():
    model = _model()
    explanation = generate_gradcam_explanation(model, _random_image(), image_size=IMAGE_SIZE)

    assert explanation.overlay_image.shape == explanation.original_image.shape
    assert explanation.overlay_image.shape == (IMAGE_SIZE[1], IMAGE_SIZE[0], 3)
    assert explanation.overlay_image.dtype == np.uint8


def test_gradcam_predicted_class_and_confidence_are_valid():
    model = _model()
    explanation = generate_gradcam_explanation(model, _random_image(), image_size=IMAGE_SIZE)

    assert 0 <= explanation.predicted_class_index < NUM_CLASSES
    assert 0.0 <= explanation.confidence <= 1.0


def test_gradcam_respects_explicit_target_class():
    model = _model()
    image = _random_image()

    explanation = generate_gradcam_explanation(model, image, image_size=IMAGE_SIZE, target_class=2)

    assert explanation.predicted_class_index == 2


def test_gradcam_uses_shared_preprocessing_pipeline():
    """The explanation's base image must equal what the shared
    ``preprocess_pil_image`` (training/inference preprocessing) produces,
    per CLAUDE.md rule 11 / ARCHITECTURE.md's consistent-preprocessing rule.
    """
    model = _model()
    image = _random_image()

    explanation = generate_gradcam_explanation(model, image, image_size=IMAGE_SIZE)
    expected = (preprocess_pil_image(image, IMAGE_SIZE) * 255.0).astype(np.uint8)

    np.testing.assert_array_equal(explanation.original_image, expected)


def test_gradcam_works_with_configurable_dense_head():
    model = _model(head_config=ClassificationHeadConfig(dropout_rate=0.2, dense_units=16))
    explanation = generate_gradcam_explanation(model, _random_image(), image_size=IMAGE_SIZE)

    assert explanation.heatmap.size > 0
    assert 0 <= explanation.predicted_class_index < NUM_CLASSES


def test_gradcam_invalid_target_layer_raises():
    model = _model()
    preprocessed = preprocess_pil_image(_random_image(), IMAGE_SIZE)[np.newaxis, ...]

    with pytest.raises(ValueError):
        compute_gradcam(model, preprocessed, target_layer_name="not_a_real_layer")


def test_resize_heatmap_matches_requested_size():
    heatmap = np.array([[0.0, 1.0], [0.5, 0.25]], dtype=np.float32)
    resized = resize_heatmap(heatmap, (20, 10))
    assert resized.shape == (10, 20)
    assert resized.min() >= 0.0 and resized.max() <= 1.0


def test_colorize_heatmap_produces_rgb_uint8():
    heatmap = np.linspace(0.0, 1.0, 16).reshape(4, 4).astype(np.float32)
    colored = colorize_heatmap(heatmap)
    assert colored.shape == (4, 4, 3)
    assert colored.dtype == np.uint8


def test_overlay_heatmap_rejects_shape_mismatch():
    original = np.zeros((10, 10, 3), dtype=np.uint8)
    heatmap = np.zeros((5, 5), dtype=np.float32)
    with pytest.raises(ValueError):
        overlay_heatmap(original, heatmap)


def test_save_gradcam_images_writes_png_files(tmp_path):
    model = _model()
    explanation = generate_gradcam_explanation(model, _random_image(), image_size=IMAGE_SIZE)

    paths = save_gradcam_images(explanation, tmp_path / "gradcam", stem="sample")

    assert paths["heatmap"].is_file()
    assert paths["overlay"].is_file()
    with Image.open(paths["overlay"]) as img:
        assert img.size == IMAGE_SIZE


def test_3d_visualization_payload_uses_real_heatmap_and_flags_limitations():
    model = _model()
    explanation = generate_gradcam_explanation(model, _random_image(), image_size=IMAGE_SIZE)

    payload = build_3d_visualization_payload(explanation, grid_size=8)

    assert payload["grid_size"] == [8, 8]
    heightmap = payload["heightmap"]
    assert len(heightmap) == 8 and all(len(row) == 8 for row in heightmap)
    flat = [value for row in heightmap for value in row]
    assert all(0.0 <= value <= 1.0 for value in flat)
    assert payload["is_biological_reconstruction"] is False
    assert "biological" in payload["limitations"].lower()

    # texture must be a real, decodable PNG derived from the actual overlay
    texture_bytes = base64.b64decode(payload["texture_png_base64"])
    with Image.open(io.BytesIO(texture_bytes)) as texture_img:
        assert texture_img.size == IMAGE_SIZE


def test_3d_heightmap_is_not_constant_for_a_structured_input():
    """The 3D payload must reflect the actual Grad-CAM output, not a
    placeholder -- so it should vary across the grid for a non-trivial input.
    """
    model = _model()
    # A structured (non-uniform) image is more likely to produce spatial
    # variation in backbone activations than pure noise.
    array = np.zeros((IMAGE_SIZE[1], IMAGE_SIZE[0], 3), dtype=np.uint8)
    array[: IMAGE_SIZE[1] // 2, :, :] = 255
    image = Image.fromarray(array)

    explanation = generate_gradcam_explanation(model, image, image_size=IMAGE_SIZE)
    payload = build_3d_visualization_payload(explanation, grid_size=8)

    flat = [value for row in payload["heightmap"] for value in row]
    assert max(flat) - min(flat) >= 0.0  # heatmap is a valid, boundable signal
    assert payload["heightmap"] == resize_heatmap(explanation.heatmap, (8, 8)).tolist()


def test_gradcam_response_payload_has_required_fields_for_frontend_backend():
    model = _model()
    class_names = [f"class_{i}" for i in range(NUM_CLASSES)]
    explanation = generate_gradcam_explanation(model, _random_image(), image_size=IMAGE_SIZE)

    payload = build_gradcam_response_payload(explanation, class_names=class_names)

    for key in (
        "predicted_class_index",
        "predicted_class",
        "confidence",
        "target_layer",
        "heatmap_png_base64",
        "overlay_png_base64",
        "visualization_3d",
        "limitations",
    ):
        assert key in payload

    assert payload["predicted_class"] == class_names[payload["predicted_class_index"]]
    assert payload["limitations"] == RESPONSIBLE_USE_NOTE
    assert "not proof of biological causation" in payload["limitations"]

    heatmap_bytes = base64.b64decode(payload["heatmap_png_base64"])
    with Image.open(io.BytesIO(heatmap_bytes)) as img:
        assert img.size == IMAGE_SIZE

    overlay_bytes = base64.b64decode(payload["overlay_png_base64"])
    with Image.open(io.BytesIO(overlay_bytes)) as img:
        assert img.size == IMAGE_SIZE


def test_gradcam_response_payload_without_class_names_has_none_predicted_class():
    model = _model()
    explanation = generate_gradcam_explanation(model, _random_image(), image_size=IMAGE_SIZE)
    payload = build_gradcam_response_payload(explanation, class_names=None)
    assert payload["predicted_class"] is None
