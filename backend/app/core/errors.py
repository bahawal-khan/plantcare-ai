"""Structured application errors.

Services raise these instead of generic exceptions so a single FastAPI
exception handler (wired in ``app/main.py``) can turn them into consistent
``{"error": ..., "detail": ...}`` JSON responses with the right HTTP status,
per BACKEND_SPEC.md "Error Handling" and CLAUDE.md rule 13 (structured
responses).
"""

from __future__ import annotations


class AppError(Exception):
    """Base class for errors that map to a structured HTTP response."""

    status_code: int = 500
    error_code: str = "internal_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ModelUnavailableError(AppError):
    """The trained model/artifacts could not be loaded or are not ready."""

    status_code = 503
    error_code = "model_unavailable"


class UnsupportedMediaTypeError(AppError):
    """The upload's content type is not an accepted image type."""

    status_code = 415
    error_code = "unsupported_media_type"


class InvalidImageError(AppError):
    """The upload could not be decoded as a valid image."""

    status_code = 422
    error_code = "invalid_image"


class UploadTooLargeError(AppError):
    """The upload exceeds the configured maximum size."""

    status_code = 413
    error_code = "upload_too_large"


class DiseaseNotFoundError(AppError):
    """No disease record matches the requested id."""

    status_code = 404
    error_code = "disease_not_found"
