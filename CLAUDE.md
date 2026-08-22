# PlantCare AI — Claude Code Project Rules

## Source of Truth
Before implementation, read:
- PROJECT_SPEC.md
- ARCHITECTURE.md
- ML_SPEC.md
- BACKEND_SPEC.md
- FRONTEND_SPEC.md
- TESTING_SPEC.md
- DEPLOYMENT_SPEC.md

For UI work also inspect `ui-references/`.

## Core Rules
1. Implement only the requested phase.
2. Do not implement future phases prematurely.
3. Inspect the existing codebase before editing.
4. Preserve working functionality.
5. Do not invent requirements, model metrics, disease facts, or statistics.
6. Keep secrets out of source control.
7. Never use hard-coded machine-specific absolute paths.
8. Keep ML training code separate from FastAPI request handling.
9. Load the trained model once at application startup/lifespan where practical.
10. Validate uploaded files by content/type and enforce upload-size limits.
11. Keep training preprocessing and inference preprocessing consistent.
12. Do not use the test set for model selection or hyperparameter tuning.
13. Add or update tests for changed behavior.
14. Run relevant tests after each phase.
15. At the end of every phase, report:
   - files changed
   - tests executed
   - tests passed/failed
   - acceptance criteria status
   - remaining issues

## Backend Rule
The backend MUST be implemented with FastAPI. Do not replace it with Flask, Django, or another backend framework.

## Database Rule
Version 1 has NO database. Disease information and class metadata must use version-controlled JSON/configuration files. Do not introduce PostgreSQL, MySQL, SQLite, SQLAlchemy, authentication, or prediction-history storage unless a future explicit requirement is added.

## Deployment Rule
The backend must remain a normal FastAPI ASGI application and be deployable on a CPU-oriented environment. Do not assume a paid GPU.

## UI Rule
Use the UI reference images as design direction, not as literal assets to copy. Maintain a consistent premium AI + nature SaaS visual language across pages.
