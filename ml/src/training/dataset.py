"""tf.data pipeline over split manifests for Stage 1/2 training.

Reads the path/class manifests written by ``ml/src/data/splits.py`` and
turns them into batched ``tf.data.Dataset`` objects, routing each split
through ``ml/src/preprocessing/augmentation.get_transform`` so that the
"augmentation is training-only" and "consistent preprocessing" rules
(ML_SPEC.md, CLAUDE.md rule 11) are enforced by construction, not by
caller discipline.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image

from ml.src.data.splits import load_split_manifest
from ml.src.preprocessing.augmentation import AugmentationConfig, DEFAULT_AUGMENTATION_CONFIG, get_transform
from ml.src.preprocessing.image import DEFAULT_IMAGE_SIZE


def load_manifest_records(
    manifest_path: str | Path,
    dataset_root: str | Path,
    class_mapping: dict[str, int],
    limit: int | None = None,
) -> tuple[list[str], list[int]]:
    """Return absolute image paths and integer labels for a manifest."""
    entries = load_split_manifest(Path(manifest_path))
    if limit is not None:
        entries = entries[:limit]
    dataset_root = Path(dataset_root)
    paths = [str(dataset_root / entry["path"]) for entry in entries]
    labels = [class_mapping[entry["class"]] for entry in entries]
    return paths, labels


def build_dataset(
    manifest_path: str | Path,
    dataset_root: str | Path,
    class_mapping: dict[str, int],
    split: str,
    image_size: tuple[int, int] = DEFAULT_IMAGE_SIZE,
    batch_size: int = 32,
    seed: int = 42,
    shuffle: bool = True,
    limit: int | None = None,
    augmentation_config: AugmentationConfig = DEFAULT_AUGMENTATION_CONFIG,
) -> tuple[tf.data.Dataset, int]:
    """Build a batched, prefetched dataset for one split.

    Returns ``(dataset, num_samples)``. ``split == "train"`` applies random
    augmentation via ``get_transform``; any other split is resize-only.
    """
    paths, labels = load_manifest_records(manifest_path, dataset_root, class_mapping, limit=limit)
    if not paths:
        raise ValueError(f"No records found in manifest {manifest_path}")

    transform = get_transform(split, image_size=image_size, config=augmentation_config, seed=seed)

    def _load(path_tensor: tf.Tensor, label_tensor: tf.Tensor) -> tuple[np.ndarray, np.ndarray]:
        path_str = path_tensor.numpy().decode("utf-8")
        with Image.open(path_str) as img:
            array = transform(img)
        return array.astype(np.float32), np.int64(label_tensor.numpy())

    def _tf_load(path_tensor: tf.Tensor, label_tensor: tf.Tensor) -> tuple[tf.Tensor, tf.Tensor]:
        array, label = tf.py_function(_load, [path_tensor, label_tensor], [tf.float32, tf.int64])
        array.set_shape((*image_size, 3))
        label.set_shape(())
        return array, label

    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    if shuffle:
        ds = ds.shuffle(buffer_size=len(paths), seed=seed, reshuffle_each_iteration=True)
    # num_parallel_calls left at the default (sequential): the train-split
    # transform closes over a single shared numpy Generator, which is not
    # safe to call concurrently from multiple AUTOTUNE worker threads.
    ds = ds.map(_tf_load)
    ds = ds.batch(batch_size).prefetch(tf.data.AUTOTUNE)
    return ds, len(paths)
