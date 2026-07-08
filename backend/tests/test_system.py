from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session


def test_health_check(
    client: TestClient,
) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
    }


def test_readiness_check(
    client: TestClient,
) -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ready",
        "database": "reachable",
    }


def test_test_database_is_reachable(
    db: Session,
) -> None:
    result = db.execute(
        text("SELECT 1")
    ).scalar_one()

    assert result == 1
