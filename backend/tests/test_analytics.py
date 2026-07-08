from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import (
    Application,
    ApplicationStatus,
    CandidateProfile,
    Job,
    JobStatus,
    User,
)


def authorization_header(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
    }


def create_candidate_profile(
    db: Session,
    candidate_user: User,
    *,
    complete: bool = True,
) -> CandidateProfile:
    profile = CandidateProfile(
        user_id=candidate_user.id,
        name="Analytics Candidate",
        skills="Python, FastAPI" if complete else "",
        education="B.E. Computer Engineering",
        project_summaries=(
            "Built backend API and analytics projects."
            if complete
            else ""
        ),
        preferred_location="Pune",
        preferred_role_type="Backend",
        domain_interest="Healthcare",
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


def create_job(
    db: Session,
    admin_user: User,
    *,
    title: str,
    status: str = JobStatus.OPEN.value,
) -> Job:
    job = Job(
        title=title,
        description=(
            "Build and maintain backend APIs using Python."
        ),
        required_skills="Python, FastAPI",
        experience_level="Entry Level",
        location="Pune",
        role_type="Backend",
        domain="Healthcare",
        status=status,
        created_by_id=admin_user.id,
    )

    db.add(job)
    db.commit()
    db.refresh(job)

    return job


def create_application(
    db: Session,
    profile: CandidateProfile,
    job: Job,
    *,
    status: str,
) -> Application:
    application = Application(
        candidate_id=profile.id,
        job_id=job.id,
        status=status,
        profile_snapshot="{}",
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return application


def test_candidate_dashboard_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        "/analytics/candidate/dashboard"
    )

    assert response.status_code == 401


def test_admin_dashboard_requires_authentication(
    client: TestClient,
) -> None:
    response = client.get(
        "/analytics/admin/dashboard"
    )

    assert response.status_code == 401


def test_admin_cannot_access_candidate_dashboard(
    client: TestClient,
    admin_token: str,
) -> None:
    response = client.get(
        "/analytics/candidate/dashboard",
        headers=authorization_header(admin_token),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Candidate access required"
    )


def test_candidate_cannot_access_admin_dashboard(
    client: TestClient,
    candidate_token: str,
) -> None:
    response = client.get(
        "/analytics/admin/dashboard",
        headers=authorization_header(candidate_token),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Admin access required"
    )


def test_candidate_dashboard_without_profile(
    client: TestClient,
    db: Session,
    admin_user: User,
    candidate_token: str,
) -> None:
    create_job(
        db,
        admin_user,
        title="Open Backend Engineer",
    )
    create_job(
        db,
        admin_user,
        title="Closed Backend Engineer",
        status=JobStatus.CLOSED.value,
    )

    response = client.get(
        "/analytics/candidate/dashboard",
        headers=authorization_header(candidate_token),
    )

    assert response.status_code == 200

    assert response.json() == {
        "applications": {
            "total": 0,
            "applied": 0,
            "shortlisted": 0,
            "rejected": 0,
        },
        "open_jobs": 1,
        "profile_completeness": 0,
    }


def test_candidate_dashboard_returns_application_counts(
    client: TestClient,
    db: Session,
    admin_user: User,
    candidate_user: User,
    candidate_token: str,
) -> None:
    profile = create_candidate_profile(
        db,
        candidate_user,
    )

    applied_job = create_job(
        db,
        admin_user,
        title="Applied Job",
    )
    shortlisted_job = create_job(
        db,
        admin_user,
        title="Shortlisted Job",
    )
    rejected_job = create_job(
        db,
        admin_user,
        title="Rejected Job",
    )

    create_application(
        db,
        profile,
        applied_job,
        status=ApplicationStatus.APPLIED.value,
    )
    create_application(
        db,
        profile,
        shortlisted_job,
        status=ApplicationStatus.SHORTLISTED.value,
    )
    create_application(
        db,
        profile,
        rejected_job,
        status=ApplicationStatus.REJECTED.value,
    )

    response = client.get(
        "/analytics/candidate/dashboard",
        headers=authorization_header(candidate_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["applications"] == {
        "total": 3,
        "applied": 1,
        "shortlisted": 1,
        "rejected": 1,
    }
    assert data["open_jobs"] == 3
    assert data["profile_completeness"] == 100


def test_candidate_dashboard_calculates_profile_completeness(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
) -> None:
    create_candidate_profile(
        db,
        candidate_user,
        complete=False,
    )

    response = client.get(
        "/analytics/candidate/dashboard",
        headers=authorization_header(candidate_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["profile_completeness"] == 71


def test_admin_dashboard_returns_job_counts(
    client: TestClient,
    db: Session,
    admin_user: User,
    admin_token: str,
) -> None:
    create_job(
        db,
        admin_user,
        title="Open Job One",
    )
    create_job(
        db,
        admin_user,
        title="Open Job Two",
    )
    create_job(
        db,
        admin_user,
        title="Closed Job",
        status=JobStatus.CLOSED.value,
    )

    response = client.get(
        "/analytics/admin/dashboard",
        headers=authorization_header(admin_token),
    )

    assert response.status_code == 200

    assert response.json()["jobs"] == {
        "total": 3,
        "open": 2,
        "closed": 1,
    }


def test_admin_dashboard_returns_application_counts(
    client: TestClient,
    db: Session,
    admin_user: User,
    candidate_user: User,
    admin_token: str,
) -> None:
    profile = create_candidate_profile(
        db,
        candidate_user,
    )

    applied_job = create_job(
        db,
        admin_user,
        title="Applied Analytics Job",
    )
    shortlisted_job = create_job(
        db,
        admin_user,
        title="Shortlisted Analytics Job",
    )
    rejected_job = create_job(
        db,
        admin_user,
        title="Rejected Analytics Job",
    )

    create_application(
        db,
        profile,
        applied_job,
        status=ApplicationStatus.APPLIED.value,
    )
    create_application(
        db,
        profile,
        shortlisted_job,
        status=ApplicationStatus.SHORTLISTED.value,
    )
    create_application(
        db,
        profile,
        rejected_job,
        status=ApplicationStatus.REJECTED.value,
    )

    response = client.get(
        "/analytics/admin/dashboard",
        headers=authorization_header(admin_token),
    )

    assert response.status_code == 200

    assert response.json()["applications"] == {
        "total": 3,
        "applied": 1,
        "shortlisted": 1,
        "rejected": 1,
    }


def test_admin_dashboard_returns_zero_counts(
    client: TestClient,
    admin_token: str,
) -> None:
    response = client.get(
        "/analytics/admin/dashboard",
        headers=authorization_header(admin_token),
    )

    assert response.status_code == 200

    assert response.json() == {
        "jobs": {
            "total": 0,
            "open": 0,
            "closed": 0,
        },
        "applications": {
            "total": 0,
            "applied": 0,
            "shortlisted": 0,
            "rejected": 0,
        },
    }
