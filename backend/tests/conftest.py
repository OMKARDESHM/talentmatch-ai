from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import hash_password
from app.database import Base, get_db
from app.main import app
from app.models import User, UserRole


TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    expire_on_commit=False,
)


@pytest.fixture
def db() -> Generator[Session, None, None]:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    with TestSessionLocal() as session:
        yield session

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db: Session) -> User:
    user = User(
        email="admin@test.dev",
        password_hash=hash_password("AdminTest123!"),
        role=UserRole.ADMIN.value,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def candidate_user(db: Session) -> User:
    user = User(
        email="candidate@test.dev",
        password_hash=hash_password("CandidateTest123!"),
        role=UserRole.CANDIDATE.value,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def admin_token(
    client: TestClient,
    admin_user: User,
) -> str:
    response = client.post(
        "/auth/login",
        json={
            "email": admin_user.email,
            "password": "AdminTest123!",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.fixture
def candidate_token(
    client: TestClient,
    candidate_user: User,
) -> str:
    response = client.post(
        "/auth/login",
        json={
            "email": candidate_user.email,
            "password": "CandidateTest123!",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]