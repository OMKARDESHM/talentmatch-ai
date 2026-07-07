import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import require_candidate
from app.database import get_db
from app.models import (
    Application,
    ApplicationStatus,
    CandidateProfile,
    Job,
    JobStatus,
    User,
)
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
)

router = APIRouter(prefix="/applications", tags=["Applications"])


def get_candidate_profile(
    db: Session,
    user_id: int,
) -> CandidateProfile:
    profile = db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == user_id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found",
        )

    return profile


def create_profile_snapshot(
    profile: CandidateProfile,
) -> str:
    snapshot = {
        "name": profile.name,
        "skills": profile.skills,
        "education": profile.education,
        "project_summaries": profile.project_summaries,
        "preferred_location": profile.preferred_location,
        "preferred_role_type": profile.preferred_role_type,
        "domain_interest": profile.domain_interest,
    }

    return json.dumps(snapshot)


@router.post(
    "",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def apply_to_job(
    application_data: ApplicationCreate,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
) -> Application:
    profile = get_candidate_profile(db, current_user.id)

    job = db.scalar(
        select(Job).where(Job.id == application_data.job_id)
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if job.status != JobStatus.OPEN.value:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Job is closed",
        )

    existing_application = db.scalar(
        select(Application).where(
            Application.candidate_id == profile.id,
            Application.job_id == job.id,
        )
    )

    if existing_application is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied to this job",
        )

    application = Application(
        candidate_id=profile.id,
        job_id=job.id,
        status=ApplicationStatus.APPLIED.value,
        profile_snapshot=create_profile_snapshot(profile),
    )

    db.add(application)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already applied to this job",
        ) from None

    db.refresh(application)

    return application


@router.get(
    "/me",
    response_model=list[ApplicationResponse],
)
def read_candidate_applications(
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
) -> list[Application]:
    profile = get_candidate_profile(db, current_user.id)

    applications = db.scalars(
        select(Application)
        .where(Application.candidate_id == profile.id)
        .order_by(Application.applied_at.desc())
    ).all()

    return list(applications)