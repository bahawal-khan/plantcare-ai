# PlantCare AI

PlantCare AI is a deep learning web application that identifies plant
diseases from a single leaf photo. Upload an image and it returns the
predicted plant, disease, a confidence score, top-k alternatives, and a
Grad-CAM heatmap explaining which region of the leaf drove the
prediction.

Built end to end — dataset pipeline, transfer learning + fine-tuning,
Grad-CAM explainability, a FastAPI backend, and a Next.js frontend — as a
portfolio project demonstrating practical applied deep learning rather
than unnecessary enterprise complexity.

## Architecture

```text
                Browser
                   |
                   v
        Next.js Frontend (TypeScript)
                   |
              HTTPS / JSON
                   |
                   v
          FastAPI ASGI Backend
                   |
       +-----------+------------+
       |           |            |
       v           v            v
  Model Service  Disease JSON  Grad-CAM
       |
       v
 EfficientNetB0
       |
       v
 Model Artifact (ml/artifacts/stage2/best_model.keras)
```

- **No database.** Disease information and class metadata are
  version-controlled JSON (`data/disease_info.json`,
  `data/class_mapping.json`) — an intentional V1 decision, not an
  oversight. See `PROJECT_SPEC.md` §4.
- **CPU-only inference.** No part of the stack assumes GPU availability.
- Full rules and rationale: `ARCHITECTURE.md`, `CLAUDE.md`.

## Machine learning

- **Model:** EfficientNetB0, ImageNet-pretrained, transfer-learned then
  fine-tuned in two stages — Stage 1 trains a custom classification head
  on a frozen backbone; Stage 2 unfreezes a controlled upper portion of
  the backbone and fine-tunes at a substantially smaller learning rate.
  (`ML_SPEC.md`, `ml/src/models/efficientnet.py`, `ml/src/training/`)
- **Dataset:** PlantVillage (`raw/color` subset), acquired via a pinned
  git commit — 38 plant/disease classes across 14 plant species, split
  70/15/15 (train/val/test) with duplicate-content grouping so no image
  crosses a split boundary. Full provenance, license status, and
  known limitations: `docs/DATASET.md`.
- **Evaluation** (held-out test set, 8,147 images, untouched until final
  evaluation — see `ml/artifacts/evaluation/`):

  | Metric | Value |
  |---|---|
  | Accuracy | 98.78% |
  | Macro F1 | 98.55% |
  | Weighted F1 | 98.78% |

  Per-class precision/recall/F1, the confusion matrix, and the
  overfitting analysis are in `ml/artifacts/evaluation/`.
- **Explainability:** Grad-CAM heatmaps (`ml/src/explainability/gradcam.py`)
  are generated per prediction and returned as both a 2D overlay and an
  interactive 3D visualization. Grad-CAM is an interpretability aid, not
  proof of biological causation — this is stated in the UI, not just here.
- **Known limitation:** PlantVillage images are lab-condition photographs
  (uniform background, single detached leaf). Expect lower accuracy on
  real-world field photos (clutter, variable lighting, phone artifacts)
  than on this dataset's own test set.

## Backend (FastAPI)

| Endpoint | Purpose |
|---|---|
| `GET /health` | Liveness + whether the model is loaded |
| `GET /model-info` | Model name/version, input size, classes, preprocessing, evaluation metrics |
| `POST /predict` | Multipart image upload → prediction + top-k + optional Grad-CAM |
| `GET /diseases` | All supported disease records |
| `GET /diseases/{disease_id}` | One disease record, or 404 |

- The model is loaded once at FastAPI `lifespan` startup
  (`backend/app/main.py`, `backend/app/services/model_service.py`) — never
  per request.
- Uploads are validated by decoded content/type and size before touching
  the model (`backend/app/services/validation.py`).
- CORS is restricted to configured frontend origins
  (`BACKEND_CORS_ORIGINS`).
- Errors are structured JSON with the right HTTP status (model
  unavailable → 503, oversized upload → 413, invalid image → 422,
  unknown disease → 404) — see `backend/app/core/errors.py`.

Full endpoint contracts: `BACKEND_SPEC.md`.

## Frontend (Next.js + TypeScript)

Pages: Home, Diagnose, Diagnosis Result, Disease Library, Disease Detail,
How It Works, About — a premium AI + nature SaaS visual language shared
across all of them (`FRONTEND_SPEC.md`, `ui-references/`).

The API base URL is environment-configured
(`NEXT_PUBLIC_API_BASE_URL`, `frontend/src/lib/site-config.ts`) — never
hard-coded in components.

## Project layout

```text
PlantCare-AI/
├── ml/            # dataset pipeline, model, training, evaluation, Grad-CAM
├── backend/        # FastAPI app (routes -> services -> ml/src inference code)
├── frontend/        # Next.js app
├── data/           # disease_info.json, class_mapping.json (version-controlled)
├── docs/           # DATASET.md, SETUP.md, DEPLOYMENT.md
├── phases/         # the 12-phase implementation plan this repo was built from
└── tests/          # cross-cutting / dataset-pipeline tests (backend/frontend tests live alongside their app)
```

## Local development

```bash
# ML environment (dataset/training/evaluation)
python -m venv ml/.venv && ml/.venv/Scripts/activate   # Windows
pip install -r ml/requirements.txt -r requirements-dev.txt

# Backend
python -m venv backend/.venv && backend/.venv/Scripts/activate
pip install -r ml/requirements.txt -r backend/requirements.txt -r requirements-dev.txt
cp .env.example .env
PYTHONPATH=. uvicorn backend.app.main:app --reload

# Frontend
cd frontend
cp .env.example .env.local
npm install
npm run dev
```

Details, including dataset acquisition: `docs/SETUP.md`, `docs/DATASET.md`.

## Testing

```bash
pytest                    # dataset pipeline + ML + backend tests
cd frontend && npm test   # frontend unit tests
cd frontend && npm run build   # production build check
```

Testing conventions and coverage expectations: `TESTING_SPEC.md`.

## Deployment

The backend runs as a standard ASGI app
(`uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`); Docker
images are provided for both the backend (`backend/Dockerfile`) and
frontend (`frontend/Dockerfile`), orchestrated by `docker-compose.yml`.

```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 docker compose up --build
```

Model artifacts are git-ignored and mounted into the backend container
as a read-only volume rather than baked into the image — see
`docs/DEPLOYMENT.md` "Model Artifact Strategy" for why, and for the exact
Hostinger VPS deployment commands (Docker + nginx + certbot), production
environment variables, and cold-start behavior.

## Responsible use

Predictions and Grad-CAM explanations are decision-support aids for a
portfolio/research context, not a substitute for professional
agricultural or plant-pathology diagnosis. See the in-app disclaimer and
`docs/DATASET.md` "Known limitation".

## Specification package

This repository was built phase by phase from the specs in this root
(`PROJECT_SPEC.md`, `ARCHITECTURE.md`, `ML_SPEC.md`, `BACKEND_SPEC.md`,
`FRONTEND_SPEC.md`, `TESTING_SPEC.md`, `DEPLOYMENT_SPEC.md`) and
`phases/PHASE_01_PROJECT_SETUP.md` through
`phases/PHASE_12_DEPLOYMENT.md`, under the rules in `CLAUDE.md`.
