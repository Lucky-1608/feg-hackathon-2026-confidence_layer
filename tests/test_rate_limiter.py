import fakeredis.aioredis
from httpx import ASGITransport, AsyncClient

from confidence.api.app import create_app
from confidence.infrastructure.rate_limiter import RedisRateLimiter


async def test_bucket_and_middleware(monkeypatch):
    redis = fakeredis.aioredis.FakeRedis()
    limiter = RedisRateLimiter(redis)
    assert await limiter.allow("a", 1)
    assert not await limiter.allow("a", 1)
    assert await limiter.allow("b", 1)
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("GLOBAL_RPM", "1")
    app = create_app()
    app.state.redis = redis
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        await client.get("/v1/not-found")
        response = await client.get("/v1/not-found")
        assert response.status_code == 429
        assert response.headers["retry-after"] == "60"
        assert (await client.get("/health")).status_code == 200
    await redis.aclose()
