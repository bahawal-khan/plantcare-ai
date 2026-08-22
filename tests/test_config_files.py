"""Phase 01 sanity tests: configuration/content files are syntactically
valid. Real disease content and class mapping are populated in later
phases (Phase 02 dataset acquisition onward), not invented here.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_class_mapping_is_valid_json_object():
    data = json.loads((ROOT / "data" / "class_mapping.json").read_text())
    assert isinstance(data, dict)


def test_disease_info_is_valid_json_array():
    data = json.loads((ROOT / "data" / "disease_info.json").read_text())
    assert isinstance(data, list)


def test_ml_config_is_valid_json_with_required_keys():
    data = json.loads((ROOT / "ml" / "configs" / "config.json").read_text())
    for key in ("seed", "image_size", "batch_size"):
        assert key in data
