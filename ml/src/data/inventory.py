"""Dataset discovery and inspection utilities.

Operates on an "ImageFolder"-style layout (``root/<class_name>/<image>``),
which matches the PlantVillage ``raw/color`` directory structure. Used by
``ml/scripts/inspect_dataset.py`` and ``ml/scripts/build_splits.py``; kept
free of any ML-framework dependency (Pillow/numpy only) per CLAUDE.md rule 8.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, UnidentifiedImageError

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".bmp", ".gif", ".JPG", ".JPEG", ".PNG")


@dataclass(frozen=True)
class ImageRecord:
    path: Path
    class_name: str


@dataclass
class DatasetReport:
    root: Path
    total_images: int
    class_counts: dict[str, int]
    corrupt_files: list[Path] = field(default_factory=list)
    duplicate_content_groups: dict[str, list[Path]] = field(default_factory=dict)
    duplicate_filename_groups: dict[str, list[Path]] = field(default_factory=dict)

    @property
    def num_classes(self) -> int:
        return len(self.class_counts)


def discover_images(root: Path) -> list[ImageRecord]:
    """Discover images laid out as ``root/<class_name>/<image_file>``.

    Class directories are visited in sorted order so results are
    deterministic across runs/platforms.
    """
    root = Path(root)
    records: list[ImageRecord] = []
    if not root.is_dir():
        return records
    for class_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        for image_path in sorted(class_dir.rglob("*")):
            if image_path.is_file() and image_path.suffix in IMAGE_EXTENSIONS:
                records.append(ImageRecord(path=image_path, class_name=class_dir.name))
    return records


def class_distribution(records: list[ImageRecord]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for record in records:
        counts[record.class_name] = counts.get(record.class_name, 0) + 1
    return dict(sorted(counts.items()))


def sha256_of_file(path: Path, chunk_size: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_corrupt_image(path: Path) -> bool:
    """Return True if the file cannot be decoded as a valid image.

    Uses a two-pass check: ``verify()`` catches structurally broken files,
    but invalidates the file handle, so a second open+decode pass is
    required to also catch truncated pixel data that ``verify()`` misses.
    """
    try:
        with Image.open(path) as img:
            img.verify()
        with Image.open(path) as img:
            img.convert("RGB").load()
        return False
    except (UnidentifiedImageError, OSError, ValueError):
        return True


def find_corrupt_images(records: list[ImageRecord]) -> list[Path]:
    return [r.path for r in records if is_corrupt_image(r.path)]


def find_duplicate_content(
    records: list[ImageRecord], hashes: dict[Path, str] | None = None
) -> dict[str, list[Path]]:
    """Group images by content hash; returns only groups with >1 member."""
    by_hash: dict[str, list[Path]] = {}
    for record in records:
        digest = hashes[record.path] if hashes is not None else sha256_of_file(record.path)
        by_hash.setdefault(digest, []).append(record.path)
    return {h: paths for h, paths in by_hash.items() if len(paths) > 1}


def find_duplicate_filenames(records: list[ImageRecord]) -> dict[str, list[Path]]:
    by_name: dict[str, list[Path]] = {}
    for record in records:
        by_name.setdefault(record.path.name, []).append(record.path)
    return {name: paths for name, paths in by_name.items() if len(paths) > 1}


def inspect_dataset(root: Path, compute_hashes: bool = True) -> DatasetReport:
    root = Path(root)
    records = discover_images(root)
    hashes = None
    duplicate_content: dict[str, list[Path]] = {}
    if compute_hashes:
        hashes = {r.path: sha256_of_file(r.path) for r in records}
        duplicate_content = find_duplicate_content(records, hashes)
    return DatasetReport(
        root=root,
        total_images=len(records),
        class_counts=class_distribution(records),
        corrupt_files=find_corrupt_images(records),
        duplicate_content_groups=duplicate_content,
        duplicate_filename_groups=find_duplicate_filenames(records),
    )
