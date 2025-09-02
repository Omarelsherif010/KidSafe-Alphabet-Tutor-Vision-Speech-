"""
Health check API endpoints
"""
from fastapi import APIRouter
from ..config import get_settings, validate_required_settings

router = APIRouter(tags=["health"])

@router.get("/")
def read_root():
    settings = get_settings()
    return {"message": "KidSafe Alphabet Tutor - LiveKit Backend Ready!"}

@router.get("/health")
def health_check():
    """Health check endpoint"""
    settings = get_settings()
    validation = validate_required_settings()
    return {
        "status": "healthy" if validation["valid"] else "degraded",
        "configuration": validation["configured"],
        "missing_settings": validation["missing"],
        "app_version": settings.app_version
    }
