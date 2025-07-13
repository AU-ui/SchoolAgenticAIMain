import re
from typing import Dict, List, Optional
from collections import Counter
import json

class LanguageDetectionService:
    def __init__(self):
        # Load language patterns and dictionaries
        self.language_patterns = self._load_language_patterns()
        self.common_words = self._load_common_words()
        self.character_sets = self._load_character_sets()
        
    def detect_language(self, text: str) -> str:
        """Detect the language of the given text"""
        try:
            if not text or len(text.strip()) < 3:
                return "unknown"
            
            # Clean text
            cleaned_text = self._clean_text(text)
            
            # Multiple detection methods
            scores = {}
            
            # Method 1: Character-based detection
            char_score = self._character_based_detection(cleaned_text)
            scores.update(char_score)
            
            # Method 2: Word-based detection
            word_score = self._word_based_detection(cleaned_text)
            scores.update(word_score)
            
            # Method 3: Pattern-based detection
            pattern_score = self._pattern_based_detection(cleaned_text)
            scores.update(pattern_score)
            
            # Combine scores
            final_scores = self._combine_scores(scores)
            
            # Return the language with highest score
            if final_scores:
                detected_language = max(final_scores.items(), key=lambda x: x[1])
                return detected_language[0] if detected_language[1] > 0.3 else "unknown"
            
            return "unknown"
            
        except Exception as e:
            print(f"Language detection error: {e}")
            return "unknown"
    
    def analyze_language_preferences(self, messages: List[Dict]) -> Dict:
        """Analyze language preferences from message history"""
        try:
            language_counts = Counter()
            language_confidence = {}
            
            for message in messages:
                text = message.get('message', '')
                language = self.detect_language(text)
                language_counts[language] += 1
            
            # Calculate preferences
            total_messages = len(messages)
            preferences = {}
            
            for language, count in language_counts.items():
                if language != "unknown":
                    preferences[language] = {
                        "percentage": round((count / total_messages) * 100, 2),
                        "count": count,
                        "confidence": self._calculate_language_confidence(language, count, total_messages)
                    }
            
            return {
                "primary_language": language_counts.most_common(1)[0][0] if language_counts else "unknown",
                "language_distribution": preferences,
                "total_messages": total_messages,
                "detected_languages": list(language_counts.keys())
            }
            
        except Exception as e:
            print(f"Language preference analysis error: {e}")
            return {}
    
    def _clean_text(self, text: str) -> str:
        """Clean text for language detection"""
        # Remove numbers and special characters, keep letters and spaces
        cleaned = re.sub(r'[^a-zA-Z\s]', '', text.lower())
        return re.sub(r'\s+', ' ', cleaned).strip()
    
    def _character_based_detection(self, text: str) -> Dict[str, float]:
        """Detect language based on character patterns"""
        scores = {}
        
        # Check for specific character sets
        for language, char_set in self.character_sets.items():
            char_count = sum(1 for char in text if char in char_set)
            if len(text) > 0:
                scores[language] = char_count / len(text)
        
        return scores
    
    def _word_based_detection(self, text: str) -> Dict[str, float]:
        """Detect language based on common words"""
        scores = {}
        words = text.split()
        
        for language, word_list in self.common_words.items():
            matches = sum(1 for word in words if word in word_list)
            if len(words) > 0:
                scores[language] = matches / len(words)
        
        return scores
    
    def _pattern_based_detection(self, text: str) -> Dict[str, float]:
        """Detect language based on linguistic patterns"""
        scores = {}
        
        for language, patterns in self.language_patterns.items():
            pattern_matches = 0
            for pattern in patterns:
                if re.search(pattern, text):
                    pattern_matches += 1
            
            if len(patterns) > 0:
                scores[language] = pattern_matches / len(patterns)
        
        return scores
    
    def _combine_scores(self, scores: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Combine scores from different detection methods"""
        final_scores = {}
        
        for language in set().union(*[method_scores.keys() for method_scores in scores.values()]):
            language_scores = []
            for method_scores in scores.values():
                if language in method_scores:
                    language_scores.append(method_scores[language])
            
            if language_scores:
                # Weighted average of all methods
                final_scores[language] = sum(language_scores) / len(language_scores)
        
        return final_scores
    
    def _calculate_language_confidence(self, language: str, count: int, total: int) -> float:
        """Calculate confidence in language detection"""
        if total == 0:
            return 0.0
        
        # Higher confidence with more samples and higher percentage
        percentage = count / total
        sample_confidence = min(1.0, count / 10)  # More samples = higher confidence
        
        return (percentage * 0.7) + (sample_confidence * 0.3)
    
    def _load_language_patterns(self) -> Dict[str, List[str]]:
        """Load language-specific patterns"""
        return {
            "en": [
                r'\bthe\b', r'\band\b', r'\bor\b', r'\bof\b', r'\bto\b',
                r'\bin\b', r'\bis\b', r'\bit\b', r'\byou\b', r'\bthat\b'
            ],
            "es": [
                r'\bel\b', r'\bla\b', r'\bde\b', r'\bque\b', r'\by\b',
                r'\ben\b', r'\bun\b', r'\bes\b', r'\bse\b', r'\bno\b'
            ],
            "fr": [
                r'\ble\b', r'\bla\b', r'\bde\b', r'\bet\b', r'\bun\b',
                r'\bdu\b', r'\bque\b', r'\bqui\b', r'\bne\b', r'\bpas\b'
            ],
            "de": [
                r'\bder\b', r'\bdie\b', r'\bdas\b', r'\bund\b', r'\bin\b',
                r'\bden\b', r'\bvon\b', r'\bmit\b', r'\bsich\b', r'\bnicht\b'
            ]
        }
    
    def _load_common_words(self) -> Dict[str, set]:
        """Load common words for each language"""
        return {
            "en": {
                "the", "and", "or", "of", "to", "in", "is", "it", "you", "that",
                "he", "was", "for", "on", "are", "as", "with", "his", "they",
                "at", "be", "this", "have", "from", "one", "had", "by", "word"
            },
            "es": {
                "el", "la", "de", "que", "y", "en", "un", "es", "se", "no",
                "te", "lo", "le", "da", "su", "por", "son", "con", "para",
                "una", "como", "pero", "sus", "me", "hasta", "hay", "donde"
            },
            "fr": {
                "le", "la", "de", "et", "un", "du", "que", "qui", "ne", "pas",
                "se", "les", "des", "pour", "dans", "sur", "est", "avec",
                "son", "par", "il", "elle", "nous", "vous", "ils", "elles"
            },
            "de": {
                "der", "die", "das", "und", "in", "den", "von", "mit", "sich",
                "nicht", "auf", "ist", "es", "an", "auch", "als", "bei",
                "einen", "um", "sind", "im", "oder", "war", "haben", "eine"
            }
        }
    
    def _load_character_sets(self) -> Dict[str, set]:
        """Load character sets for different languages"""
        return {
            "en": set("abcdefghijklmnopqrstuvwxyz"),
            "es": set("abcdefghijklmnopqrstuvwxyzñáéíóúü"),
            "fr": set("abcdefghijklmnopqrstuvwxyzàâäéèêëïîôöùûüÿç"),
            "de": set("abcdefghijklmnopqrstuvwxyzäöüß")
        } 