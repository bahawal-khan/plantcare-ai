"""Reads disease/class records from the version-controlled JSON file.

Per PROJECT_SPEC.md section 4 and CLAUDE.md rule 6, V1 has no database:
``data/disease_info.json`` is the source of truth, loaded fresh on each
call (it is small, static configuration -- unlike the model, there is no
"load once" requirement for it).
"""

from __future__ import annotations

import json
from pathlib import Path


def load_diseases(disease_info_path: str | Path) -> list[dict]:
    path = Path(disease_info_path)
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def find_disease(diseases: list[dict], disease_id: str) -> dict | None:
    for record in diseases:
        if record.get("id") == disease_id:
            return record
    return None
