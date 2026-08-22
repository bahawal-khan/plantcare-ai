from fastapi.testclient import TestClient

from app.main import app


def test_list_diseases_returns_fixture_records(tiny_model_env):
    with TestClient(app) as client:
        response = client.get("/diseases")

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["id"] == "apple-scab"
    assert body[0]["plant"] == "Apple"


def test_list_diseases_returns_empty_list_when_file_missing(tiny_model_env, tmp_path, monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "disease_info_path", str(tmp_path / "missing.json"))

    with TestClient(app) as client:
        response = client.get("/diseases")

    assert response.status_code == 200
    assert response.json() == []


def test_get_disease_by_id_returns_record(tiny_model_env):
    with TestClient(app) as client:
        response = client.get("/diseases/apple-scab")

    assert response.status_code == 200
    assert response.json()["name"] == "Apple Scab"


def test_get_unknown_disease_returns_404(tiny_model_env):
    with TestClient(app) as client:
        response = client.get("/diseases/does-not-exist")

    assert response.status_code == 404
    body = response.json()
    assert body["error"] == "disease_not_found"
