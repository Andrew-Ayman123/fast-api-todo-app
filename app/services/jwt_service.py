import uuid
from datetime import datetime, timedelta

from jose import jwt


class JWTService:
    """Service for handling JWT token generation and decoding."""

    def __init__(self, secret_key: str, algorithm: str = "HS256", expiration_minutes: int = 60) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expiration_minutes = expiration_minutes

    def generate_token(self, user_id: uuid.UUID) -> str:
        """Generate a JWT token for user authentication."""
        expiration = datetime.now() + timedelta(minutes=self.expiration_minutes)
        payload = {
            "user_id": str(user_id),
            "exp": int(expiration.timestamp()),  # Use standard JWT 'exp' claim with timestamp
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def decode_token(self, token: str) -> dict:
        """Decode a JWT token and return the payload."""
        try:
            # The jose library automatically handles exp claim validation
            return jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError:
            msg = "Token has expired"
            raise ValueError(msg)
        except jwt.JWTError as e:
            msg = "Invalid token"
            raise ValueError(msg) from e

    def decode_token_user_id(self, token: str) -> uuid.UUID:
        """Decode a JWT token and return the user ID."""
        payload = self.decode_token(token)
        return uuid.UUID(payload["user_id"])
