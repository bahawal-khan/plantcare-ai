from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """GET /health response, per BACKEND_SPEC.md."""

    status: str = Field(description="Overall API status, e.g. 'ok'.")
    model_loaded: bool = Field(description="Whether the trained model is loaded and ready.")
    version: str = Field(description="Application version.")
