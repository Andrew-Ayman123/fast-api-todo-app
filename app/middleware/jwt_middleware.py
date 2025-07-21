from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.jwt_service import JWTService
from app.dependencies import get_jwt_service
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger_util import get_logger

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
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
            except Exception as e:
                raise HTTPException(status_code=403, detail="Invalid or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, jwt_service: JWTService):
        super().__init__(app)
        self.jwt_service = jwt_service

    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                scheme, token = auth_header.split()
                if scheme.lower() != "bearer":
                    raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
                payload = self.jwt_service.decode_token(token)
                request.state.user_id = payload["user_id"]
            except Exception:
                raise HTTPException(status_code=403, detail="Invalid or expired token.")
        response = await call_next(request)
        return response
