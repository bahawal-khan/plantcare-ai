# PlantCare AI — Architecture

## High-Level
```text
                Browser
                   |
                   v
        Next.js Frontend (Vercel)
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
 Model Artifact
```

## Repository
```text
PlantCare-AI/
├── ml/
│   ├── configs/
│   ├── src/
│   │   ├── data/
│   │   ├── preprocessing/
│   │   ├── models/
│   │   ├── training/
│   │   ├── evaluation/
│   │   ├── explainability/
│   │   └── inference/
│   ├── scripts/
│   ├── artifacts/
│   └── notebooks/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── disease_info.json
│   └── class_mapping.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   └── tests/
├── frontend/
├── tests/
├── docs/
├── phases/
├── ui-references/
├── CLAUDE.md
├── PROJECT_SPEC.md
└── README.md
```

## Architectural Rules
- FastAPI is the only backend framework.
- ML code never lives inside route functions.
- Routes call services.
- Model is loaded once, not per request.
- Disease content comes from JSON/configuration in V1.
- Frontend does not contain model logic.
- Training and inference preprocessing must share the same source/configuration.
