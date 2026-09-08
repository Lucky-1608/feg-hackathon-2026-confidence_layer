"""Authentication middleware."""

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
