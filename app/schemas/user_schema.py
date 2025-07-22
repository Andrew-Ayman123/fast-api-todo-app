"""User schema definitions for FastAPI application."""
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from pydantic import BaseModel, field_validator


class UserCreateRequest(BaseModel):
    """Schema for creating a new user."""

    email: str
    username: str
    password: str

class UserLoginRequest(BaseModel):
    """Schema for user login."""

    email: str
    password: str

class UserResponse(BaseModel):
    """Schema for returning user data."""

    id: str
    email: str
    username: str
    created_at: datetime
    updated_at: datetime

    @field_validator("id", mode="before")
    @classmethod
    def convert_uuid_to_string(cls, v: str | UUID) -> str:
        """Convert UUID to string if needed."""
        if isinstance(v, UUID):
            return str(v)
        if isinstance(v, str):
            return v
        msg = f"Invalid type for id: {type(v)}. Expected UUID or str."
        raise TypeError(msg)

    class Config:
        """Pydantic model configuration."""

        from_attributes = True
        json_encoders: ClassVar[dict] = {datetime: lambda v: v.isoformat()}

class UserResponseWithToken(UserResponse):
    """Schema for returning user data with JWT token."""

    token: str

    class Config:
        """Pydantic model configuration."""

        from_attributes = True
        json_encoders: ClassVar[dict] = {datetime: lambda v: v.isoformat()}
