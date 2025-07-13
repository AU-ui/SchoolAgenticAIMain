import pandas as pd
import numpy as np
from textblob import TextBlob
import re
from collections import Counter
import json

class SentimentAnalyzer:
    def __init__(self):
        # Load sentiment dictionaries
        self.positive_words = self._load_positive_words()
        self.negative_words = self._load_negative_words()
        self.urgency_indicators = self._load_urgency_indicators()
        self.tone_indicators = self._load_tone_indicators()
        
    def analyze_sentiment(self, text):
        """Analyze sentiment of a text message"""
        try:
            # Clean text
            cleaned_text = self._clean_text(text)
            
            # TextBlob sentiment analysis
            blob = TextBlob(cleaned_text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Custom sentiment analysis
            custom_score = self._custom_sentiment_score(cleaned_text)
            
            # Determine sentiment category
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "sentiment": sentiment,
                "polarity": round(polarity, 3),
                "subjectivity": round(subjectivity, 3),
                "custom_score": round(custom_score, 3),
                "confidence": self._calculate_confidence(polarity, subjectivity, custom_score)
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {"sentiment": "neutral", "polarity": 0, "subjectivity": 0, "custom_score": 0, "confidence": 0}
    
    def analyze_tone(self, text):
        """Analyze the tone of a message"""
        try:
            cleaned_text = self._clean_text(text.lower())
            words = cleaned_text.split()
            
            tone_scores = {
                "formal": self._calculate_formality_score(cleaned_text),
                "urgent": self._calculate_urgency_score(cleaned_text),
                "friendly": self._calculate_friendliness_score(cleaned_text),
                "professional": self._calculate_professionalism_score(cleaned_text),
                "concerned": self._calculate_concern_score(cleaned_text)
            }
            
            # Determine primary tone
            primary_tone = max(tone_scores.items(), key=lambda x: x[1])
            
            return {
                "primary_tone": primary_tone[0],
                "tone_scores": tone_scores,
                "tone_indicators": self._extract_tone_indicators(cleaned_text)
            }
            
        except Exception as e:
            print(f"Error analyzing tone: {e}")
            return {"primary_tone": "neutral", "tone_scores": {}, "tone_indicators": []}
    
    def detect_urgency(self, text):
        """Detect urgency level in a message"""
        try:
            cleaned_text = self._clean_text(text.lower())
            
            # Count urgency indicators
            urgency_count = sum(1 for word in cleaned_text.split() if word in self.urgency_indicators)
            
            # Check for urgency patterns
            urgency_patterns = [
                r'\b(urgent|immediate|asap|emergency)\b',
                r'\b(now|today|tonight)\b',
                r'\b(critical|important|serious)\b',
                r'!{2,}',  # Multiple exclamation marks
                r'\b(call|contact|respond)\s+(immediately|now|today)\b'
            ]
            
            pattern_matches = sum(1 for pattern in urgency_patterns if re.search(pattern, cleaned_text))
            
            # Calculate urgency score
            urgency_score = min(1.0, (urgency_count + pattern_matches) / 5.0)
            
            # Determine urgency level
            if urgency_score > 0.7:
                level = "high"
            elif urgency_score > 0.3:
                level = "medium"
            else:
                level = "low"
            
            return {
                "urgency_level": level,
                "urgency_score": round(urgency_score, 3),
                "urgency_indicators": [word for word in cleaned_text.split() if word in self.urgency_indicators]
            }
            
        except Exception as e:
            print(f"Error detecting urgency: {e}")
            return {"urgency_level": "low", "urgency_score": 0, "urgency_indicators": []}
    
    def classify_emergency_urgency(self, text):
        """Classify emergency messages by urgency level"""
        try:
            cleaned_text = self._clean_text(text.lower())
            
            # Emergency keywords
            emergency_keywords = {
                "critical": ["emergency", "critical", "urgent", "immediate", "serious"],
                "high": ["important", "attention", "concern", "issue", "problem"],
                "medium": ["update", "information", "notice", "reminder"],
                "low": ["general", "routine", "regular", "normal"]
            }
            
            # Count emergency keywords
            keyword_counts = {}
            for level, keywords in emergency_keywords.items():
                count = sum(1 for keyword in keywords if keyword in cleaned_text)
                keyword_counts[level] = count
            
            # Determine emergency level
            if keyword_counts["critical"] > 0:
                emergency_level = "critical"
            elif keyword_counts["high"] > 0:
                emergency_level = "high"
            elif keyword_counts["medium"] > 0:
                emergency_level = "medium"
            else:
                emergency_level = "low"
            
            return {
                "emergency_level": emergency_level,
                "keyword_counts": keyword_counts,
                "requires_immediate_action": emergency_level in ["critical", "high"],
                "response_time_recommendation": self._get_response_time_recommendation(emergency_level)
            }
            
        except Exception as e:
            print(f"Error classifying emergency urgency: {e}")
            return {"emergency_level": "low", "keyword_counts": {}, "requires_immediate_action": False}
    
    def get_confidence_score(self, text):
        """Calculate confidence score for sentiment analysis"""
        try:
            blob = TextBlob(text)
            polarity = abs(blob.sentiment.polarity)
            subjectivity = blob.sentiment.subjectivity
            
            # Higher confidence for more extreme sentiments and lower subjectivity
            confidence = (polarity * 0.6) + ((1 - subjectivity) * 0.4)
            
            return min(1.0, max(0.0, confidence))
            
        except Exception as e:
            print(f"Error calculating confidence score: {e}")
            return 0.5
    
    def _clean_text(self, text):
        """Clean and normalize text"""
        # Remove special characters but keep punctuation
        cleaned = re.sub(r'[^\w\s\.\!\?]', '', text)
        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned
    
    def _custom_sentiment_score(self, text):
        """Calculate custom sentiment score"""
        words = text.lower().split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        
        total_words = len(words)
        if total_words == 0:
            return 0
        
        return (positive_count - negative_count) / total_words
    
    def _calculate_confidence(self, polarity, subjectivity, custom_score):
        """Calculate confidence in sentiment analysis"""
        # Higher confidence for more extreme polarities and lower subjectivity
        polarity_confidence = abs(polarity)
        subjectivity_confidence = 1 - subjectivity
        custom_confidence = abs(custom_score)
        
        # Weighted average
        confidence = (polarity_confidence * 0.4 + subjectivity_confidence * 0.3 + custom_confidence * 0.3)
        
        return min(1.0, max(0.0, confidence))
    
    def _calculate_formality_score(self, text):
        """Calculate formality score"""
        formal_indicators = ["sincerely", "regards", "respectfully", "dear", "yours"]
        informal_indicators = ["hey", "hi", "thanks", "bye", "cool"]
        
        formal_count = sum(1 for word in formal_indicators if word in text)
        informal_count = sum(1 for word in informal_indicators if word in text)
        
        return max(0, (formal_count - informal_count) / len(text.split()))
    
    def _calculate_urgency_score(self, text):
        """Calculate urgency score"""
        urgency_words = ["urgent", "immediate", "asap", "emergency", "critical", "now"]
        return sum(1 for word in urgency_words if word in text) / len(text.split())
    
    def _calculate_friendliness_score(self, text):
        """Calculate friendliness score"""
        friendly_words = ["thank", "appreciate", "great", "good", "wonderful", "excellent"]
        return sum(1 for word in friendly_words if word in text) / len(text.split())
    
    def _calculate_professionalism_score(self, text):
        """Calculate professionalism score"""
        professional_words = ["professional", "formal", "official", "proper", "appropriate"]
        return sum(1 for word in professional_words if word in text) / len(text.split())
    
    def _calculate_concern_score(self, text):
        """Calculate concern score"""
        concern_words = ["concern", "worried", "issue", "problem", "trouble", "difficult"]
        return sum(1 for word in concern_words if word in text) / len(text.split())
    
    def _extract_tone_indicators(self, text):
        """Extract specific tone indicators from text"""
        indicators = []
        
        for tone, words in self.tone_indicators.items():
            found_words = [word for word in words if word in text]
            if found_words:
                indicators.append({
                    "tone": tone,
                    "indicators": found_words
                })
        
        return indicators
    
    def _get_response_time_recommendation(self, emergency_level):
        """Get recommended response time based on emergency level"""
        recommendations = {
            "critical": "immediate (within 30 minutes)",
            "high": "urgent (within 2 hours)",
            "medium": "soon (within 24 hours)",
            "low": "normal (within 48 hours)"
        }
        
        return recommendations.get(emergency_level, "normal (within 48 hours)")
    
    def _load_positive_words(self):
        """Load positive sentiment words"""
        return {
            "good", "great", "excellent", "wonderful", "amazing", "fantastic", "outstanding",
            "perfect", "brilliant", "superb", "terrific", "marvelous", "splendid",
            "thank", "appreciate", "grateful", "pleased", "happy", "satisfied"
        }
    
    def _load_negative_words(self):
        """Load negative sentiment words"""
        return {
            "bad", "terrible", "awful", "horrible", "dreadful", "disappointing",
            "worried", "concerned", "upset", "angry", "frustrated", "annoyed",
            "problem", "issue", "trouble", "difficult", "challenging", "stressful"
        }
    
    def _load_urgency_indicators(self):
        """Load urgency indicator words"""
        return {
            "urgent", "immediate", "asap", "emergency", "critical", "important",
            "now", "today", "tonight", "quickly", "hurry", "rush"
        }
    
    def _load_tone_indicators(self):
        """Load tone indicator words"""
        return {
            "formal": ["sincerely", "regards", "respectfully", "dear", "yours"],
            "friendly": ["hey", "hi", "thanks", "appreciate", "great"],
            "professional": ["professional", "formal", "official", "proper"],
            "concerned": ["concern", "worried", "issue", "problem", "trouble"],
            "urgent": ["urgent", "immediate", "asap", "emergency", "critical"]
        } 