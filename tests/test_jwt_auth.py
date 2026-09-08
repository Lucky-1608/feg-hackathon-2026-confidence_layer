from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import fakeredis.aioredis
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException

from confidence.infrastructure.auth import AuthenticatedUser, JWTAuthProvider, bind_session


@pytest.mark.parametrize("failure", [None, "expired", "signature", "issuer", "audience", "missing"])
def test_jwt_validation(failure):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    provider = JWTAuthProvider("https://identity.test/jwks", "issuer", "audience")
    provider.client = Mock()
    provider.client.get_signing_key_from_jwt.return_value.key = key.public_key()
    claims = dict(
        sub="actor",
        operator_id="operator",
        iss="issuer",
        aud="audience",
        scope="decisions:write",
        exp=datetime.now(UTC) + timedelta(minutes=5),
    )
    if failure == "expired":
        claims["exp"] = datetime.now(UTC) - timedelta(minutes=5)
    if failure == "issuer":
        claims["iss"] = "bad"
    if failure == "audience":
        claims["aud"] = "bad"
    if failure == "missing":
        del claims["exp"]
    signing = rsa.generate_private_key(public_exponent=65537, key_size=2048) if failure == "signature" else key
    token = jwt.encode(claims, signing, algorithm="RS256")
    if failure:
        with pytest.raises(HTTPException) as exc:
            provider.authenticate(token)
        assert exc.value.status_code == 401
    else:
        assert provider.authenticate(token).subject == "actor"


async def test_session_ownership():
    redis = fakeredis.aioredis.FakeRedis()
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(redis=redis)))
    one = AuthenticatedUser(subject="one", operator_id="op", scopes=["decisions:write"])
    two = AuthenticatedUser(subject="two", operator_id="op", scopes=["decisions:write"])
    session = uuid4()
    assert await bind_session(request, one, "one", session, "decisions:write") == one.actor_id
    with pytest.raises(HTTPException):
        await bind_session(request, two, "two", session, "decisions:write")
    with pytest.raises(HTTPException):
        await bind_session(request, one, "two", uuid4(), "decisions:write")
    assert one.actor_id != two.actor_id
    await redis.aclose()
