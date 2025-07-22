"""PostgreSQL implementation of User repository.

This module provides a PostgreSQL implementation of the UserRepositoryInterface
using SQLAlchemy ORM for database operations.
"""
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.future import select

from app.config.database import DatabaseConnection
from app.models.user_model import UserModel
from app.repositories.user_repository_interface import UserRepositoryInterface
from app.schemas.user_schema import UserResponse
from app.utils.logger_util import get_logger


class UserPGRepository(UserRepositoryInterface):
    """PostgreSQL implementation of User repository using SQLAlchemy ORM."""

    def __init__(self, database: DatabaseConnection) -> None:
        self.database = database

    async def create_user(self, email: str, username: str, password_hash: str) -> UserResponse:
        get_logger().debug("Creating new user with email: %s", email)
        async with self.database.async_session() as session:
            new_user = UserModel(
                id=uuid.uuid4(),
                email=email,
                username=username,
                password_hash=password_hash,
            )
            session.add(new_user)
            try:
                await session.commit()
                await session.refresh(new_user)
            except IntegrityError:
                await session.rollback()
                raise
            else:
                return UserResponse.model_validate(new_user)

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserModel | None:
        async with self.database.async_session() as session:
            query = select(UserModel).where(UserModel.id == user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> UserModel | None:
        async with self.database.async_session() as session:
            query = select(UserModel).where(UserModel.email == email)
            result = await session.execute(query)
            return result.scalar_one_or_none()

