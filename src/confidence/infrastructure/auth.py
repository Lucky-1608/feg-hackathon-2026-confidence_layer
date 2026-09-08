"""JWT identity validation and access binding. Demo credentials are local only."""

import hashlib
from functools import lru_cache
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient
from pydantic import BaseModel, Field

from confidence.config import load_config

security = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    subject: str = Field(min_length=1)
    operator_id: str = Field(min_length=1)
    scopes: list[str] = Field(default_factory=list)
    is_demo: bool = False

    @property
    def actor_id(self) -> str:
        return hashlib.sha256(f"{self.operator_id}\0{self.subject}".encode()).hexdigest()

    def require_scope(self, scope: str) -> None:
        if scope not in self.scopes:
            raise HTTPException(status_code=403, detail="Insufficient scope")


class JWTAuthProvider:
    def __init__(self, jwks_url: str, issuer: str, audience: str) -> None:
        if not jwks_url.startswith("https://"):
            raise ValueError("JWKS requires HTTPS")
        self.client = PyJWKClient(jwks_url, timeout=2, lifespan=300)
        self.issuer = issuer
        self.audience = audience

    def authenticate(self, token: str) -> AuthenticatedUser:
        try:
            key = self.client.get_signing_key_from_jwt(token)
            claims = jwt.decode(
                token,
                key.key,
                algorithms=["RS256"],
                issuer=self.issuer,
                audience=self.audience,
                options={"require": ["exp", "iss", "aud", "sub", "operator_id"]},
            )
            scope = claims.get("scope", "")
            if not isinstance(scope, str):
                raise ValueError("Invalid scope")
            return AuthenticatedUser(subject=claims["sub"], operator_id=claims["operator_id"], scopes=scope.split())
        except Exception as exc:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"}
            ) from exc


@lru_cache(maxsize=8)
def jwt_provider(url: str, issuer: str, audience: str) -> JWTAuthProvider:
    return JWTAuthProvider(url, issuer, audience)


def verify_token(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)]) -> AuthenticatedUser:
    config = load_config()
    if config.auth.auth_provider == "jwt":
        auth = config.auth
        if not auth.jwks_url or not auth.jwt_issuer or not auth.jwt_audience:
            raise HTTPException(status_code=503, detail="Authentication provider is not configured")
        if credentials is None:
            raise HTTPException(status_code=401, detail="Bearer token required")
        return jwt_provider(auth.jwks_url, auth.jwt_issuer, auth.jwt_audience).authenticate(credentials.credentials)
    try:
        config.require_demo_runtime()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="Authentication provider is not configured") from exc
    if credentials is None or credentials.credentials != "demo-token":
        raise HTTPException(status_code=401, detail="Invalid authentication credentials", headers={"WWW-Authenticate": "Bearer"})
    return AuthenticatedUser(
        subject="user-123", operator_id="demo", scopes=["decisions:write", "events:write", "outcomes:write", "metrics:read"], is_demo=True
    )


async def bind_session(request: Request, user: AuthenticatedUser, actor: str, session_id: UUID, scope: str) -> str:
    user.require_scope(scope)
    if user.is_demo:
        return actor
    if actor != user.subject:
        raise HTTPException(status_code=403, detail="Actor mismatch")
    script = """
    local owner = redis.call('GET', KEYS[1])
    if owner and owner ~= ARGV[1] then return 0 end
    redis.call('SET', KEYS[1], ARGV[1])
    return 1
    """
    try:
        import asyncio

        async with asyncio.timeout(0.05):
            valid = await request.app.state.redis.eval(script, 1, f"owner:{session_id}", user.actor_id)
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Session authorization unavailable") from exc
    if not valid:
        raise HTTPException(status_code=403, detail="Session mismatch")
    return user.actor_id
