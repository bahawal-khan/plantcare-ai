from pydantic import BaseModel, ConfigDict


class DiseaseRecord(BaseModel):
    """A disease/healthy-class record from ``data/disease_info.json``.

    Fields follow PROJECT_SPEC.md section 11. Only ``id``, ``plant``, and
    ``name`` are required identifying fields; the rest are optional so this
    schema does not force content into records that don't have it yet
    (CLAUDE.md rule 5: do not invent disease facts). ``extra="allow"`` lets
    future, richer records pass through without a schema change.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    plant: str
    name: str
    description: str | None = None
    symptoms: list[str] | None = None
    causes: list[str] | None = None
    prevention: list[str] | None = None
    management: str | list[str] | None = None
    severity: str | None = None


class DiseaseListResponse(BaseModel):
    diseases: list[DiseaseRecord]
