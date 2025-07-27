"""Environment variable utility functions for the App.

These functions help in retrieving environment variables with optional default values.
They handle different data types such as string, integer, and boolean.
"""

import os


def get_env(var_name: str, default: str) -> str:
    """Get an environment variable or return a default value if not set.

    Args:
        var_name: The name of the environment variable to retrieve
        default: The default value to return if the variable is not set

    Returns:
        The value of the environment variable or the default value if not set

    """
    return os.getenv(var_name, default)


def get_env_int(var_name: str, default: int) -> int:
    """Get an environment variable as an integer or return a default value if not set.

    Args:
        var_name: The name of the environment variable to retrieve
        default: The default value to return if the variable is not set

    Returns:
        The value of the environment variable as an integer or the default value if not set

    """
    value = os.getenv(var_name, default)
    return int(value)


def get_env_bool(var_name: str, default: str) -> bool:
    """Retrieve an environment variable and interpret it as a boolean.

    Args:
        var_name: Name of the environment variable to fetch.
        default: Default string value to use if the variable is not set (e.g., 'true', 'false', '1', '0').

    Returns:
        Boolean value of the environment variable, or None if not set and no default is provided.

    """
    value = os.getenv(var_name, default)
    if value is None:
        return None
    if isinstance(value, str):
        value = value.lower()  # Normalize to lowercase for comparison
    return value in ("true", "1", "yes")
