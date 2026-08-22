"""Grad-CAM explainability for the EfficientNetB0 classifier (Phase 07).

Implements PHASE_07_GRAD_CAM.md: a 2D Grad-CAM heatmap/overlay aligned with
the original input image, plus the data payload the interactive 3D
visualization feature and Phase 08/09 will consume.

## Target layer

``TARGET_LAYER_NAME = "top_activation"``. ``ml/src/models/efficientnet.py``
builds the backbone with ``keras.applications.EfficientNetB0(include_top=False,
pooling=None)``, whose returned output tensor *is* the ``top_activation``
layer's output (the final Swish-activated, batch-normalized feature map,
shape ``(H/32, W/32, 1280)`` for a ``(H, W)`` input) -- i.e.
``backbone.output`` and ``backbone.get_layer("top_activation").output`` are
the same tensor. This is the last spatial feature map before
``GlobalAveragePooling2D`` feeds the classification head, making it the
standard Grad-CAM target for this architecture (analogous to the last
conv+activation layer used in the original Grad-CAM/Keras tutorials).

## Nested-model gradient plumbing

``build_model`` calls the EfficientNetB0 backbone *as a layer* inside the
outer functional model (``x = backbone(x)``). Keras does not expose that
call's intermediate tensors via ``backbone.get_layer(name).output`` from the
outer model's graph (attempting to build
``keras.Model(model.input, [backbone.get_layer(...).output, model.output])``
raises "Output ... is not connected to inputs"). Instead this module:

1. Reuses the model's own ``restore_pixel_range`` ``Rescaling`` layer to
   reproduce the exact ``[0, 1] -> [0, 255]`` step ``build_model`` applies
   before the backbone.
2. Calls the backbone directly (eagerly, inside a ``tf.GradientTape``) to get
   ``conv_output`` and explicitly ``tape.watch``es it.
3. Rebuilds the classification head (``GlobalAveragePooling2D`` -> optional
   dense -> dropout -> ``predictions``) as a small standalone model that
   reuses the *same trained layer objects/weights* from ``model``, so no
   weights are duplicated or retrained.

## Preprocessing consistency

Explanations are generated from ``ml/src/preprocessing/image.py``'s
``preprocess_pil_image`` -- the exact same decode/resize/[0, 1]-scale
function the training pipeline (``ml/src/training/dataset.py``) and the
planned Phase 08 inference service call, per CLAUDE.md rule 11 and
ARCHITECTURE.md ("Training and inference preprocessing must share the same
source/configuration").

## Frontend/backend-consumable output

``build_gradcam_response_payload`` returns a JSON-safe dict (base64-encoded
PNGs + plain floats/lists) intended as the data contract for a future Phase
08 API response and Phase 09 rendering -- this module defines that contract
but does not implement any FastAPI route or frontend code (out of scope for
Phase 07).

## Interactive 3D Grad-CAM visualization

``build_3d_visualization_payload`` derives a small ``grid_size x grid_size``
height/intensity grid by resizing the *actual* Grad-CAM heatmap (not a
placeholder), plus the same overlay image as a texture. Per
PHASE_07_GRAD_CAM.md requirements 8-10, this is explicitly documented and
flagged (``is_biological_reconstruction: False``) as an interactive
visualization of the 2D Grad-CAM output only -- it must never be presented as
a reconstruction of the leaf's true biological 3D geometry or as 3D disease
localization.

## Responsible use

``RESPONSIBLE_USE_NOTE`` is included in every response payload: Grad-CAM (2D
or 3D) is an interpretability aid, not proof of biological causation or
medical/agronomic certainty, per PROJECT_SPEC.md section 8 and CLAUDE.md
rule 5.
"""

from __future__ import annotations

import base64
import io
from dataclasses import dataclass
from pathlib import Path

import matplotlib
import numpy as np
import tensorflow as tf
from PIL import Image
from tensorflow import keras

from ml.src.preprocessing.image import DEFAULT_IMAGE_SIZE, preprocess_pil_image

TARGET_LAYER_NAME = "top_activation"
BACKBONE_LAYER_NAME = "efficientnetb0"
RESCALING_LAYER_NAME = "restore_pixel_range"
HEAD_LAYER_NAMES = ("global_average_pooling", "head_dense", "head_dropout", "predictions")

DEFAULT_COLORMAP = "jet"
DEFAULT_OVERLAY_ALPHA = 0.4
DEFAULT_3D_GRID_SIZE = 32

RESPONSIBLE_USE_NOTE = (
    "Grad-CAM highlights the image regions that most influenced this specific "
    "model prediction. It is an interpretability aid, not proof of biological "
    "causation and not a medical or agronomic certainty. The interactive 3D "
    "view is only an alternative rendering of this same 2D Grad-CAM heatmap: "
    "it does not reconstruct the leaf's true biological 3D structure and does "
    "not provide true 3D disease localization."
)


@dataclass(frozen=True)
class GradCAMExplanation:
    """Result of running Grad-CAM on one preprocessed image."""

    predicted_class_index: int
    confidence: float
    target_layer: str
    heatmap: np.ndarray  # float32 [0, 1], small backbone spatial grid (e.g. 7x7)
    heatmap_resized: np.ndarray  # float32 [0, 1], resized to image_size (H, W)
    heatmap_image: np.ndarray  # uint8 RGB, colorized heatmap alone, (H, W, 3)
    overlay_image: np.ndarray  # uint8 RGB, heatmap blended onto the original image, (H, W, 3)
    original_image: np.ndarray  # uint8 RGB, the preprocessed input as displayed, (H, W, 3)


def _get_backbone(model: keras.Model, backbone_layer_name: str = BACKBONE_LAYER_NAME) -> keras.Model:
    try:
        return model.get_layer(backbone_layer_name)
    except ValueError as exc:
        raise ValueError(
            f"Model has no layer named {backbone_layer_name!r}; expected the "
            "EfficientNetB0 backbone built by ml/src/models/efficientnet.py"
        ) from exc


def _validate_target_layer(backbone: keras.Model, target_layer_name: str) -> None:
    try:
        target_layer = backbone.get_layer(target_layer_name)
    except ValueError as exc:
        raise ValueError(
            f"Backbone has no layer named {target_layer_name!r}"
        ) from exc
    if tuple(target_layer.output.shape) != tuple(backbone.output.shape):
        raise ValueError(
            f"{target_layer_name!r} output shape {tuple(target_layer.output.shape)} does not "
            f"match the backbone's final output shape {tuple(backbone.output.shape)}. "
            "gradcam.py assumes the target layer IS the backbone's final feature map "
            "(see module docstring); pick a different target_layer_name or rework "
            "_build_classifier_head for a mid-backbone layer."
        )


def _build_classifier_head(model: keras.Model, backbone: keras.Model) -> keras.Model:
    """Rebuild GAP -> [dense] -> dropout -> predictions, reusing trained weights."""
    head_input = keras.Input(shape=backbone.output_shape[1:], name="gradcam_head_input")
    x = head_input
    found_any = False
    for layer_name in HEAD_LAYER_NAMES:
        try:
            layer = model.get_layer(layer_name)
        except ValueError:
            continue
        x = layer(x)
        found_any = True
    if not found_any:
        raise ValueError(
            f"Model has none of the expected classification-head layers {HEAD_LAYER_NAMES!r}"
        )
    return keras.Model(head_input, x, name="gradcam_classifier_head")


def compute_gradcam(
    model: keras.Model,
    image_batch: np.ndarray,
    target_class: int | None = None,
    target_layer_name: str = TARGET_LAYER_NAME,
) -> tuple[np.ndarray, int, float]:
    """Compute the raw Grad-CAM heatmap for one preprocessed image batch.

    ``image_batch`` must be float32 in ``[0, 1]``, shape ``(1, H, W, 3)`` --
    the same contract ``ml/src/preprocessing/image.py`` produces.

    Returns ``(heatmap, predicted_class_index, confidence)`` where
    ``heatmap`` is float32 in ``[0, 1]`` at the backbone's small spatial
    resolution (not yet resized to the input image size).
    """
    backbone = _get_backbone(model)
    _validate_target_layer(backbone, target_layer_name)
    classifier_head = _build_classifier_head(model, backbone)
    rescale_layer = model.get_layer(RESCALING_LAYER_NAME)

    inputs = tf.convert_to_tensor(image_batch, dtype=tf.float32)

    with tf.GradientTape() as tape:
        rescaled = rescale_layer(inputs)
        conv_output = backbone(rescaled, training=False)
        tape.watch(conv_output)
        predictions = classifier_head(conv_output, training=False)
        if target_class is None:
            target_class = int(tf.argmax(predictions[0]).numpy())
        class_channel = predictions[:, target_class]

    grads = tape.gradient(class_channel, conv_output)
    if grads is None:
        raise RuntimeError(
            "Grad-CAM failed: no gradient reached the target layer; check that "
            "target_layer_name lies on the path from the model's input to its output"
        )

    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    weighted_features = conv_output[0] @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(weighted_features)
    heatmap = tf.maximum(heatmap, 0.0)
    max_value = float(tf.reduce_max(heatmap))
    if max_value > 0.0:
        heatmap = heatmap / max_value

    confidence = float(predictions.numpy()[0, target_class])
    return heatmap.numpy().astype(np.float32), int(target_class), confidence


def resize_heatmap(heatmap: np.ndarray, size: tuple[int, int]) -> np.ndarray:
    """Bilinear-resize a ``[0, 1]`` heatmap to ``size = (width, height)``.

    Uses the same ``PIL`` bilinear resize convention as
    ``ml/src/preprocessing/image.py`` so the resized heatmap stays pixel-
    aligned with the original image it will be overlaid on.
    """
    scaled = np.clip(heatmap, 0.0, 1.0)
    img = Image.fromarray((scaled * 255.0).astype(np.uint8))
    resized = img.resize(size, resample=Image.BILINEAR)
    return np.asarray(resized, dtype=np.float32) / 255.0


def colorize_heatmap(heatmap: np.ndarray, colormap: str = DEFAULT_COLORMAP) -> np.ndarray:
    """Map a ``[0, 1]`` heatmap to an RGB ``uint8`` image via a matplotlib colormap."""
    cmap = matplotlib.colormaps[colormap]
    colored = cmap(np.clip(heatmap, 0.0, 1.0))[:, :, :3]
    return (colored * 255.0).astype(np.uint8)


def overlay_heatmap(
    original_rgb_uint8: np.ndarray,
    heatmap_resized: np.ndarray,
    alpha: float = DEFAULT_OVERLAY_ALPHA,
    colormap: str = DEFAULT_COLORMAP,
) -> np.ndarray:
    """Alpha-blend a colorized heatmap onto the original image (uint8 RGB, same H, W)."""
    if original_rgb_uint8.shape[:2] != heatmap_resized.shape[:2]:
        raise ValueError(
            f"Image shape {original_rgb_uint8.shape[:2]} does not match heatmap shape "
            f"{heatmap_resized.shape[:2]}; resize_heatmap to the image size first"
        )
    colored = colorize_heatmap(heatmap_resized, colormap).astype(np.float32)
    blended = original_rgb_uint8.astype(np.float32) * (1.0 - alpha) + colored * alpha
    return np.clip(blended, 0, 255).astype(np.uint8)


def generate_gradcam_explanation(
    model: keras.Model,
    image: Image.Image,
    image_size: tuple[int, int] = DEFAULT_IMAGE_SIZE,
    target_class: int | None = None,
    target_layer_name: str = TARGET_LAYER_NAME,
    alpha: float = DEFAULT_OVERLAY_ALPHA,
    colormap: str = DEFAULT_COLORMAP,
) -> GradCAMExplanation:
    """End-to-end Grad-CAM: decode/preprocess -> heatmap -> resize -> overlay.

    ``image`` is a PIL image (already-open upload or file); preprocessing goes
    through the shared ``preprocess_pil_image`` so this matches training and
    (future) inference preprocessing exactly.
    """
    preprocessed = preprocess_pil_image(image, image_size)
    batch = preprocessed[np.newaxis, ...]

    heatmap, predicted_class_index, confidence = compute_gradcam(
        model, batch, target_class=target_class, target_layer_name=target_layer_name
    )

    heatmap_resized = resize_heatmap(heatmap, image_size)
    original_uint8 = np.clip(preprocessed * 255.0, 0, 255).astype(np.uint8)
    heatmap_image = colorize_heatmap(heatmap_resized, colormap)
    overlay_image = overlay_heatmap(original_uint8, heatmap_resized, alpha=alpha, colormap=colormap)

    return GradCAMExplanation(
        predicted_class_index=predicted_class_index,
        confidence=confidence,
        target_layer=target_layer_name,
        heatmap=heatmap,
        heatmap_resized=heatmap_resized,
        heatmap_image=heatmap_image,
        overlay_image=overlay_image,
        original_image=original_uint8,
    )


def encode_png_base64(array_uint8: np.ndarray) -> str:
    """Encode an RGB ``uint8`` array as a base64 PNG string (frontend/API-consumable)."""
    buffer = io.BytesIO()
    Image.fromarray(array_uint8).save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def save_gradcam_images(explanation: GradCAMExplanation, output_dir: str | Path, stem: str) -> dict[str, Path]:
    """Save the heatmap and overlay as PNG files under ``output_dir``."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    heatmap_path = output_dir / f"{stem}_heatmap.png"
    overlay_path = output_dir / f"{stem}_overlay.png"
    Image.fromarray(explanation.heatmap_image).save(heatmap_path)
    Image.fromarray(explanation.overlay_image).save(overlay_path)
    return {"heatmap": heatmap_path, "overlay": overlay_path}


def build_3d_visualization_payload(
    explanation: GradCAMExplanation,
    grid_size: int = DEFAULT_3D_GRID_SIZE,
) -> dict:
    """Data contract for the interactive 3D Grad-CAM visualization.

    Consumers (Phase 08 API response, Phase 09 frontend renderer) are
    expected to drive an interactive 3D surface (e.g. a plane or simple
    leaf-shaped mesh) using ``heightmap`` for displacement/color intensity
    and ``texture_png_base64`` as the surface texture -- both derived
    directly from this explanation's real Grad-CAM output, not a
    placeholder. See module docstring and ``RESPONSIBLE_USE_NOTE``: this is
    only an interactive rendering of the 2D heatmap, never a biological 3D
    reconstruction.
    """
    grid = resize_heatmap(explanation.heatmap, (grid_size, grid_size))
    return {
        "target_layer": explanation.target_layer,
        "predicted_class_index": explanation.predicted_class_index,
        "confidence": explanation.confidence,
        "grid_size": [grid_size, grid_size],
        "heightmap": grid.tolist(),
        "texture_png_base64": encode_png_base64(explanation.overlay_image),
        "colormap": DEFAULT_COLORMAP,
        "is_biological_reconstruction": False,
        "limitations": RESPONSIBLE_USE_NOTE,
    }


def build_gradcam_response_payload(
    explanation: GradCAMExplanation,
    class_names: list[str] | None = None,
    grid_size: int = DEFAULT_3D_GRID_SIZE,
) -> dict:
    """Full JSON-safe Grad-CAM payload: 2D heatmap/overlay + 3D visualization data.

    This is the format Phase 08's FastAPI ``/predict`` (or a dedicated
    Grad-CAM endpoint) is expected to serialize, and what Phase 09's
    frontend is expected to render -- defined here per PHASE_07_GRAD_CAM.md
    requirement 12, without implementing either of those phases.
    """
    predicted_class = (
        class_names[explanation.predicted_class_index]
        if class_names is not None
        else None
    )
    return {
        "predicted_class_index": explanation.predicted_class_index,
        "predicted_class": predicted_class,
        "confidence": explanation.confidence,
        "target_layer": explanation.target_layer,
        "heatmap_png_base64": encode_png_base64(explanation.heatmap_image),
        "overlay_png_base64": encode_png_base64(explanation.overlay_image),
        "visualization_3d": build_3d_visualization_payload(explanation, grid_size=grid_size),
        "limitations": RESPONSIBLE_USE_NOTE,
    }
