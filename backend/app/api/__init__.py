"""
API routes package for KidSafe Alphabet Tutor
"""
from fastapi import APIRouter
from .auth import router as auth_router
from .vision import router as vision_router
from .memory import router as memory_router
from .health import router as health_router

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth_router)
api_router.include_router(vision_router)
api_router.include_router(memory_router)
api_router.include_router(health_router)
