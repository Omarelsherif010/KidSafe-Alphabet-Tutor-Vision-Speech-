import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class PhonemeAnalysis:
    """Result of phoneme analysis"""
    detected_phonemes: List[str]
    expected_phonemes: List[str]
    accuracy_score: float
    feedback: str
    pronunciation_tips: List[str]

class PhonemeService:
    """Service for phoneme detection and pronunciation feedback"""
    
    def __init__(self):
        # Phoneme mappings for A-Z letters
        self.letter_phonemes = {
            'A': ['/eɪ/', '/æ/'],  # Long A, short A
            'B': ['/biː/'],
            'C': ['/siː/'],
            'D': ['/diː/'],
            'E': ['/iː/', '/ɛ/'],  # Long E, short E
            'F': ['/ɛf/'],
            'G': ['/dʒiː/'],
            'H': ['/eɪtʃ/'],
            'I': ['/aɪ/', '/ɪ/'],  # Long I, short I
            'J': ['/dʒeɪ/'],
            'K': ['/keɪ/'],
            'L': ['/ɛl/'],
            'M': ['/ɛm/'],
            'N': ['/ɛn/'],
            'O': ['/oʊ/', '/ɒ/'],  # Long O, short O
            'P': ['/piː/'],
            'Q': ['/kjuː/'],
            'R': ['/ɑːr/'],
            'S': ['/ɛs/'],
            'T': ['/tiː/'],
            'U': ['/juː/', '/ʌ/'],  # Long U, short U
            'V': ['/viː/'],
            'W': ['/dʌbəljuː/'],
            'X': ['/ɛks/'],
            'Y': ['/waɪ/'],
            'Z': ['/ziː/', '/zɛd/']  # American/British
        }
        
        # Common pronunciation patterns
        self.phoneme_patterns = {
            '/eɪ/': ['ay', 'a_e', 'ai'],
            '/æ/': ['a'],
            '/iː/': ['ee', 'ea', 'e_e'],
            '/ɛ/': ['e'],
            '/aɪ/': ['i_e', 'igh', 'y'],
            '/ɪ/': ['i'],
            '/oʊ/': ['o_e', 'oa', 'ow'],
            '/ɒ/': ['o'],
            '/juː/': ['u_e', 'ue'],
            '/ʌ/': ['u']
        }
        
        # Pronunciation tips for common issues
        self.pronunciation_tips = {
            '/eɪ/': "Say 'ay' like in 'play'",
            '/æ/': "Say 'a' like in 'cat'",
            '/iː/': "Say 'ee' like in 'see'",
            '/ɛ/': "Say 'e' like in 'bed'",
            '/aɪ/': "Say 'i' like in 'kite'",
            '/ɪ/': "Say 'i' like in 'sit'",
            '/oʊ/': "Say 'o' like in 'go'",
            '/ɒ/': "Say 'o' like in 'hot'",
            '/juː/': "Say 'u' like in 'cute'",
            '/ʌ/': "Say 'u' like in 'cup'"
        }

    def analyze_pronunciation(self, 
                            audio_transcript: str, 
                            target_letter: str,
                            phonics_mode: bool = True) -> PhonemeAnalysis:
        """
        Analyze pronunciation from audio transcript
        
        Args:
            audio_transcript: Text from speech recognition
            target_letter: Expected letter (A-Z)
            phonics_mode: Whether to focus on phonics vs letter names
            
        Returns:
            PhonemeAnalysis with feedback and tips
        """
        try:
            target_letter = target_letter.upper()
            if target_letter not in self.letter_phonemes:
                return self._create_error_analysis("Invalid target letter")
            
            # Clean and normalize transcript
            transcript = self._normalize_transcript(audio_transcript)
            
            # Get expected phonemes for target letter
            expected_phonemes = self.letter_phonemes[target_letter]
            
            # Detect phonemes in transcript
            detected_phonemes = self._detect_phonemes(transcript, target_letter)
            
            # Calculate accuracy
            accuracy = self._calculate_accuracy(detected_phonemes, expected_phonemes)
            
            # Generate feedback
            feedback = self._generate_feedback(
                detected_phonemes, 
                expected_phonemes, 
                accuracy, 
                target_letter,
                phonics_mode
            )
            
            # Get pronunciation tips
            tips = self._get_pronunciation_tips(
                detected_phonemes, 
                expected_phonemes, 
                target_letter
            )
            
            return PhonemeAnalysis(
                detected_phonemes=detected_phonemes,
                expected_phonemes=expected_phonemes,
                accuracy_score=accuracy,
                feedback=feedback,
                pronunciation_tips=tips
            )
            
        except Exception as e:
            logger.error(f"Phoneme analysis failed: {e}")
            return self._create_error_analysis("Analysis failed")

    def _normalize_transcript(self, transcript: str) -> str:
        """Normalize transcript for phoneme analysis"""
        if not transcript:
            return ""
        
        # Convert to lowercase and remove punctuation
        normalized = re.sub(r'[^\w\s]', '', transcript.lower())
        
        # Remove extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized

    def _detect_phonemes(self, transcript: str, target_letter: str) -> List[str]:
        """Detect phonemes in transcript based on common patterns"""
        detected = []
        
        # Simple pattern matching for phoneme detection
        # In a real implementation, this would use advanced speech analysis
        
        # Check for letter name pronunciation
        if target_letter.lower() in transcript:
            detected.extend(self.letter_phonemes[target_letter])
        
        # Check for phonetic patterns
        for phoneme, patterns in self.phoneme_patterns.items():
            for pattern in patterns:
                if pattern in transcript:
                    detected.append(phoneme)
        
        return list(set(detected))  # Remove duplicates

    def _calculate_accuracy(self, 
                          detected: List[str], 
                          expected: List[str]) -> float:
        """Calculate pronunciation accuracy score"""
        if not expected:
            return 0.0
        
        if not detected:
            return 0.0
        
        # Calculate overlap between detected and expected phonemes
        matches = len(set(detected) & set(expected))
        total_expected = len(expected)
        
        # Base accuracy on matches
        accuracy = matches / total_expected
        
        # Bonus for exact matches
        if set(detected) == set(expected):
            accuracy = min(1.0, accuracy + 0.2)
        
        return round(accuracy, 2)

    def _generate_feedback(self, 
                          detected: List[str],
                          expected: List[str],
                          accuracy: float,
                          target_letter: str,
                          phonics_mode: bool) -> str:
        """Generate pronunciation feedback"""
        
        if accuracy >= 0.8:
            return f"Excellent! You pronounced '{target_letter}' perfectly!"
        elif accuracy >= 0.6:
            return f"Good job! Your '{target_letter}' sound is almost perfect."
        elif accuracy >= 0.4:
            return f"Nice try! Let's practice the '{target_letter}' sound together."
        else:
            if phonics_mode:
                return f"Let's work on the '{target_letter}' sound. Listen carefully..."
            else:
                return f"Let's practice saying the letter '{target_letter}' together."

    def _get_pronunciation_tips(self, 
                               detected: List[str],
                               expected: List[str],
                               target_letter: str) -> List[str]:
        """Get specific pronunciation tips"""
        tips = []
        
        # Get tips for expected phonemes not detected
        missing_phonemes = set(expected) - set(detected)
        
        for phoneme in missing_phonemes:
            if phoneme in self.pronunciation_tips:
                tips.append(self.pronunciation_tips[phoneme])
        
        # Add general tips
        if not tips:
            tips.append(f"Try saying '{target_letter}' clearly and slowly")
        
        # Add mouth position tips for common letters
        mouth_tips = {
            'A': "Open your mouth wide",
            'E': "Smile while saying the sound",
            'I': "Make your mouth small and round",
            'O': "Make your lips round like a circle",
            'U': "Push your lips forward"
        }
        
        if target_letter in mouth_tips:
            tips.append(mouth_tips[target_letter])
        
        return tips[:3]  # Limit to 3 tips

    def _create_error_analysis(self, error_msg: str) -> PhonemeAnalysis:
        """Create error analysis result"""
        return PhonemeAnalysis(
            detected_phonemes=[],
            expected_phonemes=[],
            accuracy_score=0.0,
            feedback=f"Sorry, I couldn't analyze that. {error_msg}",
            pronunciation_tips=["Please try speaking clearly into the microphone"]
        )

    def get_letter_sounds(self, letter: str) -> Dict[str, any]:
        """Get all sounds for a specific letter"""
        letter = letter.upper()
        if letter not in self.letter_phonemes:
            return {}
        
        return {
            'letter': letter,
            'phonemes': self.letter_phonemes[letter],
            'tips': self._get_pronunciation_tips([], self.letter_phonemes[letter], letter),
            'examples': self._get_sound_examples(letter)
        }

    def _get_sound_examples(self, letter: str) -> List[str]:
        """Get example words for letter sounds"""
        examples = {
            'A': ['apple', 'cake', 'cat'],
            'B': ['ball', 'book', 'baby'],
            'C': ['cat', 'car', 'cup'],
            'D': ['dog', 'door', 'duck'],
            'E': ['egg', 'tree', 'bed'],
            'F': ['fish', 'fun', 'leaf'],
            'G': ['go', 'big', 'dog'],
            'H': ['hat', 'house', 'happy'],
            'I': ['ice', 'kite', 'sit'],
            'J': ['jump', 'joy', 'jar'],
            'K': ['kite', 'key', 'book'],
            'L': ['lion', 'ball', 'leaf'],
            'M': ['moon', 'mom', 'swim'],
            'N': ['nose', 'sun', 'run'],
            'O': ['ocean', 'go', 'hot'],
            'P': ['pig', 'cup', 'pop'],
            'Q': ['queen', 'quiet', 'quack'],
            'R': ['red', 'car', 'run'],
            'S': ['sun', 'bus', 'snake'],
            'T': ['tree', 'cat', 'top'],
            'U': ['up', 'cute', 'cup'],
            'V': ['van', 'love', 'very'],
            'W': ['water', 'wow', 'win'],
            'X': ['box', 'fox', 'six'],
            'Y': ['yes', 'my', 'happy'],
            'Z': ['zoo', 'buzz', 'zero']
        }
        
        return examples.get(letter, [])

# Service instance
_phoneme_service = None

def get_phoneme_service() -> PhonemeService:
    """Get phoneme service instance"""
    global _phoneme_service
    if _phoneme_service is None:
        _phoneme_service = PhonemeService()
    return _phoneme_service
