"""Authenticate the Prometheus mount; probes remain public."""

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from starlette.concurrency import run_in_threadpool
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from confidence.infrastructure.auth import verify_token


class AuthenticatedMetrics:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        raw = dict(scope.get("headers", [])).get(b"authorization", b"").decode("latin1")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=raw[7:]) if raw.lower().startswith("bearer ") else None
        try:
            user = await run_in_threadpool(verify_token, credentials)
            user.require_scope("metrics:read")
        except HTTPException as exc:
            await JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers)(scope, receive, send)
            return
        await self.app(scope, receive, send)
