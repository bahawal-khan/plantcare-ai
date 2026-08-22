from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration convention, sourced from environment
    variables / .env. Endpoint and model-loading logic are implemented in
    Phase 08 (BACKEND_SPEC.md); this only establishes the config surface.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "PlantCare AI API"
    app_version: str = "0.1.0"
    backend_cors_origins: str = "http://localhost:3000"
    model_artifacts_dir: str = "ml/artifacts"
    max_upload_size_bytes: int = 5_242_880

    model_path: str = "ml/artifacts/stage2/best_model.keras"
    class_mapping_path: str = "data/class_mapping.json"
    disease_info_path: str = "data/disease_info.json"
    evaluation_metrics_path: str = "ml/artifacts/evaluation/metrics.json"
    allowed_upload_content_types: str = "image/jpeg,image/png,image/webp"
    default_top_k: int = 5

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    @property
    def allowed_upload_content_types_set(self) -> set[str]:
        return {
            content_type.strip().lower()
            for content_type in self.allowed_upload_content_types.split(",")
            if content_type.strip()
        }


settings = Settings()
