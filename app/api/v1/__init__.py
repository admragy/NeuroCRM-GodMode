"""
API v1 Router
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def api_root():
    """API v1 root endpoint"""
    return {
        "version": "v1",
        "status": "operational",
        "message": "OmniCRM God Mode API v1"
    }


@router.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"ping": "pong"}
