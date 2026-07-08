from fastapi import APIRouter
from sqlalchemy import func, select

from app.auth import AdminUser, CandidateUser, DatabaseSession
from app.models import (
    Application,
    ApplicationStatus,
    CandidateProfile,
    Job,
    JobStatus,
)
from app.schemas.analytics import (
    AdminApplicationStats,
    AdminDashboardAnalytics,
    AdminJobStats,
    CandidateApplicationStats,
    CandidateDashboardAnalytics,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


def calculate_profile_completeness(
    profile: CandidateProfile,
) -> int:
    profile_fields = (
        profile.name,
        profile.skills,
        profile.education,
        profile.project_summaries,
        profile.preferred_location,
        profile.preferred_role_type,
        profile.domain_interest,
    )

    completed_fields = sum(
        1
        for value in profile_fields
        if value and value.strip()
    )

    return round(
        completed_fields / len(profile_fields) * 100
    )


@router.get(
    "/candidate/dashboard",
    response_model=CandidateDashboardAnalytics,
)
def get_candidate_dashboard_analytics(
    current_user: CandidateUser,
    db: DatabaseSession,
) -> CandidateDashboardAnalytics:
    profile = db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == current_user.id
        )
    )

    open_jobs = (
        db.scalar(
            select(func.count(Job.id)).where(
                Job.status == JobStatus.OPEN.value
            )
        )
        or 0
    )

    if profile is None:
        return CandidateDashboardAnalytics(
            applications=CandidateApplicationStats(
                total=0,
                applied=0,
                shortlisted=0,
                rejected=0,
            ),
            open_jobs=open_jobs,
            profile_completeness=0,
        )

    application_counts = dict(
        db.execute(
            select(
                Application.status,
                func.count(Application.id),
            )
            .where(
                Application.candidate_id == profile.id
            )
            .group_by(Application.status)
        ).all()
    )

    return CandidateDashboardAnalytics(
        applications=CandidateApplicationStats(
            total=sum(application_counts.values()),
            applied=application_counts.get(
                ApplicationStatus.APPLIED.value,
                0,
            ),
            shortlisted=application_counts.get(
                ApplicationStatus.SHORTLISTED.value,
                0,
            ),
            rejected=application_counts.get(
                ApplicationStatus.REJECTED.value,
                0,
            ),
        ),
        open_jobs=open_jobs,
        profile_completeness=(
            calculate_profile_completeness(profile)
        ),
    )


@router.get(
    "/admin/dashboard",
    response_model=AdminDashboardAnalytics,
)
def get_admin_dashboard_analytics(
    current_user: AdminUser,
    db: DatabaseSession,
) -> AdminDashboardAnalytics:
    job_counts = dict(
        db.execute(
            select(
                Job.status,
                func.count(Job.id),
            )
            .where(
                Job.created_by_id == current_user.id
            )
            .group_by(Job.status)
        ).all()
    )

    owned_job_ids = select(Job.id).where(
        Job.created_by_id == current_user.id
    )

    application_counts = dict(
        db.execute(
            select(
                Application.status,
                func.count(Application.id),
            )
            .where(
                Application.job_id.in_(owned_job_ids)
            )
            .group_by(Application.status)
        ).all()
    )

    return AdminDashboardAnalytics(
        jobs=AdminJobStats(
            total=sum(job_counts.values()),
            open=job_counts.get(
                JobStatus.OPEN.value,
                0,
            ),
            closed=job_counts.get(
                JobStatus.CLOSED.value,
                0,
            ),
        ),
        applications=AdminApplicationStats(
            total=sum(application_counts.values()),
            applied=application_counts.get(
                ApplicationStatus.APPLIED.value,
                0,
            ),
            shortlisted=application_counts.get(
                ApplicationStatus.SHORTLISTED.value,
                0,
            ),
            rejected=application_counts.get(
                ApplicationStatus.REJECTED.value,
                0,
            ),
        ),
    )
