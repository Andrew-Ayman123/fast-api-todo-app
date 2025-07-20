import uvicorn
from app.utils.env_utils import get_env, get_env_int, get_env_bool

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=get_env("HOST", "0.0.0.0"),
        port=get_env_int("PORT", 8000),
        reload=get_env_bool("RELOAD", True),
        log_level=get_env("LOG_LEVEL", "info")
    )
