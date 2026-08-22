"""Shared fixtures for Phase 08 FastAPI backend tests.

Mirrors ``tests/test_gradcam.py``'s approach: build a tiny (``weights=None``,
small image size) EfficientNetB0 via ``ml/src/models/efficientnet.py`` and
point the app's settings at it, instead of loading the real ~20MB Stage 2
checkpoint. Fast and network-free, per TESTING_SPEC.md ("do not use the full
dataset in unit tests", "use small fixtures").
"""

from __future__ import annotations

import io
import json

import numpy as np
import pytest
from PIL import Image

from app.core.config import settings
from app.main import app
from ml.src.models.efficientnet import build_model, save_model

IMAGE_SIZE = (96, 96)  # 96 / 32 = 3x3 backbone grid; avoids a degenerate 1x1 Grad-CAM
CLASS_NAMES = ["Apple___Apple_scab", "Apple___healthy", "Grape___Black_rot"]


@pytest.fixture
def tiny_model_env(tmp_path, monkeypatch):
    """Point app settings at a tiny trained-looking model + fixture data."""
    model_path = tmp_path / "model.keras"
    class_mapping_path = tmp_path / "class_mapping.json"
    disease_info_path = tmp_path / "disease_info.json"
    metrics_path = tmp_path / "metrics.json"  # left absent -> evaluation metrics stay None

    model = build_model(num_classes=len(CLASS_NAMES), image_size=IMAGE_SIZE, weights=None)
    save_model(model, model_path)

    class_mapping_path.write_text(
        json.dumps({name: idx for idx, name in enumerate(CLASS_NAMES)}), encoding="utf-8"
    )
    disease_info_path.write_text(
        json.dumps(
            [
                {
                    "id": "apple-scab",
                    "plant": "Apple",
                    "name": "Apple Scab",
                    "description": "Fixture disease record for tests.",
                    "symptoms": ["Dark, scabby lesions on leaves and fruit."],
                    "causes": ["Fungal infection (Venturia inaequalis)."],
                    "prevention": ["Remove fallen leaves.", "Ensure good air circulation."],
                    "management": "Consult local agricultural extension guidance.",
                    "severity": "moderate",
                }
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(settings, "model_path", str(model_path))
    monkeypatch.setattr(settings, "class_mapping_path", str(class_mapping_path))
    monkeypatch.setattr(settings, "disease_info_path", str(disease_info_path))
    monkeypatch.setattr(settings, "evaluation_metrics_path", str(metrics_path))

    return {
        "model_path": model_path,
        "class_mapping_path": class_mapping_path,
        "disease_info_path": disease_info_path,
        "image_size": IMAGE_SIZE,
        "class_names": CLASS_NAMES,
    }


@pytest.fixture
def missing_model_env(tmp_path, monkeypatch):
    """Point settings at a model path that does not exist."""
    monkeypatch.setattr(settings, "model_path", str(tmp_path / "does_not_exist.keras"))
    monkeypatch.setattr(settings, "class_mapping_path", str(tmp_path / "does_not_exist.json"))


@pytest.fixture
def app_under_test():
    return app


def make_test_image_bytes(size: tuple[int, int] = IMAGE_SIZE, fmt: str = "PNG", seed: int = 0) -> bytes:
    rng = np.random.default_rng(seed)
    array = rng.integers(0, 256, size=(size[1], size[0], 3), dtype=np.uint8)
    image = Image.fromarray(array)
    buffer = io.BytesIO()
    image.save(buffer, format=fmt)
    return buffer.getvalue()
