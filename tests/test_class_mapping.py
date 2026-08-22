"""Phase 02 tests: class mapping construction and JSON persistence."""

import json
from pathlib import Path

from ml.src.data.class_mapping import build_class_mapping, load_class_mapping, save_class_mapping


def test_build_class_mapping_is_alphabetical_and_zero_indexed():
    mapping = build_class_mapping(["Tomato___Late_blight", "Apple___healthy", "Corn___rust"])
    assert mapping == {
        "Apple___healthy": 0,
        "Corn___rust": 1,
        "Tomato___Late_blight": 2,
    }


def test_build_class_mapping_deduplicates():
    mapping = build_class_mapping(["A", "A", "B"])
    assert mapping == {"A": 0, "B": 1}


def test_save_and_load_class_mapping_roundtrip(tmp_path: Path):
    mapping = build_class_mapping(["Healthy", "Diseased"])
    out_path = tmp_path / "class_mapping.json"
    save_class_mapping(mapping, out_path)

    loaded = load_class_mapping(out_path)
    assert loaded == mapping

    raw = json.loads(out_path.read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
