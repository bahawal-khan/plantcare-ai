from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

from .conftest import make_test_image_bytes


def test_predict_rejects_unsupported_content_type(tiny_model_env):
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            files={"file": ("leaf.txt", b"not an image", "text/plain")},
        )

    assert response.status_code == 415
    assert response.json()["error"] == "unsupported_media_type"


def test_predict_rejects_undecodable_image_bytes(tiny_model_env):
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            files={"file": ("leaf.png", b"not actually a png", "image/png")},
        )

    assert response.status_code == 422
    assert response.json()["error"] == "invalid_image"


def test_predict_rejects_oversized_upload(tiny_model_env, monkeypatch):
    monkeypatch.setattr(settings, "max_upload_size_bytes", 100)

    with TestClient(app) as client:
        response = client.post(
            "/predict",
            files={"file": ("leaf.png", make_test_image_bytes(), "image/png")},
        )

    assert response.status_code == 413
    assert response.json()["error"] == "upload_too_large"


def test_predict_rejects_empty_upload(tiny_model_env):
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            files={"file": ("leaf.png", b"", "image/png")},
        )

    assert response.status_code == 422
    assert response.json()["error"] == "invalid_image"
