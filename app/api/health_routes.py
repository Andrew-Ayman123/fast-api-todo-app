from fastapi import APIRouter, HTTPException, Depends

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/", summary="Health check endpoint")
async def health_check():
    """Health check endpoint to verify API is running"""
    return {"status": "ok"}