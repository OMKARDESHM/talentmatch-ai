from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import JobStatus


class JobCreateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=10)
    required_skills: str = Field(min_length=1)
    experience_level: str = Field(min_length=2, max_length=50)
    location: str = Field(min_length=2, max_length=150)
    role_type: str = Field(min_length=2, max_length=100)
    domain: str = Field(min_length=2, max_length=100)


class JobUpdateRequest(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(min_length=10)
    required_skills: str = Field(min_length=1)
    experience_level: str = Field(min_length=2, max_length=50)
    location: str = Field(min_length=2, max_length=150)
    role_type: str = Field(min_length=2, max_length=100)
    domain: str = Field(min_length=2, max_length=100)


class JobStatusUpdateRequest(BaseModel):
    status: JobStatus


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    required_skills: str
    experience_level: str
    location: str
    role_type: str
    domain: str
    status: str
    created_by_id: int
    created_at: datetime
    updated_at: datetime