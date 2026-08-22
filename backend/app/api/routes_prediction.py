from fastapi import APIRouter, File, Form, Request, UploadFile

from ..core.config import settings
from ..core.errors import ModelUnavailableError
from ..schemas.prediction import GradCAMResult, PredictionResponse, TopKPrediction, Visualization3D
from ..services import gradcam_service, prediction_service, validation
from ..services.model_service import ModelService

router = APIRouter(tags=["prediction"])


@router.post("/predict", response_model=PredictionResponse)
async def predict(
    request: Request,
    file: UploadFile = File(...),
    top_k: int = Form(default=settings.default_top_k),
    include_gradcam: bool = Form(default=False),
) -> PredictionResponse:
    model_service: ModelService | None = getattr(request.app.state, "model_service", None)
    if model_service is None:
        raise ModelUnavailableError("Model is not loaded")

    data = await file.read()
    image = validation.validate_and_decode_upload(
        data,
        file.content_type,
        settings.max_upload_size_bytes,
        settings.allowed_upload_content_types_set,
    )

    result = prediction_service.predict(model_service, image, top_k=top_k)

    gradcam: GradCAMResult | None = None
    if include_gradcam:
        payload = gradcam_service.generate_gradcam_payload(
            model_service, image, target_class=result.predicted_class_index
        )
        gradcam = GradCAMResult(
            predicted_class_index=payload["predicted_class_index"],
            predicted_class=payload["predicted_class"],
            confidence=payload["confidence"],
            target_layer=payload["target_layer"],
            heatmap_png_base64=payload["heatmap_png_base64"],
            overlay_png_base64=payload["overlay_png_base64"],
            visualization_3d=Visualization3D(**payload["visualization_3d"]),
            limitations=payload["limitations"],
        )

    return PredictionResponse(
        class_name=result.class_name,
        plant=result.plant,
        disease=result.disease,
        confidence=result.confidence,
        top_k=[TopKPrediction(**entry.__dict__) for entry in result.top_k],
        gradcam=gradcam,
    )
