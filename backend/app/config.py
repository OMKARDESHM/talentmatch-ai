import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def get_required_environment_variable(name: str) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise RuntimeError(
            f"{name} is not configured"
        )

    return value.strip()


def get_positive_integer_environment_variable(
    name: str,
    default: int,
) -> int:
    raw_value = os.getenv(name)

    if raw_value is None:
        return default

    try:
        value = int(raw_value)
    except ValueError as error:
        raise RuntimeError(
            f"{name} must be a positive integer"
        ) from error

    if value <= 0:
        raise RuntimeError(
            f"{name} must be a positive integer"
        )

    return value


def get_cors_origins() -> tuple[str, ...]:
    raw_value = os.getenv(
        "CORS_ORIGINS",
        (
            "http://localhost:5173,"
            "http://127.0.0.1:5173"
        ),
    )

    origins = tuple(
        origin.strip()
        for origin in raw_value.split(",")
        if origin.strip()
    )

    if not origins:
        raise RuntimeError(
            "CORS_ORIGINS must contain at least one origin"
        )

    return origins


@dataclass(frozen=True)
class Settings:
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    cors_origins: tuple[str, ...]


def load_settings() -> Settings:
    return Settings(
        database_url=os.getenv(
            "DATABASE_URL",
            "sqlite:///./talentmatch.db",
        ),
        jwt_secret_key=(
            get_required_environment_variable(
                "JWT_SECRET_KEY"
            )
        ),
        jwt_algorithm=os.getenv(
            "JWT_ALGORITHM",
            "HS256",
        ),
        access_token_expire_minutes=(
            get_positive_integer_environment_variable(
                "ACCESS_TOKEN_EXPIRE_MINUTES",
                60,
            )
        ),
        cors_origins=get_cors_origins(),
    )


settings = load_settings()
