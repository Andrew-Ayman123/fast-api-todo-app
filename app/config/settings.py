from pydantic_settings import BaseSettings
from typing import Optional
from app.utils.env_utils import get_env, get_env_int, get_env_bool

class Settings(BaseSettings):
    """Application settings - configure your database and other settings here"""
    
    # Database settings
    database_url: Optional[str] = get_env("DATABASE_URL")
    database_host: str = get_env("DATABASE_HOST", "localhost")
    database_port: int = get_env_int("DATABASE_PORT", 5432)
    database_name: str = get_env("DATABASE_NAME", "todoapp")
    database_user: str = get_env("DATABASE_USER", "user")
    database_password: str = get_env("DATABASE_PASSWORD", "password")
    database_ssl_mode: Optional[str] = get_env_bool("SSL_MODE", False)
    
    # API settings
    app_name: str = get_env("APP_NAME", "Todo API")
    app_description: str = get_env("APP_DESCRIPTION", "A simple Todo API with repository pattern")
    app_version: str = get_env("APP_VERSION", "1.0.0")
    

# Global settings instance
SETTINGS = Settings()
