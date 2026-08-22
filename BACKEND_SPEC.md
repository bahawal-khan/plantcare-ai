# PlantCare AI — FastAPI Backend Specification

## Mandatory Framework
Backend MUST use:
- FastAPI
- Pydantic
- Uvicorn
- python-multipart

Do not substitute another backend framework.

## Suggested Structure
```text
backend/
├── app/
│   ├── api/
│   │   ├── routes_health.py
│   │   ├── routes_model.py
│   │   ├── routes_prediction.py
│   │   └── routes_diseases.py
│   ├── core/
│   │   ├── config.py
│   │   └── logging.py
│   ├── schemas/
│   ├── services/
│   │   ├── model_service.py
│   │   ├── prediction_service.py
│   │   ├── gradcam_service.py
│   │   └── disease_service.py
│   └── main.py
└── tests/
```

## Endpoints

### GET /health
Returns:
- API status
- model_loaded boolean
- optional version

### GET /model-info
Returns:
- model name
- model version
- input size
- supported classes
- preprocessing metadata

### POST /predict
Multipart image upload.

Response:
- plant
- disease
- confidence
- top_k predictions where supported
- optional Grad-CAM image/reference

### GET /diseases
Returns supported disease records.

### GET /diseases/{disease_id}
Returns one disease record or 404.

## FastAPI Lifecycle
Use FastAPI lifespan/startup to initialize model services once.

Do not load TensorFlow model inside every request.

## Validation
- allowed image types
- maximum upload size
- valid image decoding
- RGB conversion
- clear errors

## CORS
Allow only configured frontend origins.

## Error Handling
Use structured responses for:
- invalid image
- oversized upload
- model unavailable
- unsupported class/artifact
- internal prediction errors

## No Database
No SQLAlchemy, SQLite, PostgreSQL, MySQL or prediction-history storage in V1.

## Testing
Use pytest and FastAPI TestClient/httpx as appropriate.
