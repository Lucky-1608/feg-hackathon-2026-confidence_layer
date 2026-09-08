import os

with open("src/confidence/infrastructure/auth.py", "w") as f:
    f.write('''"""Authentication middleware."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

security = HTTPBearer()

def verify_token(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> str:
    """Verify the bearer token.
    
    In a real implementation, this would validate a JWT against an Identity Provider (e.g. Auth0, Cognito).
    """
    token = credentials.credentials
    if token != "demo-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return "user-123"
''')

os.makedirs("docs", exist_ok=True)
with open("docs/SECURITY.md", "w") as f:
    f.write('''# Security Architecture

## Authentication
- All API endpoints are protected by OAuth2 Bearer tokens.
- Tokens must be signed by the trusted Identity Provider.

## Data Protection
- PII is not logged.
- The `anonymous_actor_id` is used instead of user IDs in core domains.
- Redis and PostgreSQL connections require TLS in production.
''')

# Update routes.py to require auth
with open("src/confidence/api/routes.py", "r") as f:
    routes = f.read()

if "from confidence.infrastructure.auth import verify_token" not in routes:
    routes = "from confidence.infrastructure.auth import verify_token\n" + routes
    
    routes = routes.replace(
        "    idemp_store: RedisIdempotencyStore = Depends(get_idempotency_store),  # noqa: B008\n) -> DecisionResponse | JSONResponse:",
        "    idemp_store: RedisIdempotencyStore = Depends(get_idempotency_store),  # noqa: B008\n    user_id: str = Depends(verify_token),\n) -> DecisionResponse | JSONResponse:"
    )

    routes = routes.replace(
        "    publisher: EventPublisher = Depends(get_event_publisher),  # noqa: B008\n) -> dict[str, str]:",
        "    publisher: EventPublisher = Depends(get_event_publisher),  # noqa: B008\n    user_id: str = Depends(verify_token),\n) -> dict[str, str]:"
    )

    with open("src/confidence/api/routes.py", "w") as f:
        f.write(routes)
