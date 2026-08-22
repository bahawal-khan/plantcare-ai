from pydantic import BaseModel, Field


class TopKPrediction(BaseModel):
    rank: int
    class_name: str = Field(description="Raw 'Plant___Disease' class label from class_mapping.json.")
    plant: str
    disease: str
    confidence: float = Field(ge=0.0, le=1.0)


class Visualization3D(BaseModel):
    """Interactive 3D Grad-CAM visualization data contract, per
    PHASE_07_GRAD_CAM.md requirement 12 / PHASE_08_BACKEND.md requirements
    6-9. This is only an interactive rendering of the real 2D Grad-CAM
    heatmap -- never a biological 3D reconstruction (see
    ``is_biological_reconstruction`` and ``limitations``).
    """

    target_layer: str
    predicted_class_index: int
    confidence: float = Field(ge=0.0, le=1.0)
    grid_size: list[int]
    heightmap: list[list[float]] = Field(description="grid_size x grid_size intensity grid derived from the real Grad-CAM heatmap.")
    texture_png_base64: str = Field(description="Base64 PNG of the Grad-CAM overlay, used as the 3D surface texture.")
    colormap: str
    is_biological_reconstruction: bool = Field(description="Always false: not true 3D disease localization.")
    limitations: str


class GradCAMResult(BaseModel):
    """Actual Grad-CAM output for this prediction -- 2D heatmap/overlay plus
    the 3D visualization data derived from it. Never a fabricated/separate
    disease visualization, per PHASE_08_BACKEND.md requirement 8.
    """

    predicted_class_index: int
    predicted_class: str | None
    confidence: float = Field(ge=0.0, le=1.0)
    target_layer: str
    heatmap_png_base64: str
    overlay_png_base64: str
    visualization_3d: Visualization3D
    limitations: str


class PredictionResponse(BaseModel):
    """POST /predict response, per BACKEND_SPEC.md."""

    class_name: str = Field(description="Raw 'Plant___Disease' class label from class_mapping.json.")
    plant: str
    disease: str
    confidence: float = Field(ge=0.0, le=1.0)
    top_k: list[TopKPrediction]
    gradcam: GradCAMResult | None = Field(default=None, description="Present only when Grad-CAM was requested.")
