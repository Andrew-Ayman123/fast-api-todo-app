"""Defines the dependency injection setup for the FastAPI application.

It provides functions to retrieve instances of database connections, repositories, and services.
These instances are cached for performance and to ensure that the same instance is reused across requests.
"""
from functools import lru_cache

from app.config.database import DatabaseConnection
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

@lru_cache
def get_database() -> DatabaseConnection:
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

    return DatabaseConnection(connection_string, enable_echo=settings.database_logging)


@lru_cache
def get_todo_repository(database: DatabaseConnection | None = None) -> TodoRepositoryInterface:
    """Get the Todo repository instance.

    Args:
        database (DatabaseConnection, optional): An optional DatabaseConnection instance.
            If not provided, a new one will be created. Defaults to None.

    Returns:
        TodoPGRepository: The Todo repository instance.

    """
    if database is None:
        database = get_database()
    return TodoPGRepository(database=database)


@lru_cache
def get_todo_service() -> TodoService:
    """Get the Todo service instance.

    Args:
        todo_repository (TodoPGRepository, optional): An optional TodoPGRepository instance.
            If not provided, a new one will be created. Defaults to None.

    Returns:
        TodoService: The Todo service instance.

    """
    todo_repository = get_todo_repository()

    return TodoService(
        todo_repository=todo_repository,
    )


@lru_cache
def get_user_repository(database: DatabaseConnection | None = None) -> UserRepositoryInterface:
    """Get the User repository instance.

    Args:
        database (DatabaseConnection, optional): An optional DatabaseConnection instance.
            If not provided, a new one will be created. Defaults to None.

    Returns:
        UserPGRepository: The User repository instance.

    """
    if database is None:
        database = get_database()
    return UserPGRepository(database=database)

@lru_cache
def get_user_service() -> UserService:
    """Get the User service instance.

    Returns:
        UserService: The User service instance.

    """
    user_repository = get_user_repository()

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
