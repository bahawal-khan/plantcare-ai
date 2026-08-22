# Production image for the FastAPI backend (Phase 12 — DEPLOYMENT_SPEC.md).
#
# Build context MUST be the repository root (not backend/), because the
# app imports the shared inference code in ml/src/* (ARCHITECTURE.md:
# "Training and inference preprocessing must share the same
# source/configuration"). See docker-compose.yml for the build context.
#
# Model artifacts (ml/artifacts/) and data (data/) are intentionally NOT
# copied into the image -- they are git-ignored and mounted as read-only
# volumes at runtime instead. See docs/DEPLOYMENT.md "Model Artifact
# Strategy" for why.

FROM python:3.11-slim

WORKDIR /app

# libgomp1 is required by the TensorFlow CPU wheel at import time.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies before copying source so `docker build` can reuse
# this layer as long as neither requirements file changes.
COPY ml/requirements.txt ml/requirements.txt
COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r ml/requirements.txt -r backend/requirements.txt

# Runtime source only -- no ml/scripts, ml/notebooks, or ml/configs
# training material, and no backend/tests (CLAUDE.md rule 8: ML training
# code stays separate from what actually ships).
COPY ml/__init__.py ml/__init__.py
COPY ml/src ml/src
COPY backend/app backend/app

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    UVICORN_WORKERS=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health', timeout=3)" || exit 1

# Single worker by default: the loaded EfficientNetB0 model is duplicated
# per worker process, so raise UVICORN_WORKERS only if the host has the
# spare memory (see docs/DEPLOYMENT.md "Resource Rules").
CMD uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS}
