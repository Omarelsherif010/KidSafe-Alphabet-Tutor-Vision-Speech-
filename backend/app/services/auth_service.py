"""
Authentication Service for KidSafe Alphabet Tutor
LiveKit token generation and session management
"""
import logging
from typing import Dict, Optional
from livekit import api
from ..config import get_settings

logger = logging.getLogger(__name__)

class AuthService:
    """Service for LiveKit authentication and token management"""
    
    def __init__(self):
        self.settings = get_settings()
    
    def generate_room_token(self, room_name: str, participant_name: str = "child") -> Dict:
        """Generate LiveKit access token for room connection"""
        try:
            if not self.settings.livekit_api_key or not self.settings.livekit_api_secret:
                raise ValueError("LiveKit credentials not configured")
            
            # Create access token with appropriate permissions
            token = api.AccessToken(
                self.settings.livekit_api_key, 
                self.settings.livekit_api_secret
            ).with_identity(participant_name) \
             .with_name(participant_name) \
             .with_grants(api.VideoGrants(
                 room_join=True,
                 room=room_name,
                 can_publish=True,
                 can_subscribe=True,
             )).to_jwt()
            
            logger.info(f"Generated token for {participant_name} in room {room_name}")
            
            return {
                "token": token,
                "url": self.settings.livekit_url,
                "room_name": room_name,
                "participant_name": participant_name
            }
            
        except Exception as e:
            logger.error(f"Token generation failed: {e}")
            raise
    
    def validate_session(self, session_id: str) -> bool:
        """Validate if session is still active and valid"""
        # Basic validation - can be extended with more sophisticated checks
        return session_id and len(session_id) > 0
    
    def create_agent_token(self, room_name: str) -> str:
        """Generate token specifically for the AI agent"""
        try:
            token = api.AccessToken(
                self.settings.livekit_api_key,
                self.settings.livekit_api_secret
            ).with_identity("alphabet_tutor_agent") \
             .with_name("AI Alphabet Tutor") \
             .with_grants(api.VideoGrants(
                 room_join=True,
                 room=room_name,
                 can_publish=True,
                 can_subscribe=True,
                 can_publish_data=True,
             )).to_jwt()
            
            logger.info(f"Generated agent token for room {room_name}")
            return token
            
        except Exception as e:
            logger.error(f"Agent token generation failed: {e}")
            raise

# Global auth service instance
auth_service = AuthService()

def get_auth_service() -> AuthService:
    """Get authentication service instance"""
    return auth_service
