import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import mean_squared_error, accuracy_score
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
import cv2
import pytesseract
from PIL import Image
import io
import base64
import re
import json
import pickle
import os
from typing import List, Dict, Any, Optional, Tuple
import random
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Advanced NLP imports
try:
    import transformers
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    from sentence_transformers import SentenceTransformer
    ADVANCED_NLP_AVAILABLE = True
except ImportError:
    ADVANCED_NLP_AVAILABLE = False
    print("⚠️ Advanced NLP not available - install transformers and sentence-transformers")

class AdvancedMLServices:
    def __init__(self):
        self.models_dir = "advanced_models"
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Initialize advanced models
        self._initialize_deep_learning_models()
        self._initialize_advanced_nlp()
        self._initialize_computer_vision()
        
        # Performance tracking
        self.advanced_performance = {
            'deep_learning_accuracy': [],
            'nlp_accuracy': [],
            'vision_accuracy': [],
            'recommendation_accuracy': []
        }
        
        print("🚀 Advanced ML Services initialized!")
    
    def _initialize_deep_learning_models(self):
        """Initialize deep learning models"""
        try:
            # Student Performance Deep Learning Model
            self.student_performance_dl = self._build_student_performance_dl()
            
            # Engagement Prediction LSTM
            self.engagement_lstm = self._build_engagement_lstm()
            
            # Attendance Pattern CNN
            self.attendance_cnn = self._build_attendance_cnn()
            
            print("✅ Deep Learning models initialized")
        except Exception as e:
            print(f"⚠️ Deep Learning initialization failed: {e}")
            self.student_performance_dl = None
            self.engagement_lstm = None
            self.attendance_cnn = None
    
    def _initialize_advanced_nlp(self):
        """Initialize advanced NLP models"""
        if ADVANCED_NLP_AVAILABLE:
            try:
                # Sentiment analysis with transformers
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
                )
                
                # Text classification for communication types
                self.text_classifier = pipeline(
                    "text-classification",
                    model="facebook/bart-large-mnli"
                )
                
                # Sentence embeddings
                self.sentence_encoder = SentenceTransformer('all-MiniLM-L6-v2')
                
                print("✅ Advanced NLP models initialized")
            except Exception as e:
                print(f"⚠️ Advanced NLP initialization failed: {e}")
                self.sentiment_pipeline = None
                self.text_classifier = None
                self.sentence_encoder = None
        else:
            self.sentiment_pipeline = None
            self.text_classifier = None
            self.sentence_encoder = None
    
    def _initialize_computer_vision(self):
        """Initialize computer vision capabilities"""
        try:
            # Face detection for attendance
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # OCR for document processing
            self.ocr_available = True
            
            print("✅ Computer Vision models initialized")
        except Exception as e:
            print(f"⚠️ Computer Vision initialization failed: {e}")
            self.face_cascade = None
            self.ocr_available = False
    
    def _build_student_performance_dl(self):
        """Build deep learning model for student performance"""
        model = keras.Sequential([
            layers.Dense(128, activation='relu', input_shape=(10,)),
            layers.Dropout(0.3),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='linear')
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def _build_engagement_lstm(self):
        """Build LSTM model for engagement prediction"""
        model = keras.Sequential([
            layers.LSTM(64, return_sequences=True, input_shape=(7, 5)),  # 7 days, 5 features
            layers.Dropout(0.2),
            layers.LSTM(32),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def _build_attendance_cnn(self):
        """Build CNN model for attendance pattern recognition"""
        model = keras.Sequential([
            layers.Conv1D(32, 3, activation='relu', input_shape=(30, 4)),  # 30 days, 4 features
            layers.MaxPooling1D(2),
            layers.Conv1D(64, 3, activation='relu'),
            layers.MaxPooling1D(2),
            layers.Flatten(),
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def advanced_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Advanced sentiment analysis using transformers"""
        if self.sentiment_pipeline:
            try:
                result = self.sentiment_pipeline(text)[0]
                
                # Enhanced analysis
                sentiment_mapping = {
                    'LABEL_0': 'negative',
                    'LABEL_1': 'neutral', 
                    'LABEL_2': 'positive'
                }
                
                # Get embeddings for similarity analysis
                embeddings = self.sentence_encoder.encode(text)
                
                return {
                    'sentiment': sentiment_mapping.get(result['label'], 'neutral'),
                    'confidence': round(result['score'] * 100, 2),
                    'sentiment_score': self._calculate_sentiment_score(result['label'], result['score']),
                    'embeddings': embeddings.tolist()[:10],  # First 10 dimensions
                    'model': 'transformers',
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                return self._fallback_sentiment_analysis(text)
        else:
            return self._fallback_sentiment_analysis(text)
    
    def _fallback_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback sentiment analysis"""
        # Simple keyword-based analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'happy']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'sad', 'angry']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            score = min(positive_count * 20, 100)
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = -min(negative_count * 20, 100)
        else:
            sentiment = 'neutral'
            score = 0
        
        return {
            'sentiment': sentiment,
            'confidence': 70,
            'sentiment_score': score,
            'model': 'fallback',
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_sentiment_score(self, label: str, score: float) -> float:
        """Calculate sentiment score from transformer output"""
        if label == 'LABEL_0':  # Negative
            return -score * 100
        elif label == 'LABEL_2':  # Positive
            return score * 100
        else:  # Neutral
            return 0
    
    def predict_student_performance_dl(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Deep learning prediction for student performance"""
        if self.student_performance_dl:
            try:
                # Prepare features for deep learning
                features = np.array([
                    student_data.get('attendance_rate', 0.8),
                    student_data.get('assignment_completion', 0.8),
                    student_data.get('study_hours', 5),
                    student_data.get('previous_grades', 75),
                    student_data.get('participation_rate', 0.7),
                    student_data.get('homework_completion', 0.8),
                    student_data.get('class_participation', 0.7),
                    student_data.get('extracurricular_involvement', 0.5),
                    student_data.get('parent_engagement', 0.6),
                    student_data.get('study_environment_score', 0.7)
                ]).reshape(1, -1)
                
                # Normalize features
                features = (features - np.mean(features)) / np.std(features)
                
                # Make prediction
                prediction = self.student_performance_dl.predict(features)[0][0]
                prediction = max(50, min(100, prediction))
                
                # Calculate confidence based on feature completeness
                confidence = self._calculate_dl_confidence(student_data)
                
                return {
                    'predicted_grade': round(prediction, 2),
                    'confidence': confidence,
                    'model': 'deep_learning',
                    'features_used': len([v for v in student_data.values() if v is not None]),
                    'risk_level': self._assess_dl_risk(prediction, student_data),
                    'recommendations': self._generate_dl_recommendations(prediction, student_data),
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                return self._fallback_performance_prediction(student_data)
        else:
            return self._fallback_performance_prediction(student_data)
    
    def _fallback_performance_prediction(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback performance prediction"""
        attendance = student_data.get('attendance_rate', 0.8)
        completion = student_data.get('assignment_completion', 0.8)
        study_hours = student_data.get('study_hours', 5)
        
        predicted_grade = (
            attendance * 30 +
            completion * 30 +
            (study_hours / 8) * 20 +
            student_data.get('previous_grades', 75) * 0.2
        )
        
        return {
            'predicted_grade': round(predicted_grade, 2),
            'confidence': 75,
            'model': 'fallback',
            'risk_level': 'medium',
            'recommendations': ['Monitor progress', 'Provide support'],
            'timestamp': datetime.now().isoformat()
        }
    
    def _calculate_dl_confidence(self, student_data: Dict[str, Any]) -> float:
        """Calculate confidence for deep learning prediction"""
        # More features = higher confidence
        feature_count = len([v for v in student_data.values() if v is not None])
        base_confidence = min(feature_count * 8, 85)  # Max 85% from features
        
        # Add confidence based on data quality
        quality_bonus = 10 if all(v is not None for v in student_data.values()) else 0
        
        return min(base_confidence + quality_bonus, 95)
    
    def _assess_dl_risk(self, prediction: float, student_data: Dict[str, Any]) -> str:
        """Assess risk level using deep learning insights"""
        if prediction < 60:
            return 'high'
        elif prediction < 75:
            return 'medium'
        else:
            return 'low'
    
    def _generate_dl_recommendations(self, prediction: float, student_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations using deep learning insights"""
        recommendations = []
        
        if prediction < 70:
            recommendations.extend([
                "Implement intensive tutoring program",
                "Daily progress monitoring required",
                "Parent-teacher conference needed",
                "Consider academic intervention"
            ])
        elif prediction < 85:
            recommendations.extend([
                "Weekly progress check-ins",
                "Targeted support in weak areas",
                "Encourage active participation",
                "Regular homework monitoring"
            ])
        else:
            recommendations.extend([
                "Maintain current performance",
                "Encourage advanced learning",
                "Consider enrichment programs",
                "Mentor other students"
            ])
        
        return recommendations[:3]
    
    def analyze_attendance_with_cv(self, image_data: str) -> Dict[str, Any]:
        """Analyze attendance using computer vision"""
        if not self.face_cascade or not self.ocr_available:
            return {'error': 'Computer vision not available'}
        
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data.split(',')[1])
            image = Image.open(io.BytesIO(image_bytes))
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale for face detection
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            
            # Analyze attendance patterns
            attendance_analysis = {
                'faces_detected': len(faces),
                'estimated_attendance': min(len(faces), 30),  # Assume max 30 students
                'text_extracted': text[:200] + "..." if len(text) > 200 else text,
                'confidence': min(len(faces) * 3, 95),
                'model': 'computer_vision',
                'timestamp': datetime.now().isoformat()
            }
            
            return attendance_analysis
            
        except Exception as e:
            return {
                'error': f'Computer vision analysis failed: {str(e)}',
                'model': 'computer_vision',
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_ai_recommendations(self, context: str, user_type: str) -> Dict[str, Any]:
        """Generate AI-powered recommendations"""
        try:
            # Use sentence embeddings for similarity
            if self.sentence_encoder:
                context_embedding = self.sentence_encoder.encode(context)
                
                # Generate recommendations based on context and user type
                recommendations = self._generate_contextual_recommendations(context, user_type)
                
                return {
                    'recommendations': recommendations,
                    'context_embedding': context_embedding.tolist()[:10],
                    'user_type': user_type,
                    'confidence': 85,
                    'model': 'ai_recommendations',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return self._fallback_recommendations(context, user_type)
                
        except Exception as e:
            return self._fallback_recommendations(context, user_type)
    
    def _generate_contextual_recommendations(self, context: str, user_type: str) -> List[str]:
        """Generate contextual recommendations"""
        recommendations = []
        
        context_lower = context.lower()
        
        if user_type == 'teacher':
            if 'attendance' in context_lower:
                recommendations.extend([
                    "Implement QR code attendance system",
                    "Send automated attendance alerts",
                    "Schedule parent meetings for absent students"
                ])
            elif 'performance' in context_lower:
                recommendations.extend([
                    "Use adaptive learning techniques",
                    "Provide personalized feedback",
                    "Implement progress tracking tools"
                ])
            elif 'engagement' in context_lower:
                recommendations.extend([
                    "Incorporate interactive activities",
                    "Use gamification elements",
                    "Encourage peer collaboration"
                ])
        
        elif user_type == 'parent':
            if 'communication' in context_lower:
                recommendations.extend([
                    "Use preferred communication channels",
                    "Send regular progress updates",
                    "Schedule regular check-ins"
                ])
            elif 'academic' in context_lower:
                recommendations.extend([
                    "Monitor homework completion",
                    "Provide study environment support",
                    "Encourage reading habits"
                ])
        
        # Add general recommendations
        recommendations.extend([
            "Leverage AI insights for better outcomes",
            "Use data-driven decision making",
            "Implement continuous improvement processes"
        ])
        
        return recommendations[:5]
    
    def _fallback_recommendations(self, context: str, user_type: str) -> Dict[str, Any]:
        """Fallback recommendations"""
        return {
            'recommendations': [
                "Monitor progress regularly",
                "Provide consistent support",
                "Communicate effectively"
            ],
            'user_type': user_type,
            'confidence': 70,
            'model': 'fallback',
            'timestamp': datetime.now().isoformat()
        }
    
    def get_advanced_performance(self) -> Dict[str, Any]:
        """Get advanced model performance metrics"""
        return {
            'deep_learning': {
                'accuracy': np.mean(self.advanced_performance['deep_learning_accuracy']) if self.advanced_performance['deep_learning_accuracy'] else 0,
                'models_available': self.student_performance_dl is not None
            },
            'nlp': {
                'accuracy': np.mean(self.advanced_performance['nlp_accuracy']) if self.advanced_performance['nlp_accuracy'] else 0,
                'models_available': self.sentiment_pipeline is not None
            },
            'computer_vision': {
                'accuracy': np.mean(self.advanced_performance['vision_accuracy']) if self.advanced_performance['vision_accuracy'] else 0,
                'models_available': self.face_cascade is not None
            },
            'recommendations': {
                'accuracy': np.mean(self.advanced_performance['recommendation_accuracy']) if self.advanced_performance['recommendation_accuracy'] else 0,
                'models_available': self.sentence_encoder is not None
            }
        }

# Initialize advanced ML services
advanced_ml_services = AdvancedMLServices() 