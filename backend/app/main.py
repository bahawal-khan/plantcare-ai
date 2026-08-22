import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import routes_diseases, routes_health, routes_model, routes_prediction
from .core.config import settings
from .core.errors import AppError
from .core.logging import configure_logging
from .services.model_service import ModelService

configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the model once at startup (CLAUDE.md rule 9 / ARCHITECTURE.md).
    # A missing/corrupt artifact must not crash the app -- health/model-info
    # /predict report a clean 503 instead (BACKEND_SPEC.md "Error Handling").
    try:
        app.state.model_service = ModelService.load(settings)
        logger.info("Model loaded from %s", settings.model_path)
    except AppError as exc:
        app.state.model_service = None
        logger.error("Model unavailable at startup: %s", exc.message)
    yield


app = FastAPI(title=settings.app_name, version=settings.app_version, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": exc.error_code, "detail": exc.message})


app.include_router(routes_health.router)
app.include_router(routes_model.router)
app.include_router(routes_prediction.router)
app.include_router(routes_diseases.router)
