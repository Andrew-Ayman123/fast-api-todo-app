"""Defines the dependency injection setup for the FastAPI application.

It provides functions to retrieve instances of database connections, repositories, and services.
These instances are cached for performance and to ensure that the same instance is reused across requests.
"""

from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.config.environment import Settings
from app.repositories.todo_pg_repository_impl import TodoPGRepository
from app.repositories.todo_repository_interface import TodoRepositoryInterface
from app.repositories.user_pg_repository_impl import UserPGRepository
from app.repositories.user_repository_interface import UserRepositoryInterface
from app.services.jwt_service import JWTService
from app.services.todo_service import TodoService
from app.services.user_service import UserService
from app.utils.build_db_connection import build_postgres_connection_string


@lru_cache
def get_env_settings() -> Settings:
    """Get the application settings instance.

    Returns:
        Settings: The application settings instance with environment variables loaded.

    """
    return Settings()


def get_database_engine() -> AsyncEngine:
    """Get the database connection instance.

    Returns:
        DatabaseConnection: The database connection instance.

    """
    settings = get_env_settings()

    # Build async connection string for SQLAlchemy
    if settings.database_url:
        # Convert postgresql:// to postgresql+asyncpg:// for async support
        connection_string = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    else:
        # Build async connection string from individual components
        connection_string = build_postgres_connection_string(
            database_user=settings.database_user,
            database_password=settings.database_password,
            database_host=settings.database_host,
            database_port=settings.database_port,
            database_name=settings.database_name,
        )
    return create_async_engine(
        connection_string,
        echo=settings.database_logging,
        future=True,
    )


async def get_database_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session instance.

    This is typically used as a FastAPI dependency.

    Yields:
        AsyncSession: The database session instance.

    """
    session_maker = get_session_maker()
    async with session_maker() as session:
        try:
            yield session
        finally:
            await session.close()



def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """Get the session maker instance.

    Returns:
        async_sessionmaker[AsyncSession]: The session maker instance.

    """
    engine = get_database_engine()
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def get_todo_repository(session: Annotated[AsyncSession, Depends(get_database_session)]) -> TodoRepositoryInterface:
    """Get the Todo repository instance.

    Args:
        session (AsyncSession): The database session instance.

    Returns:
        TodoPGRepository: The Todo repository instance.

    """
    return TodoPGRepository(session=session)


def get_todo_service(todo_repository: Annotated[TodoRepositoryInterface, Depends(get_todo_repository)]) -> TodoService:
    """Get the Todo service instance.

    Args:
        todo_repository (TodoPGRepository, optional): An optional TodoPGRepository instance.
            If not provided, a new one will be created. Defaults to None.

    Returns:
        TodoService: The Todo service instance.

    """
    return TodoService(
        todo_repository=todo_repository,
    )


def get_user_repository(session: Annotated[AsyncSession, Depends(get_database_session)]) -> UserRepositoryInterface:
    """Get the User repository instance.

    Args:
        session (AsyncSession, optional): An optional AsyncSession instance.
            If not provided, a new one will be created. Defaults to Depends(get_database_session).


    Returns:
        UserPGRepository: The User repository instance.

    """
    return UserPGRepository(session=session)


@lru_cache
def get_user_service(
    user_repository: Annotated[UserRepositoryInterface, Depends(get_user_repository)],
) -> UserService:
    """Get the User service instance.

    Args:
        user_repository (UserRepositoryInterface): The User repository instance.

    Returns:
        UserService: The User service instance.

    """
    return UserService(
        user_repository=user_repository,
    )

@lru_cache
def get_jwt_service() -> JWTService:
    """Get the JWT service instance.

    Returns:
        JWTService: The JWT service instance.

    """
    return JWTService(
        secret_key=get_env_settings().jwt_secret_key,
        algorithm=get_env_settings().jwt_algorithm,
        expiration_minutes=get_env_settings().jwt_expiration_minutes,
    )
