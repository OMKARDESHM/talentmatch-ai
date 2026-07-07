from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import create_access_token, hash_password
from app.models import (
    CandidateProfile,
    User,
    UserRole,
)


JOB_PAYLOAD = {
    "title": "Python Backend Engineer",
    "description": "Build healthcare backend APIs using Python.",
    "required_skills": "Python, FastAPI, PostgreSQL",
    "experience_level": "Entry Level",
    "location": "Pune",
    "role_type": "Backend",
    "domain": "Healthcare",
}


def auth_headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
    }


def create_candidate_profile(
    db: Session,
    candidate_user: User,
) -> CandidateProfile:
    profile = CandidateProfile(
        user_id=candidate_user.id,
        name="Pipeline Candidate",
        skills="Python, FastAPI, SQL",
        education="B.E. Computer Engineering",
        project_summaries="Built Python backend API projects.",
        preferred_location="Pune",
        preferred_role_type="Backend",
        domain_interest="Healthcare",
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


def create_job(
    client: TestClient,
    admin_token: str,
) -> dict:
    response = client.post(
        "/jobs",
        headers=auth_headers(admin_token),
        json=JOB_PAYLOAD,
    )

    assert response.status_code == 201

    return response.json()


def create_application(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
    admin_token: str,
) -> tuple[CandidateProfile, dict, dict]:
    profile = create_candidate_profile(db, candidate_user)
    job = create_job(client, admin_token)

    response = client.post(
        "/applications",
        headers=auth_headers(candidate_token),
        json={"job_id": job["id"]},
    )

    assert response.status_code == 201

    return profile, job, response.json()


def create_second_admin(
    db: Session,
) -> tuple[User, str]:
    admin = User(
        email="second-admin@talentmatch.dev",
        password_hash=hash_password("SecondAdminPass123!"),
        role=UserRole.ADMIN.value,
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    token = create_access_token(admin)

    return admin, token


def test_admin_can_view_applications_for_owned_job(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
    admin_token: str,
) -> None:
    profile, job, application = create_application(
        client,
        db,
        candidate_user,
        candidate_token,
        admin_token,
    )

    response = client.get(
        f"/admin/applications/jobs/{job['id']}",
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 200

    applications = response.json()

    assert len(applications) == 1
    assert applications[0]["id"] == application["id"]
    assert applications[0]["candidate_id"] == profile.id
    assert applications[0]["job_id"] == job["id"]
    assert applications[0]["status"] == "applied"


def test_admin_review_receives_parsed_profile_snapshot(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
    admin_token: str,
) -> None:
    _, job, _ = create_application(
        client,
        db,
        candidate_user,
        candidate_token,
        admin_token,
    )

    response = client.get(
        f"/admin/applications/jobs/{job['id']}",
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 200

    snapshot = response.json()[0]["profile_snapshot"]

    assert isinstance(snapshot, dict)
    assert snapshot["name"] == "Pipeline Candidate"
    assert snapshot["skills"] == "Python, FastAPI, SQL"
    assert snapshot["preferred_role_type"] == "Backend"


def test_admin_can_shortlist_application(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
    admin_token: str,
) -> None:
    _, _, application = create_application(
        client,
        db,
        candidate_user,
        candidate_token,
        admin_token,
    )

    response = client.patch(
        f"/admin/applications/{application['id']}/status",
        headers=auth_headers(admin_token),
        json={"status": "shortlisted"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "shortlisted"


def test_admin_can_reject_application(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
    admin_token: str,
) -> None:
    _, _, application = create_application(
        client,
        db,
        candidate_user,
        candidate_token,
        admin_token,
    )

    response = client.patch(
        f"/admin/applications/{application['id']}/status",
        headers=auth_headers(admin_token),
        json={"status": "rejected"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"


def test_candidate_cannot_view_admin_application_pipeline(
    client: TestClient,
    candidate_token: str,
) -> None:
    response = client.get(
        "/admin/applications/jobs/1",
        headers=auth_headers(candidate_token),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_candidate_cannot_update_application_status(
    client: TestClient,
    candidate_token: str,
) -> None:
    response = client.patch(
        "/admin/applications/1/status",
        headers=auth_headers(candidate_token),
        json={"status": "shortlisted"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_invalid_application_status_is_rejected(
    client: TestClient,
    admin_token: str,
) -> None:
    response = client.patch(
        "/admin/applications/1/status",
        headers=auth_headers(admin_token),
        json={"status": "interviewing"},
    )

    assert response.status_code == 422


def test_missing_application_returns_not_found(
    client: TestClient,
    admin_token: str,
) -> None:
    response = client.patch(
        "/admin/applications/9999/status",
        headers=auth_headers(admin_token),
        json={"status": "shortlisted"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"


def test_missing_job_returns_not_found(
    client: TestClient,
    admin_token: str,
) -> None:
    response = client.get(
        "/admin/applications/jobs/9999",
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_other_admin_cannot_view_job_applications(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
    admin_token: str,
) -> None:
    _, job, _ = create_application(
        client,
        db,
        candidate_user,
        candidate_token,
        admin_token,
    )
    _, second_admin_token = create_second_admin(db)

    response = client.get(
        f"/admin/applications/jobs/{job['id']}",
        headers=auth_headers(second_admin_token),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You cannot manage this job"


def test_other_admin_cannot_update_application_status(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
    admin_token: str,
) -> None:
    _, _, application = create_application(
        client,
        db,
        candidate_user,
        candidate_token,
        admin_token,
    )
    _, second_admin_token = create_second_admin(db)

    response = client.patch(
        f"/admin/applications/{application['id']}/status",
        headers=auth_headers(second_admin_token),
        json={"status": "shortlisted"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You cannot manage this job"


def test_status_update_is_visible_in_admin_pipeline(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
    admin_token: str,
) -> None:
    _, job, application = create_application(
        client,
        db,
        candidate_user,
        candidate_token,
        admin_token,
    )

    update_response = client.patch(
        f"/admin/applications/{application['id']}/status",
        headers=auth_headers(admin_token),
        json={"status": "shortlisted"},
    )

    assert update_response.status_code == 200

    pipeline_response = client.get(
        f"/admin/applications/jobs/{job['id']}",
        headers=auth_headers(admin_token),
    )

    assert pipeline_response.status_code == 200
    assert pipeline_response.json()[0]["status"] == "shortlisted"