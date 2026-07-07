import json
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models import Application, Job, User
from app.schemas.admin_application import (
    AdminApplicationResponse,
    ApplicationStatusUpdate,
)

router = APIRouter(
    prefix="/admin/applications",
    tags=["Admin Applications"],
)


def get_owned_job(
    db: Session,
    job_id: int,
    admin_id: int,
) -> Job:
    job = db.scalar(
        select(Job).where(Job.id == job_id)
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if job.created_by_id != admin_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot manage this job",
        )

    return job


def serialize_application(
    application: Application,
) -> AdminApplicationResponse:
    try:
        profile_snapshot: dict[str, Any] = json.loads(
            application.profile_snapshot
        )
    except (json.JSONDecodeError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Application profile snapshot is invalid",
        ) from None

    return AdminApplicationResponse(
        id=application.id,
        candidate_id=application.candidate_id,
        job_id=application.job_id,
        status=application.status,
        profile_snapshot=profile_snapshot,
        applied_at=application.applied_at,
        updated_at=application.updated_at,
    )


@router.get(
    "/jobs/{job_id}",
    response_model=list[AdminApplicationResponse],
)
def read_job_applications(
    job_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> list[AdminApplicationResponse]:
    get_owned_job(db, job_id, current_user.id)

    applications = db.scalars(
        select(Application)
        .where(Application.job_id == job_id)
        .order_by(Application.applied_at.desc())
    ).all()

    return [
        serialize_application(application)
        for application in applications
    ]


@router.patch(
    "/{application_id}/status",
    response_model=AdminApplicationResponse,
)
def update_application_status(
    application_id: int,
    status_data: ApplicationStatusUpdate,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> AdminApplicationResponse:
    application = db.scalar(
        select(Application).where(
            Application.id == application_id
        )
    )

    if application is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )

    get_owned_job(
        db,
        application.job_id,
        current_user.id,
    )

    application.status = status_data.status.value

    db.commit()
    db.refresh(application)

    return serialize_application(application)