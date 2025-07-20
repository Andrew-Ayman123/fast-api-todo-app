# create env read helper functions

from typing import Optional
import os
def get_env(var_name: str, default: Optional[str] = None) -> Optional[str]:
    """Get an environment variable or return a default value if not set."""
    return os.getenv(var_name, default)

def get_env_int(var_name: str, default: Optional[int] = None) -> Optional[int]:
    """Get an environment variable as an integer or return a default value if not set."""
    value = os.getenv(var_name, default)
    return int(value) if value is not None else None

def get_env_bool(var_name: str, default: Optional[bool] = None) -> Optional[bool]:
    """Get an environment variable as a boolean or return a default value if not set."""
    value = os.getenv(var_name, default)
    if value is None:
        return None
    if isinstance(value, str):
        value = value.lower()  # Normalize to lowercase for comparison
    return value in ('true', '1', 'yes')
