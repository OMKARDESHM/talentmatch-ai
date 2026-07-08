import logging
import re
from time import perf_counter
from typing import Any
from uuid import uuid4

from starlette.datastructures import Headers
from starlette.types import (
    ASGIApp,
    Message,
    Receive,
    Scope,
    Send,
)


REQUEST_ID_HEADER = "X-Request-ID"
REQUEST_ID_HEADER_BYTES = b"x-request-id"
MAX_REQUEST_ID_LENGTH = 128

REQUEST_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9._:-]+$"
)

logger = logging.getLogger("talentmatch.request")
logger.setLevel(logging.INFO)

if not logger.handlers:
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(
        logging.Formatter("%(message)s")
    )
    logger.addHandler(stream_handler)

logger.propagate = False

def is_valid_request_id(value: str | None) -> bool:
    if value is None:
        return False

    if not value:
        return False

    if len(value) > MAX_REQUEST_ID_LENGTH:
        return False

    return REQUEST_ID_PATTERN.fullmatch(value) is not None


def resolve_request_id(value: str | None) -> str:
    if is_valid_request_id(value):
        return value

    return str(uuid4())


class RequestContextMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        request_id = resolve_request_id(
            headers.get(REQUEST_ID_HEADER)
        )

        scope.setdefault("state", {})
        scope["state"]["request_id"] = request_id

        method = scope.get("method", "UNKNOWN")
        path = scope.get("path", "")
        status_code = 500
        started_at = perf_counter()

        async def send_with_request_id(
            message: Message,
        ) -> None:
            nonlocal status_code

            if message["type"] == "http.response.start":
                status_code = message["status"]

                response_headers = list(
                    message.get("headers", [])
                )

                response_headers = [
                    (name, value)
                    for name, value in response_headers
                    if name.lower()
                    != REQUEST_ID_HEADER_BYTES
                ]

                response_headers.append(
                    (
                        REQUEST_ID_HEADER_BYTES,
                        request_id.encode("ascii"),
                    )
                )

                message["headers"] = response_headers

            await send(message)

        try:
            await self.app(
                scope,
                receive,
                send_with_request_id,
            )
        finally:
            duration_ms = (
                perf_counter() - started_at
            ) * 1000

            logger.info(
                (
                    "request_completed "
                    "request_id=%s "
                    "method=%s "
                    "path=%s "
                    "status_code=%s "
                    "duration_ms=%.2f"
                ),
                request_id,
                method,
                path,
                status_code,
                duration_ms,
            )
