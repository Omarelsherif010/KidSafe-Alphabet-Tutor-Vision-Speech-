"""
Vision API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.vision_service import get_vision_service

router = APIRouter(prefix="/api/vision", tags=["vision"])

class VisionRequest(BaseModel):
    image_data: str
    session_id: str = "default"

@router.post("/recognize-letter")
async def recognize_letter(request: VisionRequest):
    """Recognize letter from camera image"""
    try:
        vision_service = get_vision_service()
        result = vision_service.detect_letter_from_image(request.image_data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vision recognition failed: {str(e)}")
