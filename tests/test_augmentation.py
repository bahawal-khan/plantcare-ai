"""Phase 02 tests: augmentation is applied only for the training split,
and produces mild/realistic transforms.
"""

import numpy as np
from PIL import Image

from ml.src.preprocessing.augmentation import AugmentationConfig, augment_image, get_transform


def _sample_image(size=(64, 64)):
    array = np.zeros((size[1], size[0], 3), dtype=np.uint8)
    array[:, : size[0] // 2] = (255, 0, 0)  # left half red
    array[:, size[0] // 2 :] = (0, 0, 255)  # right half blue
    return Image.fromarray(array)


def test_get_transform_train_applies_augmentation():
    image = _sample_image()
    transform = get_transform("train", image_size=(64, 64), seed=0)
    result = transform(image)
    assert result.shape == (64, 64, 3)
    assert result.dtype == np.float32


def test_get_transform_val_and_test_are_deterministic_no_augmentation():
    image = _sample_image()
    val_transform = get_transform("val", image_size=(64, 64))
    test_transform = get_transform("test", image_size=(64, 64))

    val_out_1 = val_transform(image)
    val_out_2 = val_transform(image)
    test_out = test_transform(image)

    # No augmentation randomness: repeated calls on the same split are identical.
    assert np.array_equal(val_out_1, val_out_2)
    assert np.array_equal(val_out_1, test_out)


def test_train_transform_differs_from_plain_resize_with_high_probability():
    image = _sample_image()
    val_transform = get_transform("val", image_size=(64, 64))
    baseline = val_transform(image)

    train_transform = get_transform("train", image_size=(64, 64), seed=123)
    augmented = train_transform(image)

    assert not np.array_equal(baseline, augmented)


def test_augment_image_output_stays_in_valid_range():
    rng = np.random.default_rng(1)
    image = np.asarray(_sample_image(), dtype=np.float32) / 255.0
    for _ in range(20):
        out = augment_image(image, rng)
        assert out.min() >= 0.0
        assert out.max() <= 1.0
        assert out.shape == image.shape


def test_augment_image_is_reproducible_given_seeded_rng():
    image = np.asarray(_sample_image(), dtype=np.float32) / 255.0
    out1 = augment_image(image, np.random.default_rng(7))
    out2 = augment_image(image, np.random.default_rng(7))
    assert np.array_equal(out1, out2)


def test_augmentation_config_defaults_are_mild():
    config = AugmentationConfig()
    assert config.rotation_deg <= 30
    assert 0.5 <= config.zoom_range[0] < 1.0 <= config.zoom_range[1] <= 1.5
    assert config.translation_frac <= 0.25
