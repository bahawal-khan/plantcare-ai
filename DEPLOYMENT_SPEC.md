# PlantCare AI — Deployment Specification

## Architecture
- Frontend: deploy separately from backend.
- Backend: FastAPI ASGI application.
- Model: CPU inference.
- No database in V1.

## Backend Deployment Requirements
The deployed backend must run:
```text
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```
or the platform's equivalent ASGI startup command.

The exact platform must be checked during Phase 12 because free-tier policies can change.

## Resource Rules
- keep upload size limited
- keep input resolution controlled
- load model once
- avoid GPU-only assumptions
- document cold-start/model-loading behavior

## Frontend
Configure an environment variable such as:
`NEXT_PUBLIC_API_BASE_URL`

Do not hard-code production API URLs throughout components.

## Security
- no secrets in Git
- CORS configured
- upload validation
- reasonable rate/resource controls
- no arbitrary file paths

## Release
Document:
- local setup
- training
- artifact placement
- backend start
- frontend start
- environment variables
- deployment
- limitations
