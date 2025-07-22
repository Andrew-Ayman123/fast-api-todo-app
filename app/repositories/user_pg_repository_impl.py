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
from app.utils.logger_util import get_logger


class UserPGRepository(UserRepositoryInterface):
    """PostgreSQL implementation of User repository using SQLAlchemy ORM."""

    def __init__(self, database: DatabaseConnection) -> None:
        """Initialize the UserPGRepository with a database connection.

        Args:
            database (DatabaseConnection): An instance of DatabaseConnection for database operations.

        """
        self.database = database

    async def create_user(self, email: str, username: str, password_hash: str) -> UserModel | None:
        """Create a new user in the PostgreSQL database.

        Args:
            email (str): The user's email.
            username (str): The user's username.
            password_hash (str): The user's hashed password.

        Returns:
            UserModel | None: The created user data.

        """
        get_logger().debug("Creating new user with email: %s", email)
        async with self.database.async_session() as session:
            # Instantiate UserModel using keyword arguments matching its fields
            new_user = UserModel(
                id=uuid.uuid4(),
                email=email,
                username=username,
                password=password_hash,
            )
            session.add(new_user)
            try:
                await session.commit()
                await session.refresh(new_user)
            except IntegrityError:
                await session.rollback()
                raise
            else:
                return new_user

    async def get_user_by_id(self, user_id: uuid.UUID) -> UserModel | None:
        """Get user data by ID.

        Args:
            user_id (UUID): The user's UUID.

        Returns:
            UserModel | None: The user data if found, else None.

        """
        async with self.database.async_session() as session:
            query = select(UserModel).where(UserModel.id == user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> UserModel | None:
        """Get user data by email.

        Args:
            email (str): The user's email.

        Returns:
            UserModel | None: The user data if found, else None.

        """
        async with self.database.async_session() as session:
            query = select(UserModel).where(UserModel.email == email)
            result = await session.execute(query)
            return result.scalar_one_or_none()

