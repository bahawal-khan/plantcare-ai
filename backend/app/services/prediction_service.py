"""Runs a single-image prediction through a loaded :class:`ModelService`.

Preprocessing goes through ``ml/src/preprocessing/image.py`` -- the same
module the training pipeline and Phase 07 Grad-CAM use -- so inference
preprocessing stays consistent with training, per CLAUDE.md rule 11.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from PIL import Image

from .model_service import ModelService
from ml.src.preprocessing.image import preprocess_pil_image


@dataclass(frozen=True)
class TopKEntry:
    rank: int
    class_name: str
    plant: str
    disease: str
    confidence: float


@dataclass(frozen=True)
class PredictionResult:
    class_name: str
    plant: str
    disease: str
    confidence: float
    predicted_class_index: int
    top_k: list[TopKEntry]


def split_class_name(class_name: str) -> tuple[str, str]:
    """Split a raw 'Plant___Disease' class label into (plant, disease).

    Matches the label format used throughout ``data/class_mapping.json``
    (e.g. ``"Apple___Apple_scab"``, ``"Apple___healthy"``).
    """
    if "___" in class_name:
        plant_raw, disease_raw = class_name.split("___", 1)
    else:
        plant_raw, disease_raw = class_name, ""
    plant = plant_raw.replace("_", " ").strip()
    disease = disease_raw.replace("_", " ").strip() or "Healthy"
    return plant, disease


def predict(model_service: ModelService, image: Image.Image, top_k: int = 5) -> PredictionResult:
    array = preprocess_pil_image(image, model_service.image_size)
    batch = array[np.newaxis, ...]
    probabilities = model_service.predict_probabilities(batch)

    predicted_index = int(np.argmax(probabilities))
    k = max(1, min(top_k, model_service.num_classes))
    top_indices = np.argsort(probabilities)[::-1][:k]

    top_k_entries = []
    for rank, idx in enumerate(top_indices, start=1):
        idx = int(idx)
        name = model_service.class_names[idx]
        plant, disease = split_class_name(name)
        top_k_entries.append(
            TopKEntry(rank=rank, class_name=name, plant=plant, disease=disease, confidence=float(probabilities[idx]))
        )

    class_name = model_service.class_names[predicted_index]
    plant, disease = split_class_name(class_name)

    return PredictionResult(
        class_name=class_name,
        plant=plant,
        disease=disease,
        confidence=float(probabilities[predicted_index]),
        predicted_class_index=predicted_index,
        top_k=top_k_entries,
    )
