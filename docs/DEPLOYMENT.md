# PlantCare AI — Deployment (Phase 12)

This document covers production configuration, the model artifact
strategy, Docker usage, and the exact steps to deploy PlantCare AI to a
Hostinger VPS. See `DEPLOYMENT_SPEC.md` for the governing requirements.

## Architecture recap

- Frontend (Next.js) and backend (FastAPI) are deployed as two separate
  processes/containers, per `ARCHITECTURE.md`.
- No database in V1 — disease content and class metadata are
  version-controlled JSON (`data/disease_info.json`,
  `data/class_mapping.json`).
- Inference is CPU-only; nothing in this stack assumes GPU availability.

## Platform decision

`DEPLOYMENT_SPEC.md` requires the exact free-tier platform to be verified
during this phase, because policies change. As of this phase, the common
"free tier" PaaS options (Render, Railway, Fly.io, Vercel for
non-frontend workloads) either cap RAM below what a TensorFlow CPU
process comfortably uses once the EfficientNetB0 model is loaded, spin
containers down aggressively (bad for a demo — every cold request pays
full model-load latency), or require a paid plan for always-on backend
workers with the traffic-controlled resource footprint this app needs.

This project targets a **Hostinger VPS** instead: a normal Linux server
with full control over memory, disk, and process lifetime, running the
backend and frontend as Docker containers behind nginx. The frontend can
still be deployed separately to Vercel's free tier if preferred (it has
no server-side ML dependency) — the steps below assume both run on the
same VPS for a single, fully self-hosted deployment.

## Production configuration

### Backend environment variables
Copy `.env.example` to `.env` on the server and set real values. Defaults
already match the repository layout; the only value that typically
changes in production is CORS:

| Variable | Production value |
|---|---|
| `BACKEND_CORS_ORIGINS` | The real frontend origin(s), e.g. `https://your-domain.com` — never `*` |
| `MODEL_ARTIFACTS_DIR` / `MODEL_PATH` / `CLASS_MAPPING_PATH` / `DISEASE_INFO_PATH` / `EVALUATION_METRICS_PATH` | Leave as-is; paths are relative to the container's `/app` and resolved via the bind mounts in `docker-compose.yml` |
| `MAX_UPLOAD_SIZE_BYTES` | Keep aligned with nginx's `client_max_body_size` (see `deploy/nginx.conf.example`) |

`.env` is git-ignored (see `.gitignore`); only `.env.example` is
committed. No secrets are committed to source control.

### Frontend environment variable
`NEXT_PUBLIC_API_BASE_URL` (see `frontend/.env.example`) points the
frontend at the backend's public URL. Next.js inlines
`NEXT_PUBLIC_*` variables into the client bundle **at build time**, so it
must be set before `npm run build` / `docker build` — not just at
container runtime. `frontend/Dockerfile` accepts it as a build `ARG`;
`docker-compose.yml` passes it through from the shell environment.

## Model artifact strategy

Trained model artifacts (`ml/artifacts/stage2/best_model.keras`, ~41 MB)
are **git-ignored** (`.gitignore`: `*.keras`, `ml/artifacts/*`) — they are
binary training outputs, not source code, and do not belong in version
control.

Deployment therefore treats the artifact as a build input that travels
with the server filesystem, not with the Docker image:

1. Train locally (or in a separate ML environment) via the Phase 03–07
   pipeline; this produces `ml/artifacts/stage2/best_model.keras`,
   `ml/artifacts/stage2/config.json`, and
   `ml/artifacts/evaluation/metrics.json`.
2. Copy `ml/artifacts/` and `data/` to the VPS with `rsync`/`scp`
   alongside the rest of the repository (exact commands below).
3. `backend/Dockerfile` does **not** `COPY` `ml/artifacts/` or `data/`
   into the image. `docker-compose.yml` bind-mounts both directories
   read-only into the container instead.

This keeps the image small and lets you swap in a retrained model
(replace the file on the host, `docker compose restart backend`) without
rebuilding the image. If the artifact is ever missing on the host, the
backend's lifespan handler catches this at startup (`ModelUnavailableError`)
and the app still starts — `/health` reports `model_loaded: false` and
`/predict` returns a structured 503 instead of crashing (see
`backend/app/main.py`, `BACKEND_SPEC.md` "Error Handling").

## Docker

### Build and run locally
```bash
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 docker compose up --build
```
- Backend: http://localhost:8000 (`/health`, `/docs`)
- Frontend: http://localhost:3000

### Images
- `backend/Dockerfile` — `python:3.11-slim`, installs `ml/requirements.txt`
  + `backend/requirements.txt` (the backend imports shared inference code
  from `ml/src/*`, so both are required at runtime), copies only
  `backend/app` and `ml/src`, runs
  `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000`.
- `frontend/Dockerfile` — multi-stage Next.js build using `output:
  "standalone"` (`frontend/next.config.ts`), runs `node server.js`.

Both images define a `HEALTHCHECK`.

## FastAPI ASGI startup (no Docker)

Equivalent to what the backend image runs, for a bare VPS or any ASGI
host:
```bash
# from the repository root, with backend/requirements.txt and
# ml/requirements.txt installed into the active environment
PYTHONPATH=. uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --workers 1
```
`PYTHONPATH=.` is required so `ml.src.*` (shared preprocessing/model
code) resolves the same way it does in the Docker image. Keep
`--workers 1` unless the host has enough spare memory to hold one loaded
EfficientNetB0 model per worker process — the model is loaded once per
process, not shared across workers.

## Health check

`GET /health` returns `{"status": "ok", "model_loaded": bool, "version":
str}` and is used by the Docker `HEALTHCHECK`, and should be pointed at
by any external uptime monitor.

## Hostinger VPS deployment (exact commands)

Assumes an Ubuntu 22.04+ Hostinger VPS, a domain's DNS already pointed at
the VPS's IP, and SSH access as a non-root sudo user.

### 1. Install Docker
```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Copy the repository and trained artifacts
From your local machine (where training already produced
`ml/artifacts/`):
```bash
rsync -avz --exclude 'node_modules' --exclude '.next' --exclude '.git' \
  ./ your-user@your-vps-ip:/opt/plantcare-ai/
```
This single command carries the source code **and** `ml/artifacts/` +
`data/` together, since they're plain files on your local disk even
though Git ignores them.

### 3. Configure environment
```bash
ssh your-user@your-vps-ip
cd /opt/plantcare-ai
cp .env.example .env
# edit .env: set BACKEND_CORS_ORIGINS=https://your-domain.com
export NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com
```

### 4. Build and start the containers
```bash
docker compose up -d --build
docker compose ps
curl http://localhost:8000/health
```

### 5. Install and configure nginx + TLS
```bash
sudo apt-get update && sudo apt-get install -y nginx certbot python3-certbot-nginx
sudo cp deploy/nginx.conf.example /etc/nginx/sites-available/plantcare-ai
sudo nano /etc/nginx/sites-available/plantcare-ai   # replace your-domain.com / api.your-domain.com
sudo ln -s /etc/nginx/sites-available/plantcare-ai /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d your-domain.com -d api.your-domain.com
```

### 6. Verify
```bash
curl https://api.your-domain.com/health
curl https://your-domain.com
```
Open `https://your-domain.com/diagnose` in a browser and run a real
prediction end to end.

### Redeploying after a model retrain or code change
```bash
rsync -avz --exclude 'node_modules' --exclude '.next' --exclude '.git' \
  ./ your-user@your-vps-ip:/opt/plantcare-ai/
ssh your-user@your-vps-ip 'cd /opt/plantcare-ai && docker compose up -d --build'
```

## Cold start behavior

The backend loads the EfficientNetB0 checkpoint once during the FastAPI
`lifespan` handler (`backend/app/main.py`), before the process starts
accepting requests — so there is no per-request "cold model" penalty
once the container is up. The cost is entirely at container start: model
deserialization typically takes several seconds on a CPU-only VPS.
`docker compose up -d` returns immediately; give the backend container a
few seconds before the first request, which the `HEALTHCHECK` /
`docker compose ps` status reflects.

## Limitations

- Trained on PlantVillage's lab-condition photographs (see
  `docs/DATASET.md` "Known limitation") — expect lower real-world
  accuracy on cluttered/field photos than on the held-out test set.
- Grad-CAM is an interpretability aid, not proof of biological causation
  (`PROJECT_SPEC.md` §8).
- Single-VPS deployment with no autoscaling; `--workers 1` by default
  trades request concurrency for memory headroom appropriate to a
  portfolio-scale deployment, not production traffic volumes.
- No database/authentication/prediction history in V1 (`PROJECT_SPEC.md`
  §4) — nothing here changes that.
