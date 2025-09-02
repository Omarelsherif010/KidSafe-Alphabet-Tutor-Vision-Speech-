from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.config import get_settings, validate_required_settings
from app.services.auth_service import get_auth_service
from app.services.vision_service import get_vision_service
from app.services.memory_service import get_memory_service
from app.api import api_router

# Load environment variables
load_dotenv()
settings = get_settings()

app = FastAPI(title=settings.app_title, version=settings.app_version)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main_livekit:app", host="0.0.0.0", port=8000, reload=True)
