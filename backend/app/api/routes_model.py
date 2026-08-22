from fastapi import APIRouter, Request

from ..core.errors import ModelUnavailableError
from ..schemas.model_info import ModelInfoResponse, PreprocessingInfo
from ..services.model_service import ModelService

router = APIRouter(tags=["model"])


@router.get("/model-info", response_model=ModelInfoResponse)
async def get_model_info(request: Request) -> ModelInfoResponse:
    model_service: ModelService | None = getattr(request.app.state, "model_service", None)
    if model_service is None:
        raise ModelUnavailableError("Model is not loaded")

    metrics = model_service.evaluation_metrics or {}
    return ModelInfoResponse(
        model_name="EfficientNetB0",
        model_version=str(model_service.model_path),
        framework="tensorflow-keras",
        input_size=list(model_service.image_size),
        num_classes=model_service.num_classes,
        supported_classes=model_service.class_names,
        target_layer=model_service.target_layer,
        preprocessing=PreprocessingInfo(
            image_size=list(model_service.image_size),
            rescale="decoded to float32 in [0, 1]",
            color_mode="RGB",
        ),
        evaluation_accuracy=metrics.get("accuracy"),
        evaluation_macro_f1=metrics.get("macro", {}).get("f1"),
    )
