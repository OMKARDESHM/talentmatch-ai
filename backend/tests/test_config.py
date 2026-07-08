import pytest

from app.config import (
    get_cors_origins,
    get_positive_integer_environment_variable,
    get_required_environment_variable,
)


def test_required_environment_variable_is_returned(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "TEST_REQUIRED_SETTING",
        " configured-value ",
    )

    value = get_required_environment_variable(
        "TEST_REQUIRED_SETTING"
    )

    assert value == "configured-value"


def test_missing_required_environment_variable_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        "TEST_REQUIRED_SETTING",
        raising=False,
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "TEST_REQUIRED_SETTING is not configured"
        ),
    ):
        get_required_environment_variable(
            "TEST_REQUIRED_SETTING"
        )


def test_blank_required_environment_variable_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "TEST_REQUIRED_SETTING",
        "   ",
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "TEST_REQUIRED_SETTING is not configured"
        ),
    ):
        get_required_environment_variable(
            "TEST_REQUIRED_SETTING"
        )


def test_positive_integer_environment_variable_uses_default(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv(
        "TEST_POSITIVE_INTEGER",
        raising=False,
    )

    value = get_positive_integer_environment_variable(
        "TEST_POSITIVE_INTEGER",
        60,
    )

    assert value == 60


def test_positive_integer_environment_variable_is_parsed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "TEST_POSITIVE_INTEGER",
        "120",
    )

    value = get_positive_integer_environment_variable(
        "TEST_POSITIVE_INTEGER",
        60,
    )

    assert value == 120


@pytest.mark.parametrize(
    "value",
    [
        "0",
        "-1",
        "invalid",
        "60.5",
    ],
)
def test_invalid_positive_integer_environment_variable_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
    value: str,
) -> None:
    monkeypatch.setenv(
        "TEST_POSITIVE_INTEGER",
        value,
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "TEST_POSITIVE_INTEGER "
            "must be a positive integer"
        ),
    ):
        get_positive_integer_environment_variable(
            "TEST_POSITIVE_INTEGER",
            60,
        )


def test_cors_origins_are_parsed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "CORS_ORIGINS",
        (
            "https://app.example.com, "
            "https://admin.example.com"
        ),
    )

    origins = get_cors_origins()

    assert origins == (
        "https://app.example.com",
        "https://admin.example.com",
    )


def test_empty_cors_origins_are_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "CORS_ORIGINS",
        " , ",
    )

    with pytest.raises(
        RuntimeError,
        match=(
            "CORS_ORIGINS must contain at least one origin"
        ),
    ):
        get_cors_origins()
