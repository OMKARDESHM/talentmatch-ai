from pydantic import BaseModel, Field


class CandidateApplicationStats(BaseModel):
    total: int = Field(ge=0)
    applied: int = Field(ge=0)
    shortlisted: int = Field(ge=0)
    rejected: int = Field(ge=0)


class CandidateDashboardAnalytics(BaseModel):
    applications: CandidateApplicationStats
    open_jobs: int = Field(ge=0)
    profile_completeness: int = Field(ge=0, le=100)


class AdminJobStats(BaseModel):
    total: int = Field(ge=0)
    open: int = Field(ge=0)
    closed: int = Field(ge=0)


class AdminApplicationStats(BaseModel):
    total: int = Field(ge=0)
    applied: int = Field(ge=0)
    shortlisted: int = Field(ge=0)
    rejected: int = Field(ge=0)


class AdminDashboardAnalytics(BaseModel):
    jobs: AdminJobStats
    applications: AdminApplicationStats
