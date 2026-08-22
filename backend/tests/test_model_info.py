from fastapi.testclient import TestClient

from app.main import app


def test_model_info_returns_expected_fields(tiny_model_env):
    with TestClient(app) as client:
        response = client.get("/model-info")

    assert response.status_code == 200
    body = response.json()
    assert body["model_name"] == "EfficientNetB0"
    assert body["num_classes"] == len(tiny_model_env["class_names"])
    assert body["supported_classes"] == tiny_model_env["class_names"]
    assert body["input_size"] == list(tiny_model_env["image_size"])
    assert body["target_layer"] == "top_activation"
    assert body["preprocessing"]["color_mode"] == "RGB"
    # No evaluation/metrics.json fixture was provided -- must not fabricate metrics.
    assert body["evaluation_accuracy"] is None
    assert body["evaluation_macro_f1"] is None


def test_model_info_returns_503_when_model_unavailable(missing_model_env):
    with TestClient(app) as client:
        response = client.get("/model-info")

    assert response.status_code == 503
    body = response.json()
    assert body["error"] == "model_unavailable"
