from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth import hash_password
from app.models import User, UserRole


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


def create_job(
    client: TestClient,
    admin_token: str,
    **overrides: str,
) -> dict:
    payload = {
        **JOB_PAYLOAD,
        **overrides,
    }

    response = client.post(
        "/jobs",
        json=payload,
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 201

    return response.json()


def test_admin_can_create_job(
    client: TestClient,
    admin_token: str,
) -> None:
    response = client.post(
        "/jobs",
        json=JOB_PAYLOAD,
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["title"] == "Python Backend Engineer"
    assert data["status"] == "open"
    assert data["location"] == "Pune"


def test_candidate_cannot_create_job(
    client: TestClient,
    candidate_token: str,
) -> None:
    response = client.post(
        "/jobs",
        json=JOB_PAYLOAD,
        headers=auth_headers(candidate_token),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_job_filters_use_and_semantics(
    client: TestClient,
    admin_token: str,
    candidate_token: str,
) -> None:
    create_job(client, admin_token)

    create_job(
        client,
        admin_token,
        title="Healthcare Data Analyst",
        required_skills="Python, SQL, Tableau",
        role_type="Data Analyst",
    )

    create_job(
        client,
        admin_token,
        title="Java Backend Developer",
        required_skills="Java, Spring Boot",
        experience_level="Mid Level",
        location="Mumbai",
        domain="FinTech",
    )

    response = client.get(
        "/jobs",
        params={
            "skill": "python",
            "location": "pune",
            "experience_level": "Entry Level",
        },
        headers=auth_headers(candidate_token),
    )

    assert response.status_code == 200

    jobs = response.json()

    assert len(jobs) == 2
    assert {
        job["title"]
        for job in jobs
    } == {
        "Python Backend Engineer",
        "Healthcare Data Analyst",
    }


def test_closed_job_is_hidden_from_candidate(
    client: TestClient,
    admin_token: str,
    candidate_token: str,
) -> None:
    job = create_job(client, admin_token)

    close_response = client.patch(
        f"/jobs/{job['id']}/status",
        json={"status": "closed"},
        headers=auth_headers(admin_token),
    )

    assert close_response.status_code == 200
    assert close_response.json()["status"] == "closed"

    list_response = client.get(
        "/jobs",
        headers=auth_headers(candidate_token),
    )

    assert list_response.status_code == 200
    assert list_response.json() == []

    detail_response = client.get(
        f"/jobs/{job['id']}",
        headers=auth_headers(candidate_token),
    )

    assert detail_response.status_code == 404


def test_owner_admin_can_view_closed_job(
    client: TestClient,
    admin_token: str,
) -> None:
    job = create_job(client, admin_token)

    client.patch(
        f"/jobs/{job['id']}/status",
        json={"status": "closed"},
        headers=auth_headers(admin_token),
    )

    response = client.get(
        f"/jobs/{job['id']}",
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "closed"


def test_admin_can_update_job(
    client: TestClient,
    admin_token: str,
) -> None:
    job = create_job(client, admin_token)

    updated_payload = {
        **JOB_PAYLOAD,
        "title": "AI Platform Backend Engineer",
        "required_skills": "Python, FastAPI, SQL, Docker",
        "domain": "AI",
    }

    response = client.put(
        f"/jobs/{job['id']}",
        json=updated_payload,
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["title"] == "AI Platform Backend Engineer"
    assert data["domain"] == "AI"
    assert "Docker" in data["required_skills"]


def test_invalid_job_status_is_rejected(
    client: TestClient,
    admin_token: str,
) -> None:
    job = create_job(client, admin_token)

    response = client.patch(
        f"/jobs/{job['id']}/status",
        json={"status": "archived"},
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 422

def test_admin_cannot_manage_another_admins_job(
    client: TestClient,
    db: Session,
    admin_token: str,
) -> None:
    other_admin = User(
        email="other-admin@test.dev",
        password_hash=hash_password("OtherAdmin123!"),
        role=UserRole.ADMIN.value,
    )

    db.add(other_admin)
    db.commit()

    login_response = client.post(
        "/auth/login",
        json={
            "email": "other-admin@test.dev",
            "password": "OtherAdmin123!",
        },
    )

    assert login_response.status_code == 200

    other_admin_token = login_response.json()["access_token"]

    job = create_job(client, admin_token)

    response = client.patch(
        f"/jobs/{job['id']}/status",
        json={"status": "closed"},
        headers=auth_headers(other_admin_token),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You cannot manage this job"