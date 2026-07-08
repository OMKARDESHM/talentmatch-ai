from datetime import datetime, timezone
from typing import Annotated

from pydantic import PlainSerializer


def serialize_utc_datetime(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    else:
        value = value.astimezone(timezone.utc)

    return value.isoformat().replace("+00:00", "Z")


UtcDateTime = Annotated[
    datetime,
    PlainSerializer(
        serialize_utc_datetime,
        return_type=str,
        when_used="json",
    ),
]