"""Atomic Redis token buckets using Redis time; no client-controlled identity."""

import asyncio
import hashlib
from collections.abc import Awaitable, Callable

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials
from redis.asyncio import Redis
from starlette.concurrency import run_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from confidence.config import load_config
from confidence.infrastructure.auth import verify_token


class RedisRateLimiter:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def allow(self, key: str, rpm: int) -> bool:
        script = """
        local time = redis.call('TIME')
        local now = tonumber(time[1]) + tonumber(time[2]) / 1000000
        local old = redis.call('HMGET', KEYS[1], 'tokens', 'time')
        local capacity = tonumber(ARGV[1])
        local tokens = tonumber(old[1]) or capacity
        local previous = tonumber(old[2]) or now
        tokens = math.min(capacity, tokens + math.max(0,now-previous)*capacity/60)
        local allowed = 0
        if tokens >= 1 then tokens = tokens-1; allowed = 1 end
        redis.call('HSET', KEYS[1], 'tokens', tokens, 'time', now)
        redis.call('EXPIRE', KEYS[1], 120)
        return allowed
        """
        return bool(await self.redis.eval(script, 1, "rate:" + hashlib.sha256(key.encode()).hexdigest(), rpm))


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        config = load_config().rate_limit
        if not request.url.path.startswith("/v1/") or not config.rate_limit_enabled:
            return await call_next(request)
        try:
            limiter = RedisRateLimiter(request.app.state.redis)
            ip = request.client.host if request.client else "unknown"
            async with asyncio.timeout(0.05):
                allowed = await limiter.allow("global", config.global_rpm) and await limiter.allow("ip:" + ip, config.per_ip_rpm)
            if not allowed:
                return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429, headers={"Retry-After": "60"})
            header = request.headers.get("authorization", "")
            if header.lower().startswith("bearer "):
                user = await run_in_threadpool(verify_token, HTTPAuthorizationCredentials(scheme="Bearer", credentials=header[7:]))
                async with asyncio.timeout(0.05):
                    allowed = await limiter.allow("actor:" + user.actor_id, config.per_actor_rpm)
                if not allowed:
                    return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429, headers={"Retry-After": "60"})
        except HTTPException as exc:
            return JSONResponse({"detail": exc.detail}, status_code=exc.status_code, headers=exc.headers)
        except Exception:
            return JSONResponse({"detail": "Rate limiting unavailable"}, status_code=503)
        return await call_next(request)
