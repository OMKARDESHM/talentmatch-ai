from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import CandidateProfile, User


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
        name="Test Candidate",
        skills="Python, FastAPI, SQL",
        education="B.E. Computer Engineering",
        project_summaries=(
            "Built backend APIs and AI-assisted data applications."
        ),
        preferred_location="Pune",
        preferred_role_type="Backend",
        domain_interest="Healthcare",
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


def test_candidate_can_view_profile(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
) -> None:
    create_candidate_profile(db, candidate_user)

    response = client.get(
        "/candidates/me",
        headers=auth_headers(candidate_token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Test Candidate"
    assert data["skills"] == "Python, FastAPI, SQL"
    assert data["preferred_location"] == "Pune"
    assert data["domain_interest"] == "Healthcare"


def test_candidate_can_update_profile(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
) -> None:
    create_candidate_profile(db, candidate_user)

    response = client.put(
        "/candidates/me",
        headers=auth_headers(candidate_token),
        json={
            "name": "Updated Candidate",
            "skills": "Python, FastAPI, SQL, Docker",
            "education": "B.E. Computer Engineering",
            "project_summaries": (
                "Built observable backend APIs and AI applications."
            ),
            "preferred_location": "Remote",
            "preferred_role_type": "Backend",
            "domain_interest": "AI",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated Candidate"
    assert data["preferred_location"] == "Remote"
    assert data["domain_interest"] == "AI"
    assert "Docker" in data["skills"]


def test_candidate_without_profile_gets_not_found(
    client: TestClient,
    candidate_token: str,
) -> None:
    response = client.get(
        "/candidates/me",
        headers=auth_headers(candidate_token),
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Candidate profile not found"


def test_admin_cannot_access_candidate_profile_endpoint(
    client: TestClient,
    admin_token: str,
) -> None:
    response = client.get(
        "/candidates/me",
        headers=auth_headers(admin_token),
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Candidate access required"