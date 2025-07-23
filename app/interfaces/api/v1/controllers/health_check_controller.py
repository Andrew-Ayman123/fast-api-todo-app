"""Health check controller for verifying API status."""

from fastapi import APIRouter, HTTPException

from app.dependencies import get_database_engine
from app.schemas.health_check_schema import HealthCheckResponse

#versioning is handled in the main file
router = APIRouter(prefix="/health", tags=["health"])

@router.get("/", summary="Health check endpoint")
async def health_check() -> HealthCheckResponse:
    """Perform a health check to verify API status.

    Returns:
        HealthCheckResponse: HealthCheckResponse with status "ok" if the API is healthy.

    Raises:
        HTTPException: 503 if the database connection fails or is not established.

    """
    try:
        get_database_engine()  # Ensure the database connection can be established

    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {e!s}") from e

    return HealthCheckResponse(status="ok")
