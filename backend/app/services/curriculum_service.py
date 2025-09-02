"""
Curriculum Service for KidSafe Alphabet Tutor
Manages lesson content, progression, and phonics data
"""
import json
import logging
from ..config import get_settings
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

class CurriculumService:
    """Service for managing alphabet curriculum and lesson progression"""
    
    def __init__(self, lessons_file: str = "app/lessons.json"):
        self.lessons_file = lessons_file
        self.lessons = self._load_lessons()
        self.phoneme_map = self._build_phoneme_map()
        self.curriculum_data = self._load_curriculum_data()
    
    def _load_lessons(self) -> Dict:
        """Load lessons from JSON file"""
        try:
            with open(self.lessons_file, "r") as f:
                lessons = json.load(f)
            logger.info(f"Loaded {len(lessons)} lessons from {self.lessons_file}")
            return lessons
        except FileNotFoundError:
            logger.error(f"Lessons file not found: {self.lessons_file}")
            return self._get_default_lessons()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in lessons file: {e}")
            return self._get_default_lessons()
    
    def _get_default_lessons(self) -> Dict:
        """Fallback lessons if file is missing"""
        return {
            "A": {
                "phoneme": "/æ/",
                "phoneme_clue": "ah",
                "examples": ["Apple", "Ant", "Alligator"],
                "activity": "Can you find something in the room that starts with the letter A?",
                "prompt": "This is the letter A. It makes the 'ah' sound, like in apple. Can you say 'ah'?"
            }
        }
    
    def _build_phoneme_map(self) -> Dict[str, List[str]]:
        """Build phoneme recognition map for all letters"""
        phoneme_map = {}
        for letter, data in self.lessons.items():
            phoneme_map[letter] = [
                data.get("phoneme_clue", "").lower(),
                letter.lower(),
                *[word.lower() for word in data.get("examples", [])]
            ]
        return phoneme_map
    
    def get_lesson(self, letter: str) -> Optional[Dict]:
        """Get lesson data for a specific letter"""
        return self.lessons.get(letter.upper())
    
    def get_current_lesson_prompt(self, letter: str, child_name: Optional[str] = None) -> str:
        """Generate context-aware lesson prompt"""
        lesson = self.get_lesson(letter)
        if not lesson:
            return f"Let's learn about the letter {letter}!"
        
        name_part = f"{child_name}, " if child_name else ""
        prompt_text = lesson.get('prompt', f"Let's learn the letter {letter}!")
        return f"{name_part}{prompt_text}"
    
    def check_pronunciation(self, user_input: str, target_letter: str) -> Tuple[bool, str]:
        """Check if user pronunciation matches target letter"""
        user_lower = user_input.lower()
        target_sounds = self.phoneme_map.get(target_letter.upper(), [])
        
        # Check if any target sounds are in user input
        for sound in target_sounds:
            if sound in user_lower:
                return True, f"Great job! You said the {target_letter} sound correctly!"
        
        lesson = self.get_lesson(target_letter)
        phoneme_clue = lesson.get("phoneme_clue", target_letter.lower()) if lesson else target_letter.lower()
        return False, f"Close! Try the '{phoneme_clue}' sound for {target_letter}. You can do it!"
    
    def get_next_letter(self, current_letter: str) -> Optional[str]:
        """Get the next letter in the alphabet"""
        if not current_letter:
            return "A"
        
        next_ord = ord(current_letter.upper()) + 1
        if next_ord <= ord('Z'):
            return chr(next_ord)
        return None  # Completed all letters
    
    def get_letter_examples(self, letter: str) -> List[str]:
        """Get example words for a letter"""
        lesson = self.get_lesson(letter)
        return lesson.get("examples", []) if lesson else []
    
    def get_letter_activity(self, letter: str) -> str:
        """Get interactive activity for a letter"""
        lesson = self.get_lesson(letter)
        return lesson.get("activity", f"Can you think of a word that starts with {letter}?") if lesson else ""
    
    def is_curriculum_complete(self, current_letter: str) -> bool:
        """Check if the child has completed the full alphabet"""
        return current_letter == "Z" or current_letter is None
    
    def get_progress_percentage(self, current_letter: str) -> float:
        """Calculate learning progress as percentage"""
        if not current_letter:
            return 0.0
        
        letter_index = ord(current_letter.upper()) - ord('A')
        return min((letter_index / 25) * 100, 100.0)  # 26 letters total
    
    def reload_lessons(self) -> bool:
        """Reload lessons from file (useful for hot updates)"""
        try:
            self.lessons = self._load_lessons()
            self.phoneme_map = self._build_phoneme_map()
            return True
        except Exception as e:
            logger.error(f"Failed to reload lessons: {e}")
            return False

# Global curriculum service instance
curriculum_service = CurriculumService()

def get_curriculum_service() -> CurriculumService:
    """Get curriculum service instance"""
    return curriculum_service
