from typing import TYPE_CHECKING

from fastapi import HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.dependencies import get_jwt_service

if TYPE_CHECKING:
    from app.services.jwt_service import JWTService


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True) -> None:
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            jwt_service: JWTService = get_jwt_service()
            try:
                # get_logger().debug(f"User ID from token: {payload}")
                payload = jwt_service.decode_token(credentials.credentials)
                request.state.user_id = payload["user_id"]
            except Exception:
                raise HTTPException(status_code=403, detail="Invalid or expired token.")
            return credentials.credentials
        raise HTTPException(status_code=403, detail="Invalid authorization code.")
