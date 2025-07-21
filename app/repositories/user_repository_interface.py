"""User repository interface module.

This module defines the abstract interface for User repository operations.
"""
import uuid
from abc import ABC, abstractmethod

from app.models.user_model import UserModel
from app.schemas.user_schema import UserCreateRequest, UserLoginRequest


class UserRepositoryInterface(ABC):
    @abstractmethod
    async def create_user(self, email: str, username: str, password_hash: str) -> UserModel:
        """Create a new user and return the user model."""
        pass

    @abstractmethod
    async def get_user_by_id(self, user_id: uuid.UUID) -> UserModel | None:
        """Get user data by ID."""
        pass

    @abstractmethod
    async def get_user_by_email(self, email: str) -> UserModel | None:
        """Get user data by email."""
        pass