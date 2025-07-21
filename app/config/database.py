"""Database connection management using SQLAlchemy async engine."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class DatabaseConnection:
    """Database connection class using SQLAlchemy async engine."""

    def __init__(self, connection_string: str, *, enable_echo: bool = True) -> None:
        """Initialize database connection with provided connection string.

        Args:
            connection_string: Database connection string (should use postgresql+asyncpg:// for async support)
            enable_echo (bool, optional): Whether to log SQL queries. Defaults to True.

        """
        self.connection_string = connection_string

        # Create async engine
        self.engine = create_async_engine(
            self.connection_string,
            echo=enable_echo,
            future=True,
        )

        # Create async session factory
        self.async_session = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session.

        Returns:
            AsyncGenerator[AsyncSession, None]: An async session generator for database operations.

        """
        async with self.async_session() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def close(self) -> None:
        """Close the database engine."""
        await self.engine.dispose()
