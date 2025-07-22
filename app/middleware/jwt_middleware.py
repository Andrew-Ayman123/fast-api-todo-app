
"""JWT middleware for FastAPI to handle Bearer token authentication."""
from typing import TYPE_CHECKING

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.dependencies import get_jwt_service

if TYPE_CHECKING:
    from app.services.jwt_service import JWTService


class JWTBearer(HTTPBearer):
    """Custom HTTPBearer class for JWT authentication in FastAPI.

    Validates Bearer token and sets user_id in request state.
    """

    def __init__(self) -> None:
        """Initialize JWTBearer.

        Args:
            auto_error (bool): Whether to automatically raise errors.

        """
        super().__init__(auto_error=True)

    async def __call__(self, request: Request) -> str:
        """Validate JWT Bearer token from request.

        Args:
            request (Request): FastAPI request object.

        Returns:
            str: JWT token string if valid.

        Raises:
            403 HTTPException: If authentication fails.

        """
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            jwt_service: JWTService = get_jwt_service()
            try:
                payload = jwt_service.decode_token(credentials.credentials)
                request.state.user_id = payload["user_id"]
            except Exception as e:
                raise HTTPException(status_code=403, detail="Invalid or expired token.") from e
            return credentials.credentials
        raise HTTPException(status_code=403, detail="Invalid authorization code.")
