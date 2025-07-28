from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from ..services.nlp_services import NLPServices
from ..services.time_series_analysis import TimeSeriesAnalysis
from ..services.advanced_language_processing import AdvancedLanguageProcessing
from ..services.feedback_learning import FeedbackLearningService

router = APIRouter(prefix="/ml/enhanced", tags=["Enhanced ML Services"])

# Initialize services
nlp_services = NLPServices()
time_series = TimeSeriesAnalysis()
language_processing = AdvancedLanguageProcessing()
feedback_service = FeedbackLearningService()

# Enhanced ML API endpoints for Pain Points #1 and #5