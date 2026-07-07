import json

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import CandidateProfile, User


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
        name="Application Candidate",
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


def test_candidate_can_apply_to_open_job(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
    admin_token: str,
) -> None:
    profile = create_candidate_profile(db, candidate_user)
    job = create_job(client, admin_token)

    response = client.post(
        "/applications",
        headers=auth_headers(candidate_token),
        json={"job_id": job["id"]},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["candidate_id"] == profile.id
    assert data["job_id"] == job["id"]
    assert data["status"] == "applied"

    snapshot = json.loads(data["profile_snapshot"])

    assert snapshot["name"] == "Application Candidate"
    assert snapshot["skills"] == "Python, FastAPI, SQL"
    assert snapshot["preferred_location"] == "Pune"


def test_application_snapshot_is_not_changed_by_profile_update(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
    admin_token: str,
) -> None:
    create_candidate_profile(db, candidate_user)
    job = create_job(client, admin_token)

    apply_response = client.post(
        "/applications",
        headers=auth_headers(candidate_token),
        json={"job_id": job["id"]},
    )

    assert apply_response.status_code == 201

    application = apply_response.json()
    original_snapshot = json.loads(
        application["profile_snapshot"]
    )

    update_response = client.put(
        "/candidates/me",
        headers=auth_headers(candidate_token),
        json={
            "name": "Changed Candidate",
            "skills": "Java, Spring Boot",
            "education": "Updated Education",
            "project_summaries": "Updated project summary.",
            "preferred_location": "Mumbai",
            "preferred_role_type": "Backend",
            "domain_interest": "FinTech",
        },
    )

    assert update_response.status_code == 200

    applications_response = client.get(
        "/applications/me",
        headers=auth_headers(candidate_token),
    )

    assert applications_response.status_code == 200

    stored_snapshot = json.loads(
        applications_response.json()[0]["profile_snapshot"]
    )

    assert stored_snapshot == original_snapshot
    assert stored_snapshot["name"] == "Application Candidate"
    assert stored_snapshot["skills"] == "Python, FastAPI, SQL"


def test_candidate_cannot_apply_twice_to_same_job(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
    admin_token: str,
) -> None:
    create_candidate_profile(db, candidate_user)
    job = create_job(client, admin_token)

    first_response = client.post(
        "/applications",
        headers=auth_headers(candidate_token),
        json={"job_id": job["id"]},
    )

    second_response = client.post(
        "/applications",
        headers=auth_headers(candidate_token),
        json={"job_id": job["id"]},
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert (
        second_response.json()["detail"]
        == "You have already applied to this job"
    )


def test_candidate_cannot_apply_to_closed_job(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
    admin_token: str,
) -> None:
    create_candidate_profile(db, candidate_user)
    job = create_job(client, admin_token)

    close_response = client.patch(
        f"/jobs/{job['id']}/status",
        headers=auth_headers(admin_token),
        json={"status": "closed"},
    )

    assert close_response.status_code == 200

    response = client.post(
        "/applications",
        headers=auth_headers(candidate_token),
        json={"job_id": job["id"]},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Job is closed"


def test_candidate_cannot_apply_to_missing_job(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
) -> None:
    create_candidate_profile(db, candidate_user)

    response = client.post(
        "/applications",
        headers=auth_headers(candidate_token),
        json={"job_id": 9999},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Job not found"


def test_candidate_without_profile_cannot_apply(
    client: TestClient,
    candidate_token: str,
) -> None:
    response = client.post(
        "/applications",
        headers=auth_headers(candidate_token),
        json={"job_id": 1},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Candidate profile not found"


def test_candidate_can_view_own_applications(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
    admin_token: str,
) -> None:
    create_candidate_profile(db, candidate_user)
    job = create_job(client, admin_token)

    apply_response = client.post(
        "/applications",
        headers=auth_headers(candidate_token),
        json={"job_id": job["id"]},
    )

    assert apply_response.status_code == 201

    response = client.get(
        "/applications/me",
        headers=auth_headers(candidate_token),
    )

    assert response.status_code == 200

    applications = response.json()

    assert len(applications) == 1
    assert applications[0]["job_id"] == job["id"]
    assert applications[0]["status"] == "applied"


def test_admin_cannot_apply_to_job(
    client: TestClient,
    admin_token: str,
) -> None:
    response = client.post(
        "/applications",
        headers=auth_headers(admin_token),
        json={"job_id": 1},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Candidate access required"