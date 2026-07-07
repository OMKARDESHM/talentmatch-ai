from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import require_candidate
from app.database import get_db
from app.models import CandidateProfile, User
from app.schemas.candidate import (
    CandidateProfileResponse,
    CandidateProfileUpdate,
)

router = APIRouter(prefix="/candidates", tags=["Candidates"])


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


@router.get(
    "/me",
    response_model=CandidateProfileResponse,
)
def read_candidate_profile(
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
) -> CandidateProfile:
    return get_candidate_profile(db, current_user.id)


@router.put(
    "/me",
    response_model=CandidateProfileResponse,
)
def update_candidate_profile(
    profile_data: CandidateProfileUpdate,
    current_user: User = Depends(require_candidate),
    db: Session = Depends(get_db),
) -> CandidateProfile:
    profile = get_candidate_profile(db, current_user.id)

    for field, value in profile_data.model_dump().items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile