from pydantic import BaseModel, Field


class PreprocessingInfo(BaseModel):
    image_size: list[int] = Field(description="[width, height] the model expects.")
    rescale: str = Field(description="Pixel value convention applied before the model's internal rescaling.")
    color_mode: str


class ModelInfoResponse(BaseModel):
    """GET /model-info response, per BACKEND_SPEC.md.

    ``evaluation_accuracy``/``evaluation_macro_f1`` are read from the Phase 06
    evaluation report when available and omitted (``None``) rather than
    fabricated when it is not, per CLAUDE.md rule 5.
    """

    model_name: str
    model_version: str = Field(description="Identifier for the loaded checkpoint, e.g. its artifact path.")
    framework: str
    input_size: list[int] = Field(description="[width, height] the model expects.")
    num_classes: int
    supported_classes: list[str]
    target_layer: str = Field(description="Grad-CAM target layer, see PHASE_07_GRAD_CAM.md.")
    preprocessing: PreprocessingInfo
    evaluation_accuracy: float | None = None
    evaluation_macro_f1: float | None = None
