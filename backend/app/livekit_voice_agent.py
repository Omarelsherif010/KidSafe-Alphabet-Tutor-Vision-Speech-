#!/usr/bin/env python3
"""
LiveKit Voice Agent for KidSafe Alphabet Tutor
Real-time speech-to-speech using LiveKit's voice pipeline
"""
import asyncio
import json
import logging
import os
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import openai, silero, noise_cancellation

# Import modular services
from app.config import get_settings
from app.services.agent_service import get_agent_service
from app.services.curriculum_service import get_curriculum_service
from app.services.memory_service import get_memory_service
from app.services.safety_service import get_safety_service

# Load environment variables
load_dotenv()
settings = get_settings()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KidSafeAlphabetTutor(Agent):
    """AI Tutor Agent for teaching alphabet with phonics"""
    
    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.agent_service = get_agent_service(session_id)
        
        # Create system instructions
        instructions = self.agent_service.generate_system_prompt()
        super().__init__(instructions=instructions)
    
    def update_memory(self, user_input: str, assistant_response: str):
        """Update memory using modular service"""
        if user_input or assistant_response:
            self.agent_service.memory.add_turn(self.session_id, user_input, assistant_response)
            # Refresh system prompt with updated context
            self.instructions = self.agent_service.generate_system_prompt()
    
    def process_user_input(self, user_input: str) -> tuple:
        """Process user input through safety and curriculum checks"""
        return self.agent_service.process_user_input(user_input)
    
    def generate_response(self, user_input: str) -> tuple:
        """Generate response using agent service"""
        return self.agent_service.generate_response(user_input)

async def entrypoint(ctx: agents.JobContext):
    """Main entry point for the LiveKit voice agent"""
    
    # Extract session ID from room name or use default
    session_id = ctx.room.name or "default"
    
    # Create the tutor agent with session context
    tutor = KidSafeAlphabetTutor(session_id)
    
    # Initialize the voice session with child-optimized settings
    session = AgentSession(
        # Speech-to-Text: OpenAI Whisper optimized for child speech
        stt=openai.STT(
            model=settings.speech_model,
            language="en",
        ),
        # Large Language Model: GPT-4 for conversation
        llm=openai.LLM(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
        ),
        # Text-to-Speech: OpenAI TTS with child-friendly voice
        tts=openai.TTS(
            model=settings.tts_model,
            voice=settings.tts_voice,
            speed=settings.tts_speed,
        ),
        # Voice Activity Detection
        vad=silero.VAD.load(),
        # Turn detection for natural conversation flow (disabled for now)
        # turn_detection=MultilingualModel(),
    )
    
    logger.info(f"🎯 Agent joining room: {ctx.room.name}")
    logger.info(f"🎤 Ready to process child speech input")
    
    # Connect to the room and start the session
    await ctx.connect(auto_subscribe=agents.AutoSubscribe.AUDIO_ONLY)
    logger.info(f"✅ Agent connected to room: {ctx.room.name}")
    
    # Start the session to begin processing audio
    session.start(ctx.room, ctx.participant)
    logger.info(f"🎤 Session started, ready for voice interaction")
    
    # Set up event handlers for memory updates and speech processing
    @session.on("user_input_transcribed")
    def on_user_input_transcribed(event):
        """Called when user speech is transcribed"""
        user_text = event.transcript
        logger.info(f"🎤 USER_INPUT_TRANSCRIBED: Child said: '{user_text}' (final: {event.is_final})")
        
        if event.is_final:
            # Process user input through safety checks
            is_safe, processed_input, metadata = tutor.process_user_input(user_text)
            
            if not is_safe:
                logger.warning(f"Unsafe input detected: {metadata}")
                # Note: Safety response will be handled by the LLM naturally
                # We'll still process the cleaned input
            
            # Update tutor memory with safe input
            tutor.update_memory(processed_input, "")
            
            # Get current state
            state = tutor.agent_service.memory.get_derived_state(session_id)
            
            # Send user speech to frontend for display
            try:
                data_payload = {
                    "type": "user_speech",
                    "text": processed_input,
                    "current_letter": state["current_letter"],
                    "timestamp": None,
                    "interim": False
                }
                logger.info(f"📤 Sending user speech data: {data_payload}")
                
                # Send data synchronously
                ctx.room.local_participant.publish_data(
                    json.dumps(data_payload).encode('utf-8'),
                    reliable=True
                )
                logger.info(f"📤 Sent user speech to frontend: '{user_text}'")
            except Exception as e:
                logger.error(f"❌ Failed to send user speech to frontend: {e}")
        else:
            # Send interim speech for live display
            try:
                data_payload = {
                    "type": "user_speech",
                    "text": user_text,
                    "interim": True,
                    "timestamp": None
                }
                logger.info(f"📤 Sending interim speech: '{user_text}'")
                
                ctx.room.local_participant.publish_data(
                    json.dumps(data_payload).encode('utf-8'),
                    reliable=True
                )
            except Exception as e:
                logger.error(f"❌ Failed to send interim speech: {e}")
    
    @session.on("conversation_item_added")
    def on_conversation_item_added(event):
        """Called when conversation item is added (user or agent)"""
        item = event.item
        logger.info(f"💬 CONVERSATION_ITEM_ADDED: {item.role} said: '{item.text_content}'")
        
        if item.role == "assistant":
            assistant_text = item.text_content
            
            # Get current state from modular service
            state = tutor.agent_service.memory.get_derived_state(session_id)
            
            # Analyze response for progress tracking
            is_correct = any(word in assistant_text.lower() for word in ['great', 'correct', 'right', 'good', 'excellent', 'perfect'])
            needs_practice = any(word in assistant_text.lower() for word in ['try again', 'not quite', 'almost', 'practice'])
            
            logger.info(f"📊 Progress analysis - Correct: {is_correct}, Needs Practice: {needs_practice}")
            
            # Send agent speech to frontend for display
            try:
                data_payload = {
                    "type": "agent_speech",
                    "text": assistant_text,
                    "current_letter": state["current_letter"],
                    "timestamp": None,
                    "progress": {
                        "is_correct": is_correct,
                        "needs_practice": needs_practice
                    },
                    "derived_state": state
                }
                logger.info(f"📤 Sending agent speech data: {data_payload}")
                
                # Send data synchronously
                ctx.room.local_participant.publish_data(
                    json.dumps(data_payload).encode('utf-8'),
                    reliable=True
                )
                logger.info(f"📤 Sent agent speech to frontend: '{assistant_text}'")
            except Exception as e:
                logger.error(f"❌ Failed to send agent speech to frontend: {e}")
            
            # Update memory with the response
            tutor.update_memory("", assistant_text)
    
    # Add data reception handler for debugging
    @ctx.room.on("data_received")
    def on_data_received(data, participant):
        """Called when data is received from participants"""
        try:
            decoded_data = json.loads(data.decode('utf-8'))
            logger.info(f"📨 Data received from {participant.identity}: {decoded_data}")
        except Exception as e:
            logger.error(f"❌ Failed to decode data: {e}")
    
    # Start the voice session with proper audio input handling
    await session.start(
        room=ctx.room,
        agent=tutor,
        room_input_options=RoomInputOptions(
            # Noise cancellation for better child speech recognition
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    
    logger.info(f"✅ Voice session started in room: {ctx.room.name}")
    logger.info(f"🎤 Listening for child speech input...")
    
    # Send initial greeting
    await session.generate_reply(
        instructions="Greet the child and introduce yourself as their alphabet tutor. Ask them to say 'ah' like in apple to start learning letter A."
    )
    
    logger.info("🎯 KidSafe Alphabet Tutor agent started successfully!")

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
