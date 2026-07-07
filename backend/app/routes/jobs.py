from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.auth import AdminUser, CurrentUser, DatabaseSession
from app.models import Job, JobStatus
from app.schemas.job import (
    JobCreateRequest,
    JobResponse,
    JobStatusUpdateRequest,
    JobUpdateRequest,
)


router = APIRouter(
    tags=["Jobs"],
)


def get_owned_job(
    job_id: int,
    admin_id: int,
    db: DatabaseSession,
) -> Job:
    job = db.get(Job, job_id)

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


@router.post(
    "/jobs",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    request: JobCreateRequest,
    admin: AdminUser,
    db: DatabaseSession,
) -> Job:
    job = Job(
        title=request.title,
        description=request.description,
        required_skills=request.required_skills,
        experience_level=request.experience_level,
        location=request.location,
        role_type=request.role_type,
        domain=request.domain,
        status=JobStatus.OPEN.value,
        created_by_id=admin.id,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


@router.get(
    "/jobs",
    response_model=list[JobResponse],
)
def list_open_jobs(
    current_user: CurrentUser,
    db: DatabaseSession,
    skill: Annotated[str | None, Query(min_length=1)] = None,
    location: Annotated[str | None, Query(min_length=1)] = None,
    experience_level: Annotated[
        str | None,
        Query(min_length=1),
    ] = None,
) -> list[Job]:
    statement = (
        select(Job)
        .where(Job.status == JobStatus.OPEN.value)
        .order_by(Job.created_at.desc(), Job.id.desc())
    )

    if skill:
        statement = statement.where(
            func.lower(Job.required_skills).contains(skill.lower())
        )

    if location:
        statement = statement.where(
            func.lower(Job.location) == location.lower()
        )

    if experience_level:
        statement = statement.where(
            func.lower(Job.experience_level)
            == experience_level.lower()
        )

    return list(db.scalars(statement).all())


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
)
def get_job(
    job_id: int,
    current_user: CurrentUser,
    db: DatabaseSession,
) -> Job:
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if (
        job.status == JobStatus.CLOSED.value
        and job.created_by_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return job


@router.put(
    "/jobs/{job_id}",
    response_model=JobResponse,
)
def update_job(
    job_id: int,
    request: JobUpdateRequest,
    admin: AdminUser,
    db: DatabaseSession,
) -> Job:
    job = get_owned_job(job_id, admin.id, db)

    job.title = request.title
    job.description = request.description
    job.required_skills = request.required_skills
    job.experience_level = request.experience_level
    job.location = request.location
    job.role_type = request.role_type
    job.domain = request.domain

    db.commit()
    db.refresh(job)

    return job


@router.patch(
    "/jobs/{job_id}/status",
    response_model=JobResponse,
)
def update_job_status(
    job_id: int,
    request: JobStatusUpdateRequest,
    admin: AdminUser,
    db: DatabaseSession,
) -> Job:
    job = get_owned_job(job_id, admin.id, db)

    job.status = request.status.value

    db.commit()
    db.refresh(job)

    return job


@router.get(
    "/admin/jobs",
    response_model=list[JobResponse],
    tags=["Admin"],
)
def list_admin_jobs(
    admin: AdminUser,
    db: DatabaseSession,
) -> list[Job]:
    statement = (
        select(Job)
        .where(Job.created_by_id == admin.id)
        .order_by(Job.created_at.desc(), Job.id.desc())
    )

    return list(db.scalars(statement).all())