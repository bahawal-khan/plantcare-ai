"""Class-name <-> integer-index mapping, saved as version-controlled JSON
per CLAUDE.md's "no database" rule (data/class_mapping.json).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable


def build_class_mapping(class_names: Iterable[str]) -> dict[str, int]:
    """Alphabetically-sorted class name -> index mapping (reproducible)."""
    unique_sorted = sorted(set(class_names))
    return {name: idx for idx, name in enumerate(unique_sorted)}


def save_class_mapping(mapping: dict[str, int], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(mapping, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def load_class_mapping(path: Path) -> dict[str, int]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
