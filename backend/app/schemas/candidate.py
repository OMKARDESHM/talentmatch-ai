from pydantic import BaseModel, ConfigDict, Field


class CandidateProfileUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    skills: str = Field(min_length=1, max_length=1000)
    education: str = Field(min_length=1, max_length=1000)
    project_summaries: str = Field(min_length=1, max_length=3000)
    preferred_location: str = Field(min_length=1, max_length=100)
    preferred_role_type: str = Field(min_length=1, max_length=100)
    domain_interest: str = Field(min_length=1, max_length=100)


class CandidateProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    skills: str
    education: str
    project_summaries: str
    preferred_location: str
    preferred_role_type: str
    domain_interest: str