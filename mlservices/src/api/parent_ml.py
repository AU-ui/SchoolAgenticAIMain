from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from ..models.parent_analytics import ParentAnalytics
from ..models.sentiment_analyzer import SentimentAnalyzer
from ..models.engagement_predictor import EngagementPredictor
from ..services.translation_service import TranslationService
from ..services.language_detection import LanguageDetectionService

router = APIRouter(prefix="/ml/parent", tags=["Parent ML Services"])

# Initialize ML services
parent_analytics = ParentAnalytics()
sentiment_analyzer = SentimentAnalyzer()
engagement_predictor = EngagementPredictor()
translation_service = TranslationService()
language_detector = LanguageDetectionService()

class CommunicationData(BaseModel):
    message_id: int
    sender_id: int
    recipient_id: int
    message: str
    timestamp: str
    message_type: str  # 'email', 'sms', 'notification'
    language: Optional[str] = None

class ParentEngagementData(BaseModel):
    parent_id: int
    response_time: float  # hours
    response_rate: float  # percentage
    preferred_channel: str
    preferred_time: str
    total_messages: int
    read_rate: float

class SentimentRequest(BaseModel):
    messages: List[CommunicationData]
    analyze_tone: bool = True
    detect_urgency: bool = True

class TranslationRequest(BaseModel):
    text: str
    source_language: Optional[str] = None
    target_language: str
    context: Optional[str] = None

class EngagementPredictionRequest(BaseModel):
    parent_data: ParentEngagementData
    message_content: str
    message_type: str
    send_time: str

@router.post("/sentiment/analyze")
async def analyze_communication_sentiment(request: SentimentRequest):
    """Analyze sentiment and tone of parent-teacher communications"""
    try:
        results = []
        
        for message in request.messages:
            analysis = {
                'message_id': message.message_id,
                'sentiment': sentiment_analyzer.analyze_sentiment(message.message),
                'tone': sentiment_analyzer.analyze_tone(message.message) if request.analyze_tone else None,
                'urgency_level': sentiment_analyzer.detect_urgency(message.message) if request.detect_urgency else None,
                'language': language_detector.detect_language(message.message),
                'confidence': sentiment_analyzer.get_confidence_score(message.message)
            }
            results.append(analysis)
        
        return {
            "success": True,
            "data": results,
            "message": "Sentiment analysis completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@router.post("/translation/translate")
async def translate_message(request: TranslationRequest):
    """Translate messages between different languages"""
    try:
        # Detect source language if not provided
        if not request.source_language:
            request.source_language = language_detector.detect_language(request.text)
        
        translated_text = translation_service.translate(
            request.text,
            request.source_language,
            request.target_language,
            request.context
        )
        
        return {
            "success": True,
            "data": {
                "original_text": request.text,
                "translated_text": translated_text,
                "source_language": request.source_language,
                "target_language": request.target_language,
                "confidence": translation_service.get_confidence_score()
            },
            "message": "Translation completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@router.post("/engagement/predict")
async def predict_engagement(request: EngagementPredictionRequest):
    """Predict parent engagement likelihood for a message"""
    try:
        prediction = engagement_predictor.predict_engagement(
            request.parent_data.dict(),
            request.message_content,
            request.message_type,
            request.send_time
        )
        
        return {
            "success": True,
            "data": prediction,
            "message": "Engagement prediction completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Engagement prediction failed: {str(e)}")

@router.post("/communication/optimize")
async def optimize_communication_strategy(parent_data: ParentEngagementData):
    """Optimize communication strategy for a parent"""
    try:
        strategy = parent_analytics.optimize_communication_strategy(parent_data.dict())
        
        return {
            "success": True,
            "data": strategy,
            "message": "Communication strategy optimized"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Strategy optimization failed: {str(e)}")

@router.get("/insights/{parent_id}")
async def get_parent_insights(parent_id: int):
    """Get personalized insights for parent communication"""
    try:
        insights = parent_analytics.generate_parent_insights(parent_id)
        
        return {
            "success": True,
            "data": insights,
            "message": "Parent insights generated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate insights: {str(e)}")

@router.post("/notifications/smart-schedule")
async def schedule_smart_notifications(parent_data: ParentEngagementData):
    """Schedule notifications at optimal times for maximum engagement"""
    try:
        schedule = parent_analytics.schedule_smart_notifications(parent_data.dict())
        
        return {
            "success": True,
            "data": schedule,
            "message": "Smart notification schedule created"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schedule creation failed: {str(e)}")

@router.post("/language/preferences")
async def analyze_language_preferences(messages: List[CommunicationData]):
    """Analyze parent language preferences and patterns"""
    try:
        preferences = language_detector.analyze_language_preferences(messages)
        
        return {
            "success": True,
            "data": preferences,
            "message": "Language preferences analyzed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Language analysis failed: {str(e)}")

@router.post("/emergency/classify")
async def classify_emergency_urgency(message: CommunicationData):
    """Classify emergency messages by urgency level"""
    try:
        classification = sentiment_analyzer.classify_emergency_urgency(message.message)
        
        return {
            "success": True,
            "data": classification,
            "message": "Emergency classification completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Emergency classification failed: {str(e)}") 