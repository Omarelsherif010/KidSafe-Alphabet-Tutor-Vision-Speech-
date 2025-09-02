#!/usr/bin/env python3
"""
Runner script for LiveKit Voice Agent
"""
import os
import sys
from dotenv import load_dotenv

def main():
    # Load environment variables
    load_dotenv()
    
    # Check required environment variables
    required_vars = ["OPENAI_API_KEY", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET", "LIVEKIT_URL"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file")
        return
    
    print("🎯 KidSafe Alphabet Tutor - LiveKit Voice Agent")
    print("✅ Environment configured")
    print("🚀 Starting LiveKit agent...")
    print("📞 Connect to the room to start the speech-to-speech session")
    
    # Import and run the agent
    from livekit import agents
    from app.livekit_voice_agent import entrypoint
    
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))

if __name__ == "__main__":
    main()
