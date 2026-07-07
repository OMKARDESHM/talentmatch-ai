from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from app.models import ApplicationStatus


class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus


class AdminApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    candidate_id: int
    job_id: int
    status: ApplicationStatus
    profile_snapshot: dict[str, Any]
    applied_at: datetime
    updated_at: datetime