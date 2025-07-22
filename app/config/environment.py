"""Environment configuration settings for the FastAPI application.

This module defines the application settings using Pydantic's BaseSettings.
It includes database connection settings and API metadata.
"""
from pydantic_settings import BaseSettings

from app.utils.env_util import get_env, get_env_bool, get_env_int


class Settings(BaseSettings):
    """Application settings: database and API configuration."""

    # Database settings
    database_url: str = get_env("DATABASE_URL","postgresql://user:pass@localhost:5432/todoapp")
    database_host: str = get_env("DATABASE_HOST", "localhost")
    database_port: int = get_env_int("DATABASE_PORT", 5432)
    database_name: str = get_env("DATABASE_NAME", "todoapp")
    database_user: str = get_env("DATABASE_USER", "user")
    database_password: str = get_env("DATABASE_PASSWORD", "password")

    database_logging: bool = get_env_bool("DATABASE_LOGGING", "False")

    # API settings
    app_name: str = get_env("APP_NAME", "Todo API")
    app_description: str = get_env("APP_DESCRIPTION", "A simple Todo API with repository pattern")
    app_version: str = get_env("APP_VERSION", "1.0.0")

    server_host: str = get_env("SERVER_HOST", "127.0.0.1")
    server_port: int = get_env_int("SERVER_PORT", 8000)
    server_reload: bool = get_env_bool("SERVER_RELOAD", "True")
    server_log_level: str = get_env("SERVER_LOG_LEVEL", "info")

    # JWT settings
    jwt_secret_key: str = get_env("JWT_SECRET_KEY", "your_secret_key")
    jwt_algorithm: str = get_env("JWT_ALGORITHM", "HS256")
    jwt_expiration_minutes: int = get_env_int("JWT_EXPIRATION_MINUTES", 60)
