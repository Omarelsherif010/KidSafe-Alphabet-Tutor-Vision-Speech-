"""
Vision Service for KidSafe Alphabet Tutor
Letter recognition and object detection using computer vision
"""
import logging
import cv2
import numpy as np
from ..config import get_settings
from typing import Dict, List, Optional, Tuple
from PIL import Image, ImageEnhance, ImageFilter
import io
import logging
import base64
import openai

logger = logging.getLogger(__name__)

class VisionService:
    """Enhanced service for computer vision tasks with letter recognition"""
    
    def __init__(self):
        self.settings = get_settings()
        self.client = openai.OpenAI(api_key=self.settings.openai_api_key)
        
        # Letter recognition confidence thresholds
        self.confidence_thresholds = {
            'high': 0.85,
            'medium': 0.65,
            'low': 0.45
        }
    
    def detect_letter_from_image(self, image_data: str) -> Dict[str, any]:
        """
        Enhanced letter detection with preprocessing and multiple methods
        
        Args:
            image_data: Base64 encoded image string
            
        Returns:
            Dict with comprehensive letter detection results
        """
        try:
            # Validate image data
            if not self.validate_image(image_data):
                return self._create_error_result("Invalid image data format")
            
            # Preprocess image for better recognition
            processed_image = self._preprocess_image(image_data)
            
            # Try multiple detection methods
            results = []
            
            # Method 1: OpenAI Vision API
            openai_result = self._detect_with_openai(processed_image)
            if openai_result['success']:
                results.append(openai_result)
            
            # Method 2: Fallback pattern matching (for offline capability)
            pattern_result = self._detect_with_patterns(processed_image)
            if pattern_result['success']:
                results.append(pattern_result)
            
            # Combine results and return best match
            return self._combine_detection_results(results)
                
        except Exception as e:
            logger.error(f"Vision detection failed: {e}")
            return self._create_error_result(f"Detection failed: {str(e)}")
    
    def _preprocess_image(self, image_data: str) -> str:
        """Preprocess image for better letter recognition"""
        try:
            # Extract base64 data
            header, data = image_data.split(',', 1)
            image_bytes = base64.b64decode(data)
            
            # Open image with PIL
            image = Image.open(io.BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance contrast and sharpness
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.5)
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.2)
            
            # Apply slight blur to reduce noise
            image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
            
            # Resize if too large (max 800px on longest side)
            max_size = 800
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Convert back to base64
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            processed_data = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/jpeg;base64,{processed_data}"
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image_data  # Return original if preprocessing fails
    
    def _detect_with_openai(self, image_data: str) -> Dict[str, any]:
        """Detect letter using OpenAI Vision API"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": """Look at this image and identify any single uppercase letter (A-Z) that you can see clearly. 
                                
Rules:
- Only identify ONE letter, the most prominent/clear one
- Must be a standard uppercase letter A-Z
- Ignore handwritten or stylized text
- Respond with ONLY the letter (e.g., 'A') or 'NONE' if no clear letter
- Be conservative - only identify letters you're very confident about"""
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_data,
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=5,
                temperature=0.1
            )
            
            detected_text = response.choices[0].message.content.strip().upper()
            
            # Validate detected letter
            if detected_text in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' and len(detected_text) == 1:
                return {
                    "success": True,
                    "letter": detected_text,
                    "confidence": self.confidence_thresholds['high'],
                    "method": "openai_vision",
                    "details": "Detected using OpenAI Vision API"
                }
            else:
                return {
                    "success": False,
                    "error": "No clear letter detected by OpenAI",
                    "method": "openai_vision"
                }
                
        except Exception as e:
            logger.error(f"OpenAI vision detection failed: {e}")
            return {
                "success": False,
                "error": f"OpenAI detection failed: {str(e)}",
                "method": "openai_vision"
            }
    
    def _detect_with_patterns(self, image_data: str) -> Dict[str, any]:
        """Fallback pattern-based letter detection"""
        try:
            # This is a simplified fallback method
            # In a production system, this could use OCR libraries like Tesseract
            
            # For now, return a basic pattern match result
            # This could be enhanced with actual computer vision algorithms
            
            return {
                "success": False,
                "error": "Pattern detection not implemented",
                "method": "pattern_matching"
            }
            
        except Exception as e:
            logger.error(f"Pattern detection failed: {e}")
            return {
                "success": False,
                "error": f"Pattern detection failed: {str(e)}",
                "method": "pattern_matching"
            }
    
    def _combine_detection_results(self, results: List[Dict]) -> Dict[str, any]:
        """Combine multiple detection results and return the best one"""
        if not results:
            return self._create_error_result("No detection methods succeeded")
        
        # Sort by confidence score
        successful_results = [r for r in results if r.get('success', False)]
        
        if not successful_results:
            return self._create_error_result("No letters detected by any method")
        
        # Return highest confidence result
        best_result = max(successful_results, key=lambda x: x.get('confidence', 0))
        
        # Add combined method info
        methods_used = [r.get('method', 'unknown') for r in results]
        best_result['methods_attempted'] = methods_used
        
        return best_result
    
    def _create_error_result(self, error_message: str) -> Dict[str, any]:
        """Create standardized error result"""
        return {
            "success": False,
            "error": error_message,
            "letter": None,
            "confidence": 0.0,
            "method": "none"
        }
    
    def validate_image(self, image_data: str) -> bool:
        """Enhanced image validation"""
        try:
            if not image_data or not image_data.startswith('data:image'):
                return False
            
            # Extract base64 data
            header, data = image_data.split(',', 1)
            image_bytes = base64.b64decode(data)
            
            # Check image size (limit to 10MB)
            if len(image_bytes) > 10 * 1024 * 1024:
                logger.warning("Image too large")
                return False
            
            # Validate it's a valid image
            image = Image.open(io.BytesIO(image_bytes))
            
            # Check minimum dimensions
            if image.size[0] < 50 or image.size[1] < 50:
                logger.warning("Image too small")
                return False
            
            # Check maximum dimensions
            if image.size[0] > 4000 or image.size[1] > 4000:
                logger.warning("Image dimensions too large")
                return False
            
            # Verify image integrity
            image.verify()
            
            return True
            
        except Exception as e:
            logger.error(f"Image validation failed: {e}")
            return False
    
    def get_detection_tips(self) -> List[str]:
        """Get tips for better letter detection"""
        return [
            "📝 Use printed letters (not handwritten)",
            "💡 Ensure good lighting on the letter",
            "📏 Hold the letter close enough to fill the frame",
            "🎯 Keep the camera steady when capturing",
            "🔤 Use high contrast (dark letter on light background)",
            "📱 Clean your camera lens for clearer images"
        ]
    
# Service instance
_vision_service = None

def get_vision_service() -> VisionService:
    """Get vision service instance"""
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService()
    return _vision_service
