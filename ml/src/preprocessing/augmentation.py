"""Training-only augmentation.

Per PROJECT_SPEC.md / ML_SPEC.md / PHASE_02_DATASET_PIPELINE.md:
- augmentation is applied only to the training split, never to
  validation/test
- transforms are mild/realistic: horizontal flip, small rotation,
  moderate zoom, small translation, mild brightness/contrast

``get_transform(split, ...)`` is the single entry point the training data
pipeline should call: it returns the augmenting transform for
``split == "train"`` and a no-op (resize-only) transform for every other
split, so "augmentation is training-only" is enforced by construction
rather than by convention.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import numpy as np
from PIL import Image, ImageEnhance

from ml.src.preprocessing.image import DEFAULT_IMAGE_SIZE, preprocess_pil_image


@dataclass(frozen=True)
class AugmentationConfig:
    horizontal_flip: bool = True
    rotation_deg: float = 15.0
    zoom_range: tuple[float, float] = (0.9, 1.1)
    translation_frac: float = 0.1
    brightness_range: tuple[float, float] = (0.9, 1.1)
    contrast_range: tuple[float, float] = (0.9, 1.1)


DEFAULT_AUGMENTATION_CONFIG = AugmentationConfig()


def augment_image(
    image: np.ndarray,
    rng: np.random.Generator,
    config: AugmentationConfig = DEFAULT_AUGMENTATION_CONFIG,
) -> np.ndarray:
    """Apply mild random augmentation to a float32 [0, 1] HxWx3 array.

    Intended to run on already-decoded/resized training images.
    """
    pil_image = Image.fromarray((np.clip(image, 0.0, 1.0) * 255.0).astype(np.uint8))
    width, height = pil_image.size

    if config.horizontal_flip and rng.random() < 0.5:
        pil_image = pil_image.transpose(Image.FLIP_LEFT_RIGHT)

    angle = rng.uniform(-config.rotation_deg, config.rotation_deg)
    pil_image = pil_image.rotate(angle, resample=Image.BILINEAR, fillcolor=(0, 0, 0))

    zoom = rng.uniform(*config.zoom_range)
    if zoom != 1.0:
        new_w, new_h = max(1, round(width * zoom)), max(1, round(height * zoom))
        zoomed = pil_image.resize((new_w, new_h), resample=Image.BILINEAR)
        if zoom >= 1.0:
            left = (new_w - width) // 2
            top = (new_h - height) // 2
            pil_image = zoomed.crop((left, top, left + width, top + height))
        else:
            canvas = Image.new("RGB", (width, height))
            left = (width - new_w) // 2
            top = (height - new_h) // 2
            canvas.paste(zoomed, (left, top))
            pil_image = canvas

    max_dx = int(width * config.translation_frac)
    max_dy = int(height * config.translation_frac)
    dx = rng.integers(-max_dx, max_dx + 1) if max_dx > 0 else 0
    dy = rng.integers(-max_dy, max_dy + 1) if max_dy > 0 else 0
    pil_image = pil_image.transform(
        (width, height), Image.AFFINE, (1, 0, -dx, 0, 1, -dy), fillcolor=(0, 0, 0)
    )

    brightness_factor = rng.uniform(*config.brightness_range)
    pil_image = ImageEnhance.Brightness(pil_image).enhance(brightness_factor)
    contrast_factor = rng.uniform(*config.contrast_range)
    pil_image = ImageEnhance.Contrast(pil_image).enhance(contrast_factor)

    return np.asarray(pil_image, dtype=np.float32) / 255.0


def get_transform(
    split: str,
    image_size: tuple[int, int] = DEFAULT_IMAGE_SIZE,
    config: AugmentationConfig = DEFAULT_AUGMENTATION_CONFIG,
    seed: int | None = None,
) -> Callable[[Image.Image], np.ndarray]:
    """Return the preprocessing(+augmentation) transform for a split.

    ``split == "train"`` -> decode/resize followed by random augmentation.
    any other split (``val``/``test``) -> decode/resize only, no augmentation.
    """
    rng = np.random.default_rng(seed)

    if split == "train":

        def transform(image: Image.Image) -> np.ndarray:
            base = preprocess_pil_image(image, image_size)
            return augment_image(base, rng, config)

        return transform

    def identity_transform(image: Image.Image) -> np.ndarray:
        return preprocess_pil_image(image, image_size)

    return identity_transform
