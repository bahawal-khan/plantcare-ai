from fastapi.testclient import TestClient

from app.main import app


def test_health_reports_model_loaded_when_model_available(tiny_model_env):
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["model_loaded"] is True
    assert "version" in body


def test_health_reports_model_not_loaded_when_model_missing(missing_model_env):
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["model_loaded"] is False
