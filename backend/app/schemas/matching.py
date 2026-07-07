from pydantic import BaseModel, Field

from app.schemas.job import JobResponse


class JobMatchRequest(BaseModel):
    query: str = Field(
        min_length=3,
        max_length=1000,
    )


class InterpretedIntentResponse(BaseModel):
    skills: list[str]
    role_types: list[str]
    domains: list[str]
    locations: list[str]
    experience_levels: list[str]


class JobMatchResult(BaseModel):
    job: JobResponse
    match_score: int = Field(ge=0, le=100)
    explanation: str
    matched_factors: list[str]


class JobMatchResponse(BaseModel):
    query: str
    interpreted_intent: InterpretedIntentResponse
    matches: list[JobMatchResult]