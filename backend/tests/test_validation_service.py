"""Unit tests for app.services.validation, independent of FastAPI routing."""

import pytest

from app.core.errors import InvalidImageError, UnsupportedMediaTypeError, UploadTooLargeError
from app.services.validation import validate_and_decode_upload

from .conftest import make_test_image_bytes

ALLOWED = {"image/jpeg", "image/png", "image/webp"}


def test_valid_png_decodes_and_converts_to_rgb():
    image = validate_and_decode_upload(make_test_image_bytes(), "image/png", 5_000_000, ALLOWED)
    assert image.mode == "RGB"


def test_wrong_content_type_raises_unsupported_media_type():
    with pytest.raises(UnsupportedMediaTypeError):
        validate_and_decode_upload(b"data", "application/pdf", 5_000_000, ALLOWED)


def test_missing_content_type_raises_unsupported_media_type():
    with pytest.raises(UnsupportedMediaTypeError):
        validate_and_decode_upload(make_test_image_bytes(), None, 5_000_000, ALLOWED)


def test_undecodable_bytes_raise_invalid_image_error():
    with pytest.raises(InvalidImageError):
        validate_and_decode_upload(b"garbage-not-an-image", "image/png", 5_000_000, ALLOWED)


def test_empty_bytes_raise_invalid_image_error():
    with pytest.raises(InvalidImageError):
        validate_and_decode_upload(b"", "image/png", 5_000_000, ALLOWED)


def test_oversized_upload_raises_upload_too_large_error():
    data = make_test_image_bytes()
    with pytest.raises(UploadTooLargeError):
        validate_and_decode_upload(data, "image/png", max_size_bytes=len(data) - 1, allowed_content_types=ALLOWED)
