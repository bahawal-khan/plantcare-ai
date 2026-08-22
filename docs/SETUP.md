# PlantCare AI — Local Setup (Phase 01)

This document covers environment setup established during Phase 01
(Project Setup). It will be extended in later phases as training,
the API, and the frontend are implemented.

## Prerequisites
- Python 3.11+
- Node.js 20+ / npm
- Git

## Environment variables
Copy `.env.example` to `.env` and adjust values as needed. Never commit
a real `.env` file (see `.gitignore`).

## ML environment
```bash
python -m venv ml/.venv
ml/.venv/Scripts/activate   # Windows
pip install -r ml/requirements.txt
pip install -r requirements-dev.txt
```

## Backend environment
```bash
python -m venv backend/.venv
backend/.venv/Scripts/activate   # Windows
pip install -r backend/requirements.txt
pip install -r requirements-dev.txt
```

## Frontend environment
```bash
cd frontend
npm install
```

## Running tests
```bash
# Repository structure / config sanity tests + backend app scaffold tests
pytest

# Frontend (once test tooling is added in Phase 09)
cd frontend && npm test
```

## Dataset (Phase 02)
```bash
python ml/scripts/acquire_dataset.py   # acquire PlantVillage raw/color (see docs/DATASET.md)
python ml/scripts/inspect_dataset.py   # count images/classes, detect corrupt/duplicate files
python ml/scripts/build_splits.py      # build train/val/test manifests + data/class_mapping.json
```
See `docs/DATASET.md` for the exact source, commit, license status, and
split strategy.

## Notes
- `data/class_mapping.json` is populated by `ml/scripts/build_splits.py`
  once the dataset is acquired (Phase 02); `data/disease_info.json`
  remains a placeholder (`[]`) — disease content is sourced in a later
  phase, per CLAUDE.md rule 5.
- `ml/artifacts/` and `data/raw/` and `data/processed/` are git-ignored;
  large binaries and datasets are never committed.
- Model training, FastAPI endpoints, and the Next.js pages are **not**
  implemented in this phase — see `phases/` for the remaining plan.
