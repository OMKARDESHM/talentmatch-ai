from fastapi import APIRouter
from sqlalchemy import text

from app.auth import DatabaseSession
from app.schemas.system import (
    HealthResponse,
    ReadinessResponse,
)


router = APIRouter(
    tags=["System"],
)


@router.get(
    "/health",
    response_model=HealthResponse,
)
def health_check() -> HealthResponse:
    return HealthResponse(status="healthy")


@router.get(
    "/ready",
    response_model=ReadinessResponse,
)
def readiness_check(
    db: DatabaseSession,
) -> ReadinessResponse:
    db.execute(text("SELECT 1"))

    return ReadinessResponse(
        status="ready",
        database="reachable",
    )
