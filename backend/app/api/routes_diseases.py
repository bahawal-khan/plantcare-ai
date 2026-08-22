from fastapi import APIRouter

from ..core.config import settings
from ..core.errors import DiseaseNotFoundError
from ..schemas.disease import DiseaseRecord
from ..services import disease_service

router = APIRouter(tags=["diseases"])


@router.get("/diseases", response_model=list[DiseaseRecord])
async def list_diseases() -> list[dict]:
    return disease_service.load_diseases(settings.disease_info_path)


@router.get("/diseases/{disease_id}", response_model=DiseaseRecord)
async def get_disease(disease_id: str) -> dict:
    diseases = disease_service.load_diseases(settings.disease_info_path)
    record = disease_service.find_disease(diseases, disease_id)
    if record is None:
        raise DiseaseNotFoundError(f"No disease record with id {disease_id!r}")
    return record
