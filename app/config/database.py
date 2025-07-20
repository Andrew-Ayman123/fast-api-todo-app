from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator
from app.config.settings import SETTINGS

class DatabaseConnection:
    """Database connection class using SQLAlchemy async engine"""
    
    def __init__(self):
        # Build async connection string for SQLAlchemy
        if SETTINGS.database_url:
            # Convert postgresql:// to postgresql+asyncpg:// for async support
            self.connection_string = SETTINGS.database_url.replace("postgresql://", "postgresql+asyncpg://")
        else:
            # Build async connection string from individual components
            self.connection_string = (
                f"postgresql+asyncpg://{SETTINGS.database_user}:{SETTINGS.database_password}"
                f"@{SETTINGS.database_host}:{SETTINGS.database_port}/{SETTINGS.database_name}"
            )
        
        # Create async engine
        self.engine = create_async_engine(
            self.connection_string,
            echo=True,  # Set to False in production
            future=True
        )
        
        # Create async session factory
        self.async_session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session"""
        async with self.async_session() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self):
        """Close the database engine"""
        await self.engine.dispose()


# Global database instance
database = DatabaseConnection()