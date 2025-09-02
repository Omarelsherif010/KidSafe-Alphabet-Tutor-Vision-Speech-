"""
Agent Service for KidSafe Alphabet Tutor
Orchestrates the AI tutoring logic and conversation flow
"""
import logging
from typing import Dict, Optional, Tuple
from .curriculum_service import get_curriculum_service
from .memory_service import get_memory_service
from .safety_service import get_safety_service
from ..config import get_settings

logger = logging.getLogger(__name__)

class AgentService:
    """Service for AI agent logic and conversation orchestration"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.curriculum = get_curriculum_service()
        self.memory = get_memory_service()
        self.safety = get_safety_service()
        self.settings = get_settings()
    
    def generate_system_prompt(self) -> str:
        """Generate context-aware system prompt for the AI agent"""
        state = self.memory.get_derived_state(self.session_id)
        current_letter = state["current_letter"]
        child_name = state.get("child_name")
        
        lesson = self.curriculum.get_lesson(current_letter)
        name_part = f"The child's name is {child_name}. " if child_name else ""
        
        lesson_info = ""
        if lesson:
            lesson_info = f"""
Current lesson: Letter {current_letter}
- Sound: {lesson.get('phoneme_clue', current_letter.lower())}
- Examples: {', '.join(lesson.get('examples', []))}
- Activity: {lesson.get('activity', '')}
"""
        
        return f"""You are a friendly, patient alphabet tutor for young children (ages 3-7).

{name_part}{lesson_info}

Your role:
- Teach phonics (letter sounds) in a playful, encouraging way
- Give gentle pronunciation feedback for the letter {current_letter}
- Keep responses very short (1-2 sentences max)
- Use simple, child-friendly language
- Focus on the phonetic sound of the current letter
- Be extremely encouraging and positive

Guidelines:
- If child says the correct sound for {current_letter}, praise enthusiastically and move to next letter
- If incorrect, gently correct with the right sound and encourage them to try again
- Use phrases like "Great job!", "You're doing amazing!", "Let's try together!"
- Never be harsh or critical - always be supportive
- If child tells you their name, remember it and use it

Remember: You're helping a young child learn, so be patient, kind, and encouraging!"""
    
    def process_user_input(self, user_input: str) -> Tuple[bool, str, Dict]:
        """
        Process user input through safety and curriculum checks
        Returns: (is_safe, processed_input, metadata)
        """
        # Safety check
        is_safe, cleaned_input, violations = self.safety.moderate_content(user_input)
        
        if not is_safe:
            safety_response = self.safety.generate_safe_response(violations)
            return False, safety_response, {"violations": violations}
        
        # Check if appropriate for learning context
        if not self.safety.is_child_appropriate_request(cleaned_input):
            return False, "Let's focus on learning letters! What letter would you like to practice?", {"inappropriate_request": True}
        
        return True, cleaned_input, {}
    
    def generate_response(self, user_input: str) -> Tuple[str, Dict]:
        """
        Generate AI response with curriculum and memory context
        Returns: (response_text, metadata)
        """
        # Get current state
        state = self.memory.get_derived_state(self.session_id)
        current_letter = state["current_letter"]
        
        # Check pronunciation
        is_correct, feedback = self.curriculum.check_pronunciation(user_input, current_letter)
        
        metadata = {
            "current_letter": current_letter,
            "is_correct": is_correct,
            "needs_practice": not is_correct,
            "progress_made": False
        }
        
        # Handle letter progression
        if is_correct:
            next_letter = self.curriculum.get_next_letter(current_letter)
            if next_letter:
                self.memory.progress_letter(self.session_id, current_letter, next_letter)
                metadata["progress_made"] = True
                metadata["new_letter"] = next_letter
                
                # Generate progression response
                next_lesson = self.curriculum.get_lesson(next_letter)
                if next_lesson:
                    response = f"{feedback} Now let's learn {next_letter}! {next_lesson.get('prompt', '')}"
                else:
                    response = f"{feedback} Great job! Let's try the letter {next_letter}."
            else:
                response = f"{feedback} Wow! You've learned the whole alphabet! You're amazing!"
                metadata["curriculum_complete"] = True
        else:
            response = feedback
        
        return response, metadata
    
    def handle_special_commands(self, user_input: str) -> Optional[Tuple[str, Dict]]:
        """Handle special commands like help, repeat, etc."""
        user_lower = user_input.lower().strip()
        
        if user_lower in ["help", "what do i do", "i don't know"]:
            state = self.memory.get_derived_state(self.session_id)
            current_letter = state["current_letter"]
            lesson = self.curriculum.get_lesson(current_letter)
            
            if lesson:
                return lesson.get("prompt", f"Let's practice the letter {current_letter}!"), {"type": "help"}
        
        elif user_lower in ["repeat", "say that again", "what"]:
            # Get last assistant message
            history = self.memory.get_conversation_history(self.session_id, limit=2)
            if history and history[-1].get("type") == "assistant":
                return history[-1]["text"], {"type": "repeat"}
        
        elif "next letter" in user_lower or "skip" in user_lower:
            state = self.memory.get_derived_state(self.session_id)
            current_letter = state["current_letter"]
            next_letter = self.curriculum.get_next_letter(current_letter)
            
            if next_letter:
                self.memory.progress_letter(self.session_id, current_letter, next_letter)
                lesson = self.curriculum.get_lesson(next_letter)
                prompt = lesson.get("prompt", f"Let's learn {next_letter}!") if lesson else f"Let's try {next_letter}!"
                return f"Okay! {prompt}", {"type": "skip", "new_letter": next_letter}
        
        return None
    
    def get_session_context(self) -> Dict:
        """Get full session context for the agent"""
        state = self.memory.get_derived_state(self.session_id)
        history = self.memory.get_conversation_history(self.session_id)
        stats = self.memory.get_session_stats(self.session_id)
        
        return {
            "derived_state": state,
            "conversation_history": history,
            "session_stats": stats,
            "current_lesson": self.curriculum.get_lesson(state["current_letter"])
        }

def get_agent_service(session_id: str) -> AgentService:
    """Get agent service instance for session"""
    return AgentService(session_id)
