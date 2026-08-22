import base64
import io

from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from ml.src.explainability.gradcam import RESPONSIBLE_USE_NOTE

from .conftest import make_test_image_bytes


def test_predict_without_gradcam_flag_omits_gradcam(tiny_model_env):
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            files={"file": ("leaf.png", make_test_image_bytes(), "image/png")},
        )

    assert response.status_code == 200
    assert response.json()["gradcam"] is None


def test_predict_with_gradcam_flag_returns_2d_and_3d_payload(tiny_model_env):
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            data={"include_gradcam": "true"},
            files={"file": ("leaf.png", make_test_image_bytes(), "image/png")},
        )

    assert response.status_code == 200
    body = response.json()
    gradcam = body["gradcam"]
    assert gradcam is not None

    # 2D Grad-CAM output.
    assert gradcam["predicted_class"] in tiny_model_env["class_names"]
    assert gradcam["target_layer"] == "top_activation"
    heatmap_bytes = base64.b64decode(gradcam["heatmap_png_base64"])
    with Image.open(io.BytesIO(heatmap_bytes)) as img:
        assert img.size == tuple(tiny_model_env["image_size"])
    overlay_bytes = base64.b64decode(gradcam["overlay_png_base64"])
    with Image.open(io.BytesIO(overlay_bytes)) as img:
        assert img.size == tuple(tiny_model_env["image_size"])

    # Required interactive 3D visualization data (PHASE_08_BACKEND.md req. 7/9).
    viz = gradcam["visualization_3d"]
    grid = viz["grid_size"]
    assert len(viz["heightmap"]) == grid[0]
    assert all(len(row) == grid[1] for row in viz["heightmap"])
    assert all(0.0 <= v <= 1.0 for row in viz["heightmap"] for v in row)
    texture_bytes = base64.b64decode(viz["texture_png_base64"])
    with Image.open(io.BytesIO(texture_bytes)) as img:
        assert img.size == tuple(tiny_model_env["image_size"])

    # Must not claim biological 3D localization (PHASE_07/08 responsible-use rule).
    assert viz["is_biological_reconstruction"] is False
    assert "biological" in viz["limitations"].lower()
    assert gradcam["limitations"] == RESPONSIBLE_USE_NOTE


def test_gradcam_visualization_matches_predicted_class(tiny_model_env):
    """The 3D payload must correspond to the same prediction as the 2D
    Grad-CAM result, not a separate/fabricated one.
    """
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            data={"include_gradcam": "true"},
            files={"file": ("leaf.png", make_test_image_bytes(), "image/png")},
        )

    gradcam = response.json()["gradcam"]
    assert gradcam["visualization_3d"]["predicted_class_index"] == gradcam["predicted_class_index"]
    assert gradcam["visualization_3d"]["confidence"] == gradcam["confidence"]
