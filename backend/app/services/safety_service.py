"""
Safety Service for KidSafe Alphabet Tutor
Content moderation, parental controls, and COPPA compliance
"""
import logging
import re
from ..config import get_settings
from typing import Dict, List, Optional, Tuple
from better_profanity import profanity

logger = logging.getLogger(__name__)

class SafetyService:
    """Service for content moderation and child safety"""
    
    def __init__(self):
        # Initialize profanity filter
        profanity.load_censor_words()
        
        # PII patterns to detect and block
        self.pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{3}-\d{3}-\d{4}\b',  # Phone
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{1,5}\s+\w+\s+(street|st|avenue|ave|road|rd|drive|dr)\b',  # Address
        ]
        
        # Unsafe topics for children
        self.unsafe_topics = [
            'violence', 'scary', 'death', 'blood', 'weapon', 'gun', 'knife',
            'stranger', 'secret', 'password', 'address', 'phone number',
            'where do you live', 'what school', 'parents work'
        ]
    
    def moderate_content(self, text: str) -> Tuple[bool, str, List[str]]:
        """
        Moderate content for child safety
        Returns: (is_safe, cleaned_text, violations)
        """
        violations = []
        cleaned_text = text
        
        # Check for profanity
        if profanity.contains_profanity(text):
            violations.append("inappropriate_language")
            cleaned_text = profanity.censor(text)
        
        # Check for PII
        pii_found = self._detect_pii(text)
        if pii_found:
            violations.extend(pii_found)
            cleaned_text = self._remove_pii(cleaned_text)
        
        # Check for unsafe topics
        unsafe_found = self._detect_unsafe_topics(text)
        if unsafe_found:
            violations.extend(unsafe_found)
        
        is_safe = len(violations) == 0
        
        if violations:
            logger.warning(f"Content violations detected: {violations}")
        
        return is_safe, cleaned_text, violations
    
    def _detect_pii(self, text: str) -> List[str]:
        """Detect personally identifiable information"""
        violations = []
        
        for pattern in self.pii_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                violations.append("pii_detected")
                break
        
        return violations
    
    def _remove_pii(self, text: str) -> str:
        """Remove PII from text"""
        cleaned = text
        
        for pattern in self.pii_patterns:
            cleaned = re.sub(pattern, "[REMOVED]", cleaned, flags=re.IGNORECASE)
        
        return cleaned
    
    def _detect_unsafe_topics(self, text: str) -> List[str]:
        """Detect unsafe topics for children"""
        violations = []
        text_lower = text.lower()
        
        for topic in self.unsafe_topics:
            if topic in text_lower:
                violations.append(f"unsafe_topic_{topic.replace(' ', '_')}")
        
        return violations
    
    def generate_safe_response(self, violations: List[str]) -> str:
        """Generate appropriate response for safety violations"""
        if "inappropriate_language" in violations:
            return "Let's use kind words! Can we try saying that in a nicer way?"
        
        if any("pii" in v for v in violations):
            return "Remember, we don't share personal information! Let's focus on learning letters instead."
        
        if any("unsafe_topic" in v for v in violations):
            return "That's not something we talk about in our alphabet lessons. Let's learn about letters instead!"
        
        return "Let's keep our conversation about learning letters! What letter would you like to practice?"
    
    def validate_parental_gate(self, answer: str, expected: str) -> bool:
        """Validate parental gate math problem"""
        try:
            return str(answer).strip() == str(expected).strip()
        except:
            return False
    
    def generate_parental_gate_challenge(self) -> Tuple[str, str]:
        """Generate simple math challenge for parental gate"""
        import random
        
        a = random.randint(1, 10)
        b = random.randint(1, 10)
        question = f"What is {a} + {b}?"
        answer = str(a + b)
        
        return question, answer
    
    def is_child_appropriate_request(self, text: str) -> bool:
        """Check if request is appropriate for child learning context"""
        text_lower = text.lower()
        
        # Allow alphabet and learning related requests
        learning_keywords = [
            'letter', 'alphabet', 'sound', 'word', 'learn', 'teach', 'practice',
            'phonics', 'pronunciation', 'spell', 'say', 'repeat'
        ]
        
        # Block inappropriate requests
        inappropriate_keywords = [
            'hack', 'break', 'destroy', 'kill', 'hurt', 'bad words',
            'password', 'login', 'account', 'money', 'buy', 'sell'
        ]
        
        # Check for learning context
        has_learning_context = any(keyword in text_lower for keyword in learning_keywords)
        has_inappropriate_content = any(keyword in text_lower for keyword in inappropriate_keywords)
        
        return has_learning_context and not has_inappropriate_content

# Global safety service instance
safety_service = SafetyService()

def get_safety_service() -> SafetyService:
    """Get safety service instance"""
    return safety_service
