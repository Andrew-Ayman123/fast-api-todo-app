"""Build a PostgreSQL connection string for asynchronous database connections using asyncpg."""

def build_postgres_connection_string(
    database_user: str,
    database_password: str,
    database_host: str,
    database_port: str,
    database_name: str,
) -> str:
    """Build async PostgreSQL connection string.

    Args:
        database_user (str): Database username
        database_password (str): Database password
        database_host (str): Database host
        database_port (str): Database port
        database_name (str): Database name

    Returns:
        str: Async PostgreSQL connection string

    """
    # Build async connection string from individual components
    return (
        f"postgresql+asyncpg://{database_user}:{database_password}"
        f"@{database_host}:{database_port}/{database_name}"
    )
