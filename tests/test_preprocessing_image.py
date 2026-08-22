"""Phase 02 tests: shared decode/resize preprocessing used by both the
training pipeline and (in later phases) FastAPI inference.
"""

from pathlib import Path

import numpy as np
from PIL import Image

from ml.src.preprocessing.image import (
    DEFAULT_IMAGE_SIZE,
    load_and_preprocess_image,
    preprocess_image_bytes,
    preprocess_pil_image,
)


def _save_rgba_image(path: Path, size=(50, 30)) -> None:
    array = np.zeros((size[1], size[0], 4), dtype=np.uint8)
    array[..., 0] = 200  # red channel
    array[..., 3] = 128  # alpha
    Image.fromarray(array, mode="RGBA").save(path)


def test_preprocess_converts_to_rgb_and_resizes(tmp_path: Path):
    path = tmp_path / "img.png"
    _save_rgba_image(path)
    result = load_and_preprocess_image(path, image_size=(224, 224))
    assert result.shape == (224, 224, 3)
    assert result.dtype == np.float32


def test_preprocess_output_is_normalized_0_1(tmp_path: Path):
    path = tmp_path / "img.png"
    _save_rgba_image(path)
    result = load_and_preprocess_image(path, image_size=(32, 32))
    assert result.min() >= 0.0
    assert result.max() <= 1.0


def test_preprocess_from_bytes_matches_from_path(tmp_path: Path):
    path = tmp_path / "img.jpg"
    array = np.full((40, 40, 3), (10, 20, 30), dtype=np.uint8)
    Image.fromarray(array).save(path)

    from_path = load_and_preprocess_image(path, image_size=(64, 64))
    from_bytes = preprocess_image_bytes(path.read_bytes(), image_size=(64, 64))

    assert np.allclose(from_path, from_bytes)


def test_default_image_size_matches_config_convention():
    assert DEFAULT_IMAGE_SIZE == (224, 224)


def test_preprocess_pil_image_handles_grayscale():
    gray = Image.new("L", (20, 20), color=128)
    result = preprocess_pil_image(gray, image_size=(20, 20))
    assert result.shape == (20, 20, 3)
