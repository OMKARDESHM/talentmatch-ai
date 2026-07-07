from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.auth import (
    AdminUser,
    CandidateUser,
    CurrentUser,
    DatabaseSession,
    create_access_token,
    hash_password,
    verify_password,
)
from app.models import User
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    request: RegisterRequest,
    db: DatabaseSession,
) -> User:
    existing_user = db.scalar(
        select(User).where(User.email == request.email)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    user = User(
        email=request.email,
        password_hash=hash_password(request.password),
        role=request.role.value,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login_user(
    request: LoginRequest,
    db: DatabaseSession,
) -> TokenResponse:
    user = db.scalar(
        select(User).where(User.email == request.email)
    )

    if user is None or not verify_password(
        request.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(user)

    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(current_user: CurrentUser) -> User:
    return current_user


@router.get("/admin-check")
def admin_check(admin: AdminUser) -> dict[str, str]:
    return {
        "message": f"Admin access granted for {admin.email}",
    }


@router.get("/candidate-check")
def candidate_check(candidate: CandidateUser) -> dict[str, str]:
    return {
        "message": f"Candidate access granted for {candidate.email}",
    }