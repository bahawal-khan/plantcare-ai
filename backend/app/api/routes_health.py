from fastapi import APIRouter, Request

from ..core.config import settings
from ..schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def get_health(request: Request) -> HealthResponse:
    model_service = getattr(request.app.state, "model_service", None)
    return HealthResponse(
        status="ok",
        model_loaded=model_service is not None,
        version=settings.app_version,
    )
