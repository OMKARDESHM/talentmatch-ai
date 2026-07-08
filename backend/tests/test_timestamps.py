from datetime import datetime, timedelta, timezone

from app.schemas.application import ApplicationResponse
from app.schemas.common import serialize_utc_datetime
from app.schemas.job import JobResponse


def test_naive_datetime_serializes_as_utc() -> None:
    value = datetime(
        2026,
        7,
        8,
        5,
        51,
        35,
        283765,
    )

    result = serialize_utc_datetime(value)

    assert result == "2026-07-08T05:51:35.283765Z"


def test_utc_datetime_serializes_with_z_suffix() -> None:
    value = datetime(
        2026,
        7,
        8,
        5,
        51,
        35,
        tzinfo=timezone.utc,
    )

    result = serialize_utc_datetime(value)

    assert result == "2026-07-08T05:51:35Z"


def test_offset_datetime_is_converted_to_utc() -> None:
    india_timezone = timezone(
        timedelta(hours=5, minutes=30)
    )

    value = datetime(
        2026,
        7,
        8,
        11,
        21,
        35,
        tzinfo=india_timezone,
    )

    result = serialize_utc_datetime(value)

    assert result == "2026-07-08T05:51:35Z"


def test_application_response_serializes_timestamps_as_utc() -> None:
    response = ApplicationResponse(
        id=1,
        candidate_id=1,
        job_id=1,
        status="applied",
        profile_snapshot="{}",
        applied_at=datetime(
            2026,
            7,
            8,
            5,
            51,
            35,
        ),
        updated_at=datetime(
            2026,
            7,
            8,
            6,
            10,
            20,
        ),
    )

    data = response.model_dump(mode="json")

    assert data["applied_at"] == "2026-07-08T05:51:35Z"
    assert data["updated_at"] == "2026-07-08T06:10:20Z"


def test_job_response_serializes_timestamps_as_utc() -> None:
    response = JobResponse(
        id=1,
        title="Python Backend Engineer",
        description="Build backend APIs using Python.",
        required_skills="Python, FastAPI",
        experience_level="Entry Level",
        location="Pune",
        role_type="Backend",
        domain="Healthcare",
        status="open",
        created_by_id=1,
        created_at=datetime(
            2026,
            7,
            8,
            5,
            30,
        ),
        updated_at=datetime(
            2026,
            7,
            8,
            5,
            45,
        ),
    )

    data = response.model_dump(mode="json")

    assert data["created_at"] == "2026-07-08T05:30:00Z"
    assert data["updated_at"] == "2026-07-08T05:45:00Z"