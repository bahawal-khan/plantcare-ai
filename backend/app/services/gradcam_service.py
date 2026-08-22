"""Wraps the Phase 07 Grad-CAM module for FastAPI's ``/predict`` endpoint.

This module never computes its own heatmap logic -- it only calls
``ml/src/explainability/gradcam.py`` (the module PHASE_07_GRAD_CAM.md
defines and ``tests/test_gradcam.py`` already verifies) so the API exposes
the actual Grad-CAM result, per PHASE_08_BACKEND.md requirement 8.
"""

from __future__ import annotations

from PIL import Image

from .model_service import ModelService
from ml.src.explainability.gradcam import build_gradcam_response_payload, generate_gradcam_explanation


def generate_gradcam_payload(
    model_service: ModelService,
    image: Image.Image,
    target_class: int | None = None,
) -> dict:
    """Full Grad-CAM response payload (2D heatmap/overlay + 3D visualization)
    for the given image, using the already-loaded model.
    """
    explanation = generate_gradcam_explanation(
        model_service.model,
        image,
        image_size=model_service.image_size,
        target_class=target_class,
        target_layer_name=model_service.target_layer,
    )
    return build_gradcam_response_payload(explanation, class_names=model_service.class_names)
