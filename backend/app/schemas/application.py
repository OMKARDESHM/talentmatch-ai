from pydantic import BaseModel, ConfigDict

from app.models import ApplicationStatus
from app.schemas.common import UtcDateTime


class ApplicationCreate(BaseModel):
    job_id: int


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int
    job_id: int
    status: ApplicationStatus
    profile_snapshot: str
    applied_at: UtcDateTime
    updated_at: UtcDateTime