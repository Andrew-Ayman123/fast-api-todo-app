"""Defines the dependency injection setup for the FastAPI application.

It provides functions to retrieve instances of database connections, repositories, and services.
These instances are cached for performance and to ensure that the same instance is reused across requests.
"""

from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.config.environment import Settings
from app.utils.build_db_connection import build_postgres_connection_string


@lru_cache
def get_env_settings() -> Settings:
    """Get the application settings instance.

    Returns:
        Settings: The application settings instance with environment variables loaded.

    """
    return Settings()


def get_database_engine_test() -> AsyncEngine:
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


def get_session_maker_test() -> async_sessionmaker[AsyncSession]:
    """Get the session maker instance.

    Returns:
        async_sessionmaker[AsyncSession]: The session maker instance.

    """
    engine = get_database_engine_test()
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
