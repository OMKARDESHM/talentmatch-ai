import logging
import re

from fastapi.testclient import TestClient

from app.main import app
from app.middleware import (
    REQUEST_ID_HEADER,
    is_valid_request_id,
    resolve_request_id,
)


UUID_PATTERN = re.compile(
    (
        r"^[0-9a-f]{8}-"
        r"[0-9a-f]{4}-"
        r"[0-9a-f]{4}-"
        r"[0-9a-f]{4}-"
        r"[0-9a-f]{12}$"
    )
)


def test_valid_request_id_is_accepted() -> None:
    assert is_valid_request_id(
        "talentmatch-request_123:api.v1"
    )


def test_invalid_request_id_characters_are_rejected() -> None:
    assert not is_valid_request_id(
        "request id with spaces"
    )


def test_overlong_request_id_is_rejected() -> None:
    assert not is_valid_request_id("a" * 129)


def test_missing_request_id_generates_uuid() -> None:
    request_id = resolve_request_id(None)

    assert UUID_PATTERN.fullmatch(request_id)


def test_health_response_contains_generated_request_id(
    client: TestClient,
) -> None:
    response = client.get("/health")

    request_id = response.headers[REQUEST_ID_HEADER]

    assert response.status_code == 200
    assert UUID_PATTERN.fullmatch(request_id)


def test_valid_incoming_request_id_is_preserved(
    client: TestClient,
) -> None:
    request_id = "talentmatch-test-request-123"

    response = client.get(
        "/health",
        headers={
            REQUEST_ID_HEADER: request_id,
        },
    )

    assert response.status_code == 200
    assert (
        response.headers[REQUEST_ID_HEADER]
        == request_id
    )


def test_invalid_incoming_request_id_is_replaced(
    client: TestClient,
) -> None:
    response = client.get(
        "/health",
        headers={
            REQUEST_ID_HEADER: (
                "invalid request id"
            ),
        },
    )

    request_id = response.headers[REQUEST_ID_HEADER]

    assert response.status_code == 200
    assert request_id != "invalid request id"
    assert UUID_PATTERN.fullmatch(request_id)


def test_not_found_response_contains_request_id(
    client: TestClient,
) -> None:
    response = client.get(
        "/route-that-does-not-exist"
    )

    assert response.status_code == 404
    assert UUID_PATTERN.fullmatch(
        response.headers[REQUEST_ID_HEADER]
    )


def test_request_completion_is_logged(
    client: TestClient,
    caplog,
) -> None:
    request_id = "logging-test-request"

    with caplog.at_level(
        logging.INFO,
        logger="talentmatch.request",
    ):
        response = client.get(
            "/health",
            headers={
                REQUEST_ID_HEADER: request_id,
            },
        )

    assert response.status_code == 200

    messages = [
        record.getMessage()
        for record in caplog.records
        if record.name == "talentmatch.request"
    ]

    assert any(
        "request_completed" in message
        and f"request_id={request_id}" in message
        and "method=GET" in message
        and "path=/health" in message
        and "status_code=200" in message
        and "duration_ms=" in message
        for message in messages
    )


def test_request_log_does_not_include_query_string(
    client: TestClient,
    caplog,
) -> None:
    secret_value = "sensitive-search-value"

    with caplog.at_level(
        logging.INFO,
        logger="talentmatch.request",
    ):
        response = client.get(
            f"/health?search={secret_value}"
        )

    assert response.status_code == 200

    request_logs = [
        record.getMessage()
        for record in caplog.records
        if record.name == "talentmatch.request"
    ]

    assert request_logs
    assert all(
        secret_value not in message
        for message in request_logs
    )


def test_request_log_does_not_include_authorization_token(
    client: TestClient,
    caplog,
) -> None:
    token = "secret-bearer-token-value"

    with caplog.at_level(
        logging.INFO,
        logger="talentmatch.request",
    ):
        response = client.get(
            "/health",
            headers={
                "Authorization": f"Bearer {token}",
            },
        )

    assert response.status_code == 200

    request_logs = [
        record.getMessage()
        for record in caplog.records
        if record.name == "talentmatch.request"
    ]

    assert request_logs
    assert all(
        token not in message
        for message in request_logs
    )


def test_request_logger_emits_info_logs() -> None:
    request_logger = logging.getLogger(
        "talentmatch.request"
    )

    assert request_logger.isEnabledFor(logging.INFO)
