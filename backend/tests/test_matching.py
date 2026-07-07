from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.matching import parse_matching_intent
from app.models import (
    CandidateProfile,
    Job,
    JobStatus,
    User,
)


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
        name="Matching Candidate",
        skills="Python, FastAPI, SQL",
        education="B.E. Computer Engineering",
        project_summaries=(
            "Built Python backend APIs and data applications."
        ),
        preferred_location="Pune",
        preferred_role_type="Backend",
        domain_interest="Healthcare",
    )

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return profile


def create_matching_jobs(
    db: Session,
    admin_user: User,
) -> list[Job]:
    jobs = [
        Job(
            title="Python Backend Engineer",
            description=(
                "Build healthcare APIs using Python and FastAPI."
            ),
            required_skills="Python, FastAPI, PostgreSQL",
            experience_level="Entry Level",
            location="Pune",
            role_type="Backend",
            domain="Healthcare",
            status=JobStatus.OPEN.value,
            created_by_id=admin_user.id,
        ),
        Job(
            title="Java Backend Developer",
            description=(
                "Build financial services using Java."
            ),
            required_skills="Java, Spring Boot, MySQL",
            experience_level="Mid Level",
            location="Mumbai",
            role_type="Backend",
            domain="FinTech",
            status=JobStatus.OPEN.value,
            created_by_id=admin_user.id,
        ),
        Job(
            title="Healthcare Data Analyst",
            description=(
                "Analyse healthcare datasets and reports."
            ),
            required_skills="Python, SQL, Tableau",
            experience_level="Entry Level",
            location="Pune",
            role_type="Data Analyst",
            domain="Healthcare",
            status=JobStatus.OPEN.value,
            created_by_id=admin_user.id,
        ),
        Job(
            title="Closed Python Backend Role",
            description=(
                "A closed healthcare backend opportunity."
            ),
            required_skills="Python, FastAPI",
            experience_level="Entry Level",
            location="Pune",
            role_type="Backend",
            domain="Healthcare",
            status=JobStatus.CLOSED.value,
            created_by_id=admin_user.id,
        ),
    ]

    db.add_all(jobs)
    db.commit()

    for job in jobs:
        db.refresh(job)

    return jobs


def test_intent_parser_extracts_known_preferences() -> None:
    intent = parse_matching_intent(
        "I want a Python backend role in healthcare in Pune"
    )

    assert intent.skills == ["python"]
    assert intent.role_types == ["backend"]
    assert intent.domains == ["healthcare"]
    assert intent.locations == ["pune"]


def test_intent_parser_understands_aliases() -> None:
    intent = parse_matching_intent(
        "Fresh graduate looking for a back-end health tech "
        "role in Bangalore"
    )

    assert intent.role_types == ["backend"]
    assert intent.domains == ["healthcare"]
    assert intent.locations == ["bengaluru"]
    assert intent.experience_levels == ["entry level"]


def test_candidate_receives_ranked_job_matches(
    client: TestClient,
    db: Session,
    candidate_user: User,
    admin_user: User,
    candidate_token: str,
) -> None:
    create_candidate_profile(db, candidate_user)
    create_matching_jobs(db, admin_user)

    response = client.post(
        "/matching/jobs",
        headers=auth_headers(candidate_token),
        json={
            "query": (
                "I want a Python backend role in healthcare "
                "in Pune"
            )
        },
    )

    assert response.status_code == 200

    matches = response.json()["matches"]

    assert len(matches) == 3
    assert matches[0]["job"]["title"] == (
        "Python Backend Engineer"
    )
    assert matches[0]["match_score"] == 95


def test_match_results_are_sorted_by_score(
    client: TestClient,
    db: Session,
    candidate_user: User,
    admin_user: User,
    candidate_token: str,
) -> None:
    create_candidate_profile(db, candidate_user)
    create_matching_jobs(db, admin_user)

    response = client.post(
        "/matching/jobs",
        headers=auth_headers(candidate_token),
        json={
            "query": (
                "Python backend healthcare role in Pune"
            )
        },
    )

    assert response.status_code == 200

    scores = [
        match["match_score"]
        for match in response.json()["matches"]
    ]

    assert scores == sorted(scores, reverse=True)


def test_closed_jobs_are_excluded_from_matching(
    client: TestClient,
    db: Session,
    candidate_user: User,
    admin_user: User,
    candidate_token: str,
) -> None:
    create_candidate_profile(db, candidate_user)
    create_matching_jobs(db, admin_user)

    response = client.post(
        "/matching/jobs",
        headers=auth_headers(candidate_token),
        json={
            "query": "Python backend healthcare role"
        },
    )

    assert response.status_code == 200

    titles = [
        match["job"]["title"]
        for match in response.json()["matches"]
    ]

    assert "Closed Python Backend Role" not in titles


def test_match_result_explains_relevance(
    client: TestClient,
    db: Session,
    candidate_user: User,
    admin_user: User,
    candidate_token: str,
) -> None:
    create_candidate_profile(db, candidate_user)
    create_matching_jobs(db, admin_user)

    response = client.post(
        "/matching/jobs",
        headers=auth_headers(candidate_token),
        json={
            "query": "Python backend healthcare role in Pune"
        },
    )

    assert response.status_code == 200

    best_match = response.json()["matches"][0]

    assert "Skill: Python" in best_match["matched_factors"]
    assert "Role type: Backend" in best_match["matched_factors"]
    assert "Domain: Healthcare" in best_match["matched_factors"]
    assert "Location: Pune" in best_match["matched_factors"]
    assert best_match["explanation"]


def test_profile_skills_are_used_when_query_omits_skills(
    client: TestClient,
    db: Session,
    candidate_user: User,
    admin_user: User,
    candidate_token: str,
) -> None:
    create_candidate_profile(db, candidate_user)
    create_matching_jobs(db, admin_user)

    response = client.post(
        "/matching/jobs",
        headers=auth_headers(candidate_token),
        json={
            "query": "I want a backend healthcare role in Pune"
        },
    )

    assert response.status_code == 200

    best_match = response.json()["matches"][0]

    assert best_match["job"]["title"] == (
        "Python Backend Engineer"
    )
    assert "Skill: Python" in best_match["matched_factors"]
    assert "Skill: Fastapi" in best_match["matched_factors"]


def test_explicit_query_skill_overrides_profile_skill_context(
    client: TestClient,
    db: Session,
    candidate_user: User,
    admin_user: User,
    candidate_token: str,
) -> None:
    create_candidate_profile(db, candidate_user)
    create_matching_jobs(db, admin_user)

    response = client.post(
        "/matching/jobs",
        headers=auth_headers(candidate_token),
        json={
            "query": "I want a Java backend role"
        },
    )

    assert response.status_code == 200

    best_match = response.json()["matches"][0]

    assert best_match["job"]["title"] == (
        "Java Backend Developer"
    )
    assert "Skill: Java" in best_match["matched_factors"]


def test_admin_cannot_use_candidate_matching(
    client: TestClient,
    admin_token: str,
) -> None:
    response = client.post(
        "/matching/jobs",
        headers=auth_headers(admin_token),
        json={
            "query": "Python backend role"
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == (
        "Candidate access required"
    )


def test_missing_candidate_profile_returns_not_found(
    client: TestClient,
    candidate_token: str,
) -> None:
    response = client.post(
        "/matching/jobs",
        headers=auth_headers(candidate_token),
        json={
            "query": "Python backend role"
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Candidate profile not found"
    )


def test_short_query_is_rejected(
    client: TestClient,
    candidate_token: str,
) -> None:
    response = client.post(
        "/matching/jobs",
        headers=auth_headers(candidate_token),
        json={
            "query": "AI"
        },
    )

    assert response.status_code == 422


def test_matching_with_no_open_jobs_returns_empty_results(
    client: TestClient,
    db: Session,
    candidate_user: User,
    candidate_token: str,
) -> None:
    create_candidate_profile(db, candidate_user)

    response = client.post(
        "/matching/jobs",
        headers=auth_headers(candidate_token),
        json={
            "query": "Python backend healthcare role"
        },
    )

    assert response.status_code == 200
    assert response.json()["matches"] == []