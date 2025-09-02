"""
Configuration management for KidSafe Alphabet Tutor
Centralized settings and environment variables
"""
import os
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings with environment variable support"""
    
    def __init__(self):
        # API Keys
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.livekit_api_key: str = os.getenv("LIVEKIT_API_KEY", "")
        self.livekit_api_secret: str = os.getenv("LIVEKIT_API_SECRET", "")
        self.livekit_url: str = os.getenv("LIVEKIT_URL", "")
        
        # Application Settings
        self.app_title: str = "KidSafe Alphabet Tutor"
        self.app_version: str = "1.0.0"
        self.debug: bool = os.getenv("DEBUG", "false").lower() == "true"
        
        # CORS Settings
        self.cors_origins: List[str] = [
            "http://localhost:3000", 
            "http://localhost:3001", 
            "http://127.0.0.1:3000", 
            "http://127.0.0.1:3001"
        ]
        
        # Speech Settings
        self.speech_model: str = "whisper-1"
        self.tts_model: str = "tts-1"
        self.tts_voice: str = "nova"
        self.tts_speed: float = 0.9
        self.llm_model: str = "gpt-4"
        self.llm_temperature: float = 0.7
        
        # Session Settings
        self.memory_turns: int = 3
        self.max_session_duration: int = 3600  # 1 hour
        
        # Safety Settings
        self.content_moderation: bool = True
        self.parental_gate_enabled: bool = True
        
        # Performance Settings
        self.target_latency_ms: int = 1200

# Global settings instance
settings = Settings()

def get_settings() -> Settings:
    """Get application settings"""
    return settings

def validate_required_settings() -> dict:
    """Validate that all required settings are present"""
    missing = []
    
    if not settings.openai_api_key:
        missing.append("OPENAI_API_KEY")
    if not settings.livekit_api_key:
        missing.append("LIVEKIT_API_KEY")
    if not settings.livekit_api_secret:
        missing.append("LIVEKIT_API_SECRET")
    if not settings.livekit_url:
        missing.append("LIVEKIT_URL")
    
    return {
        "valid": len(missing) == 0,
        "missing": missing,
        "configured": {
            "openai": bool(settings.openai_api_key),
            "livekit": bool(settings.livekit_api_key and settings.livekit_api_secret)
        }
    }
