"""Shared image decode/resize preprocessing.

This module is the single source of truth for turning a raw image (file
path or in-memory bytes) into the normalized array the model consumes.
Both the training data pipeline (Phase 03+) and the FastAPI inference
service (Phase 08+) must call this module rather than reimplementing
decode/resize logic, per ML_SPEC.md "consistent preprocessing" and
CLAUDE.md rule 11.
"""

from __future__ import annotations

import io
from pathlib import Path

import numpy as np
from PIL import Image

DEFAULT_IMAGE_SIZE = (224, 224)


def preprocess_pil_image(image: Image.Image, image_size: tuple[int, int] = DEFAULT_IMAGE_SIZE) -> np.ndarray:
    """Convert to RGB, resize, and scale to float32 in [0, 1]."""
    rgb_image = image.convert("RGB")
    resized = rgb_image.resize(image_size, resample=Image.BILINEAR)
    array = np.asarray(resized, dtype=np.float32) / 255.0
    return array


def load_and_preprocess_image(
    path: str | Path, image_size: tuple[int, int] = DEFAULT_IMAGE_SIZE
) -> np.ndarray:
    """Decode an image file from disk (training pipeline use)."""
    with Image.open(path) as img:
        return preprocess_pil_image(img, image_size)


def preprocess_image_bytes(
    data: bytes, image_size: tuple[int, int] = DEFAULT_IMAGE_SIZE
) -> np.ndarray:
    """Decode an in-memory image (FastAPI upload inference use)."""
    with Image.open(io.BytesIO(data)) as img:
        return preprocess_pil_image(img, image_size)
