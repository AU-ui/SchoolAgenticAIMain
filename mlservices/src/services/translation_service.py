import requests
import json
from typing import Optional, Dict, Any
import hashlib
import time

class TranslationService:
    def __init__(self):
        # Initialize translation service
        self.api_key = self._get_api_key()
        self.base_url = "https://translation.googleapis.com/language/translate/v2"
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
        
    def translate(self, text: str, source_language: str, target_language: str, context: Optional[str] = None) -> str:
        """Translate text from source language to target language"""
        try:
            # Check cache first
            cache_key = self._generate_cache_key(text, source_language, target_language)
            if cache_key in self.cache:
                cached_result = self.cache[cache_key]
                if time.time() - cached_result['timestamp'] < self.cache_ttl:
                    return cached_result['translation']
            
            # Prepare request
            params = {
                'q': text,
                'source': source_language,
                'target': target_language,
                'key': self.api_key
            }
            
            if context:
                params['context'] = context
            
            # Make API request
            response = requests.post(self.base_url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                translation = result['data']['translations'][0]['translatedText']
                
                # Cache result
                self.cache[cache_key] = {
                    'translation': translation,
                    'timestamp': time.time()
                }
                
                return translation
            else:
                # Fallback to simple translation
                return self._fallback_translate(text, source_language, target_language)
                
        except Exception as e:
            print(f"Translation error: {e}")
            return self._fallback_translate(text, source_language, target_language)
    
    def translate_batch(self, texts: list, source_language: str, target_language: str) -> list:
        """Translate multiple texts at once"""
        try:
            translations = []
            for text in texts:
                translation = self.translate(text, source_language, target_language)
                translations.append(translation)
            return translations
        except Exception as e:
            print(f"Batch translation error: {e}")
            return texts  # Return original texts if translation fails
    
    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return [
            {"code": "en", "name": "English"},
            {"code": "es", "name": "Spanish"},
            {"code": "fr", "name": "French"},
            {"code": "de", "name": "German"},
            {"code": "it", "name": "Italian"},
            {"code": "pt", "name": "Portuguese"},
            {"code": "ru", "name": "Russian"},
            {"code": "zh", "name": "Chinese"},
            {"code": "ja", "name": "Japanese"},
            {"code": "ko", "name": "Korean"},
            {"code": "ar", "name": "Arabic"},
            {"code": "hi", "name": "Hindi"},
            {"code": "bn", "name": "Bengali"},
            {"code": "ur", "name": "Urdu"},
            {"code": "tr", "name": "Turkish"}
        ]
    
    def get_confidence_score(self) -> float:
        """Get confidence score for the last translation"""
        # In real implementation, this would return the confidence from the API
        return 0.85  # Mock confidence score
    
    def _get_api_key(self) -> str:
        """Get API key from environment or config"""
        import os
        return os.getenv('GOOGLE_TRANSLATE_API_KEY', 'your-api-key-here')
    
    def _generate_cache_key(self, text: str, source_lang: str, target_lang: str) -> str:
        """Generate cache key for translation"""
        content = f"{text}:{source_lang}:{target_lang}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _fallback_translate(self, text: str, source_language: str, target_language: str) -> str:
        """Fallback translation using simple dictionary"""
        # Simple fallback translations for common phrases
        fallback_dict = {
            "en-es": {
                "hello": "hola",
                "goodbye": "adiós",
                "thank you": "gracias",
                "please": "por favor",
                "emergency": "emergencia",
                "important": "importante",
                "urgent": "urgente"
            },
            "en-fr": {
                "hello": "bonjour",
                "goodbye": "au revoir",
                "thank you": "merci",
                "please": "s'il vous plaît",
                "emergency": "urgence",
                "important": "important",
                "urgent": "urgent"
            }
        }
        
        key = f"{source_language}-{target_language}"
        if key in fallback_dict:
            for english, translation in fallback_dict[key].items():
                text = text.replace(english.lower(), translation)
        
        return text 