"""
Memory Service for KidSafe Alphabet Tutor
Manages 3-turn conversation memory and derived state
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from ..config import get_settings

logger = logging.getLogger(__name__)

class MemoryService:
    """Service for managing session memory and derived state"""
    
    def __init__(self, max_turns: int = 3):
        self.max_turns = max_turns
        self.sessions: Dict[str, Dict] = {}
    
    def get_session(self, session_id: str) -> Dict:
        """Get or create session memory"""
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "history": [],
                "derived_state": {
                    "current_letter": "A",
                    "child_name": None,
                    "difficulty": "easy",
                    "last_mistake": None,
                    "session_start": datetime.now().isoformat(),
                    "total_interactions": 0
                }
            }
        return self.sessions[session_id]
    
    def add_turn(self, session_id: str, user_input: str, assistant_response: str) -> Dict:
        """Add a conversation turn and update derived state"""
        session = self.get_session(session_id)
        
        # Add conversation turns
        session["history"].append({
            "type": "user",
            "text": user_input,
            "timestamp": datetime.now().isoformat()
        })
        session["history"].append({
            "type": "assistant", 
            "text": assistant_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last N turns (N*2 for user+assistant pairs)
        max_entries = self.max_turns * 2
        session["history"] = session["history"][-max_entries:]
        
        # Update derived state
        self._update_derived_state(session, user_input, assistant_response)
        
        session["derived_state"]["total_interactions"] += 1
        
        logger.info(f"Updated session {session_id}: {len(session['history'])} turns")
        return session
    
    def _update_derived_state(self, session: Dict, user_input: str, assistant_response: str):
        """Update derived state based on conversation"""
        state = session["derived_state"]
        user_lower = user_input.lower()
        
        # Extract child's name
        if "my name is" in user_lower or "i'm" in user_lower or "i am" in user_lower:
            name_candidates = []
            
            if "my name is" in user_lower:
                name_part = user_lower.split("my name is")[-1].strip()
                if name_part:
                    name_candidates.append(name_part.split()[0])
            
            if "i'm" in user_lower:
                name_part = user_lower.split("i'm")[-1].strip()
                if name_part:
                    name_candidates.append(name_part.split()[0])
            
            if "i am" in user_lower:
                name_part = user_lower.split("i am")[-1].strip()
                if name_part:
                    name_candidates.append(name_part.split()[0])
            
            for candidate in name_candidates:
                if candidate and candidate.isalpha() and len(candidate) > 1:
                    state["child_name"] = candidate.capitalize()
                    logger.info(f"Child's name identified: {state['child_name']}")
                    break
        
        # Track difficulty based on response patterns
        if any(word in assistant_response.lower() for word in ['try again', 'not quite', 'almost']):
            state["last_mistake"] = user_input
            # Don't change difficulty immediately, wait for pattern
        elif any(word in assistant_response.lower() for word in ['great', 'excellent', 'perfect']):
            state["last_mistake"] = None
    
    def progress_letter(self, session_id: str, from_letter: str, to_letter: str) -> bool:
        """Progress to next letter in curriculum"""
        session = self.get_session(session_id)
        old_letter = session["derived_state"]["current_letter"]
        session["derived_state"]["current_letter"] = to_letter
        
        logger.info(f"Session {session_id}: Letter progression {old_letter} → {to_letter}")
        return True
    
    def get_derived_state(self, session_id: str) -> Dict:
        """Get current derived state for session"""
        session = self.get_session(session_id)
        return session["derived_state"].copy()
    
    def get_conversation_history(self, session_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history for session"""
        session = self.get_session(session_id)
        history = session["history"]
        
        if limit:
            return history[-limit:]
        return history.copy()
    
    def clear_session(self, session_id: str) -> bool:
        """Clear session memory (for parental controls)"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Cleared session {session_id}")
            return True
        return False
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Get session statistics"""
        session = self.get_session(session_id)
        state = session["derived_state"]
        
        return {
            "session_id": session_id,
            "current_letter": state["current_letter"],
            "child_name": state["child_name"],
            "total_interactions": state["total_interactions"],
            "session_duration": self._calculate_session_duration(state["session_start"]),
            "conversation_turns": len(session["history"]) // 2
        }
    
    def _calculate_session_duration(self, start_time: str) -> int:
        """Calculate session duration in seconds"""
        try:
            start = datetime.fromisoformat(start_time)
            duration = (datetime.now() - start).total_seconds()
            return int(duration)
        except:
            return 0

# Global memory service instance
memory_service = MemoryService()

def get_memory_service() -> MemoryService:
    """Get memory service instance"""
    return memory_service
