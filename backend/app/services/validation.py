"""Upload validation for ``POST /predict``.

Per BACKEND_SPEC.md "Validation" and CLAUDE.md rule 10: check content type,
enforce a maximum size, and confirm the bytes actually decode as an image
before handing anything to the model. Accepts only in-memory bytes from a
multipart upload -- never a server file path (CLAUDE.md rule 7 /
PHASE_08_BACKEND.md requirement 14).
"""

from __future__ import annotations

import io

from PIL import Image, UnidentifiedImageError

from ..core.errors import InvalidImageError, UnsupportedMediaTypeError, UploadTooLargeError


def validate_and_decode_upload(
    data: bytes,
    content_type: str | None,
    max_size_bytes: int,
    allowed_content_types: set[str],
) -> Image.Image:
    if content_type is None or content_type.lower() not in allowed_content_types:
        raise UnsupportedMediaTypeError(
            f"Unsupported content type {content_type!r}; expected one of {sorted(allowed_content_types)}"
        )

    if not data:
        raise InvalidImageError("Uploaded file is empty")

    if len(data) > max_size_bytes:
        raise UploadTooLargeError(f"Upload exceeds maximum size of {max_size_bytes} bytes")

    try:
        image = Image.open(io.BytesIO(data))
        image.load()  # force full decode now so truncated/corrupt files fail here, not later
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise InvalidImageError("File could not be decoded as a valid image") from exc

    return image.convert("RGB")
