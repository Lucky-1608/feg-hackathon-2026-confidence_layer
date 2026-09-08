"""Request identity propagated to async audit tasks and structured logs."""

import re
from contextvars import ContextVar
from uuid import uuid4

import structlog
from starlette.types import ASGIApp, Message, Receive, Scope, Send

request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


class CorrelationIdMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        incoming = dict(scope.get("headers", [])).get(b"x-request-id", b"").decode("ascii", errors="ignore")
        value = incoming if re.fullmatch(r"[A-Za-z0-9_-]{1,64}", incoming) else str(uuid4())
        token = request_id.set(value)
        log_tokens = structlog.contextvars.bind_contextvars(request_id=value)

        async def send_response(message: Message) -> None:
            if message["type"] == "http.response.start":
                message["headers"] = [*message.get("headers", []), (b"x-request-id", value.encode())]
            await send(message)

        try:
            await self.app(scope, receive, send_response)
        finally:
            request_id.reset(token)
            structlog.contextvars.reset_contextvars(**log_tokens)
