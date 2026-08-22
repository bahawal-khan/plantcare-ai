# PlantCare AI — Testing Specification

## Unit Tests
Test:
- dataset discovery
- split logic
- class mapping
- preprocessing
- configuration
- disease JSON validation
- prediction formatting
- confidence/top-k formatting

## ML Smoke Tests
- model constructs
- forward pass succeeds
- output dimension equals class count
- save/load succeeds
- Grad-CAM smoke test succeeds on a sample

## FastAPI Tests
- /health
- /model-info
- /diseases
- /diseases/{id}
- valid /predict
- invalid image
- oversized upload
- missing model behavior
- response schema validation

## Frontend
Where practical test:
- upload validation
- loading/error/result states
- disease filtering
- API error handling

## Rules
- do not use the full dataset in unit tests
- use small fixtures
- do not modify tests merely to make them pass
- test changed behavior
- run full suite before release
