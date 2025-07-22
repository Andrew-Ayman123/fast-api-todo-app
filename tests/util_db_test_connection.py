"""Test database connection utility for FastAPI Todo App."""

from functools import lru_cache

from app.config.database import DatabaseConnection
from app.utils.env_util import get_env


@lru_cache
def get_test_db_connection() -> DatabaseConnection:
    """Get a database connection for testing.

    This uses a test database connection string, which should be configured
    in your environment or settings for testing purposes.

    Returns:
        DatabaseConnection: A database connection instance configured for testing.

    """
    db_connection_url = get_env("TEST_DATABASE_URL", "postgresql+asyncpg://user:password@localhost/test_db")
    return DatabaseConnection(connection_string=db_connection_url, enable_echo=False)
