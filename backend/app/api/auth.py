"""
Authentication API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..services.auth_service import get_auth_service

router = APIRouter(prefix="/api", tags=["auth"])

class TokenRequest(BaseModel):
    room_name: str
    participant_name: str = "child"

@router.post("/livekit-token")
async def generate_livekit_token(request: TokenRequest):
    """Generate LiveKit access token for room connection"""
    try:
        auth_service = get_auth_service()
        token_data = auth_service.generate_room_token(
            request.room_name, 
            request.participant_name
        )
        return token_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Token generation failed: {str(e)}")
