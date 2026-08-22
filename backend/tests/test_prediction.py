from fastapi.testclient import TestClient

from app.main import app
from app.services.model_service import ModelService

from .conftest import make_test_image_bytes


def test_predict_accepts_valid_image_and_returns_required_fields(tiny_model_env):
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            files={"file": ("leaf.png", make_test_image_bytes(), "image/png")},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["class_name"] in tiny_model_env["class_names"]
    assert isinstance(body["plant"], str) and body["plant"]
    assert isinstance(body["disease"], str) and body["disease"]
    assert 0.0 <= body["confidence"] <= 1.0
    assert len(body["top_k"]) == len(tiny_model_env["class_names"])
    assert body["gradcam"] is None

    ranks = [entry["rank"] for entry in body["top_k"]]
    assert ranks == sorted(ranks)
    confidences = [entry["confidence"] for entry in body["top_k"]]
    assert confidences == sorted(confidences, reverse=True)


def test_predict_respects_top_k_parameter(tiny_model_env):
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            data={"top_k": "1"},
            files={"file": ("leaf.png", make_test_image_bytes(), "image/png")},
        )

    assert response.status_code == 200
    assert len(response.json()["top_k"]) == 1


def test_predict_class_name_splits_into_plant_and_disease(tiny_model_env):
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            files={"file": ("leaf.png", make_test_image_bytes(), "image/png")},
        )

    body = response.json()
    plant_raw, disease_raw = body["class_name"].split("___", 1)
    assert body["plant"] == plant_raw.replace("_", " ")
    expected_disease = disease_raw.replace("_", " ") or "Healthy"
    assert body["disease"] == expected_disease


def test_predict_returns_503_when_model_unavailable(missing_model_env):
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            files={"file": ("leaf.png", make_test_image_bytes(), "image/png")},
        )

    assert response.status_code == 503
    assert response.json()["error"] == "model_unavailable"


def test_predict_does_not_accept_a_server_file_path(tiny_model_env):
    """POST /predict only accepts multipart file bytes -- there is no field
    a client can use to make the server read an arbitrary local path
    (PHASE_08_BACKEND.md requirement 14 / CLAUDE.md rule 7).
    """
    with TestClient(app) as client:
        response = client.post("/predict", data={"path": "C:/Windows/win.ini"})

    assert response.status_code == 422  # missing required 'file' part


def test_model_is_loaded_once_not_per_request(tiny_model_env, monkeypatch):
    call_count = {"n": 0}
    original_load = ModelService.load

    def counting_load(settings):
        call_count["n"] += 1
        return original_load(settings)

    monkeypatch.setattr(ModelService, "load", staticmethod(counting_load))

    with TestClient(app) as client:
        for _ in range(3):
            response = client.post(
                "/predict",
                files={"file": ("leaf.png", make_test_image_bytes(), "image/png")},
            )
            assert response.status_code == 200

    assert call_count["n"] == 1
