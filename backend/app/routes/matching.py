from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.auth import CandidateUser, DatabaseSession
from app.matching import (
    build_ranking_context,
    parse_matching_intent,
    rank_jobs,
)
from app.models import CandidateProfile, Job, JobStatus
from app.schemas.matching import (
    InterpretedIntentResponse,
    JobMatchResponse,
    JobMatchResult,
    JobMatchRequest,
)


router = APIRouter(
    prefix="/matching",
    tags=["Matching"],
)


@router.post(
    "/jobs",
    response_model=JobMatchResponse,
)
def match_jobs(
    request: JobMatchRequest,
    candidate: CandidateUser,
    db: DatabaseSession,
) -> JobMatchResponse:
    profile = db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == candidate.id
        )
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate profile not found",
        )

    statement = (
        select(Job)
        .where(Job.status == JobStatus.OPEN.value)
        .order_by(Job.id)
    )

    jobs = list(db.scalars(statement).all())

    intent = parse_matching_intent(request.query)
    context = build_ranking_context(intent, profile)
    ranked_jobs = rank_jobs(jobs, context)

    matches = [
        JobMatchResult(
            job=ranked_job.job,
            match_score=ranked_job.match_score,
            explanation=ranked_job.explanation,
            matched_factors=ranked_job.matched_factors,
        )
        for ranked_job in ranked_jobs
    ]

    return JobMatchResponse(
        query=request.query,
        interpreted_intent=InterpretedIntentResponse(
            skills=intent.skills,
            role_types=intent.role_types,
            domains=intent.domains,
            locations=intent.locations,
            experience_levels=intent.experience_levels,
        ),
        matches=matches,
    )