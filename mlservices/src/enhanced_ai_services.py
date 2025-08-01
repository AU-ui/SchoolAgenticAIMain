import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.neural_network import MLPRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, accuracy_score, classification_report
from sklearn.preprocessing import StandardScaler, LabelEncoder
from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re
import json
import pickle
import os
from typing import List, Dict, Any, Optional, Tuple
import random
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class EnhancedAIServices:
    def __init__(self):
        self.models_dir = "models"
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Initialize models
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        
        # Advanced ML Models
        self.engagement_model = GradientBoostingRegressor(n_estimators=200, learning_rate=0.1, random_state=42)
        self.performance_model = MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42)
        self.attendance_model = RandomForestClassifier(n_estimators=150, random_state=42)
        self.sentiment_model = LogisticRegression(random_state=42)
        
        # Feedback storage
        self.feedback_data = {
            'engagement_feedback': [],
            'performance_feedback': [],
            'attendance_feedback': [],
            'sentiment_feedback': []
        }
        
        # Model performance tracking
        self.model_performance = {
            'engagement_accuracy': [],
            'performance_accuracy': [],
            'attendance_accuracy': [],
            'sentiment_accuracy': []
        }
        
        # Load existing models or train new ones
        self._load_or_train_models()
    
    def _load_or_train_models(self):
        """Load existing models or train new ones with enhanced data"""
        # Try to load existing models
        if self._load_models():
            print("✅ Loaded existing trained models")
        else:
            print("🔄 Training new models with enhanced data...")
            self._train_enhanced_models()
            self._save_models()
    
    def _train_enhanced_models(self):
        """Train models with more realistic and diverse data"""
        np.random.seed(42)
        n_samples = 5000  # Increased sample size
        
        # Enhanced Engagement Data (more realistic patterns)
        engagement_data = self._generate_realistic_engagement_data(n_samples)
        
        # Enhanced Performance Data (academic patterns)
        performance_data = self._generate_realistic_performance_data(n_samples)
        
        # Enhanced Attendance Data (school patterns)
        attendance_data = self._generate_realistic_attendance_data(n_samples)
        
        # Train models
        self._train_engagement_model(engagement_data)
        self._train_performance_model(performance_data)
        self._train_attendance_model(attendance_data)
        
        print("✅ All models trained successfully")
    
    def _generate_realistic_engagement_data(self, n_samples: int) -> Dict[str, Any]:
        """Generate realistic parent engagement data"""
        # Realistic patterns: parents more engaged during school hours, less on weekends
        time_of_day = np.random.normal(14, 4, n_samples)  # Peak around 2 PM
        time_of_day = np.clip(time_of_day, 0, 23)
        
        # Day of week probabilities (weekdays more likely)
        day_probs = [0.1, 0.15, 0.15, 0.15, 0.15, 0.15, 0.15]
        day_probs = [p/sum(day_probs) for p in day_probs]  # Normalize to sum to 1
        day_of_week = np.random.choice([0,1,2,3,4,5,6], n_samples, p=day_probs)  # Weekdays more likely
        
        # Response time: faster during school hours, slower on weekends
        response_time = np.where(day_of_week < 5, 
                                np.random.exponential(4, n_samples),  # Weekdays: faster
                                np.random.exponential(12, n_samples))  # Weekends: slower
        
        # Message length: varies by time and day
        message_length = np.random.normal(150, 80, n_samples)
        message_length = np.clip(message_length, 10, 500)
        
        # Previous engagement affects current engagement
        previous_engagement = np.random.uniform(0.2, 1.0, n_samples)
        
        # Calculate realistic engagement score
        engagement_score = (
            0.3 * (1 / (1 + response_time/24)) +  # Response time factor
            0.2 * (message_length / 500) +        # Message length factor
            0.2 * (1 - abs(time_of_day - 14) / 24) +  # Time of day factor
            0.2 * (1 - day_of_week / 7) +         # Day of week factor
            0.1 * previous_engagement             # Previous engagement factor
        ) + np.random.normal(0, 0.1, n_samples)  # Add noise
        
        engagement_score = np.clip(engagement_score, 0.1, 1.0)
        
        return {
            'response_time': response_time,
            'message_length': message_length,
            'time_of_day': time_of_day,
            'day_of_week': day_of_week,
            'previous_engagement': previous_engagement,
            'engagement_score': engagement_score
        }
    
    def _generate_realistic_performance_data(self, n_samples: int) -> Dict[str, Any]:
        """Generate realistic student performance data"""
        # Attendance rate: most students have good attendance
        attendance_rate = np.random.beta(8, 2, n_samples)  # Skewed towards high attendance
        
        # Assignment completion: correlates with attendance
        assignment_completion = attendance_rate * 0.8 + np.random.normal(0, 0.1, n_samples)
        assignment_completion = np.clip(assignment_completion, 0.3, 1.0)
        
        # Study hours: varies by student
        study_hours = np.random.gamma(3, 1.5, n_samples)  # Most study 2-6 hours
        study_hours = np.clip(study_hours, 0.5, 12)
        
        # Previous grades: affects current performance
        previous_grades = np.random.normal(75, 15, n_samples)
        previous_grades = np.clip(previous_grades, 50, 100)
        
        # Participation rate: correlates with attendance and previous grades
        participation_rate = (attendance_rate * 0.4 + 
                            (previous_grades - 50) / 50 * 0.4 + 
                            np.random.normal(0, 0.1, n_samples))
        participation_rate = np.clip(participation_rate, 0.1, 1.0)
        
        # Calculate final grade based on all factors
        final_grade = (
            0.25 * attendance_rate * 100 +
            0.25 * assignment_completion * 100 +
            0.20 * (study_hours / 8) * 100 +
            0.20 * previous_grades +
            0.10 * participation_rate * 100
        ) + np.random.normal(0, 5, n_samples)
        
        final_grade = np.clip(final_grade, 50, 100)
        
        return {
            'attendance_rate': attendance_rate,
            'assignment_completion': assignment_completion,
            'study_hours': study_hours,
            'previous_grades': previous_grades,
            'participation_rate': participation_rate,
            'final_grade': final_grade
        }
    
    def _generate_realistic_attendance_data(self, n_samples: int) -> Dict[str, Any]:
        """Generate realistic attendance patterns"""
        # Student characteristics
        student_id = np.random.randint(1, 1000, n_samples)
        
        # Day of week: Monday and Friday have lower attendance
        # Normalize probabilities to sum to 1
        day_probs = [0.85, 0.92, 0.94, 0.93, 0.91, 0.88, 0.95]
        day_probs = [p/sum(day_probs) for p in day_probs]  # Normalize to sum to 1
        day_of_week = np.random.choice([0,1,2,3,4,5,6], n_samples, p=day_probs)
        
        # Time of day: morning classes have better attendance
        time_of_day = np.random.normal(10, 3, n_samples)
        time_of_day = np.clip(time_of_day, 7, 17)
        
        # Weather effect (simulated)
        weather_good = np.random.choice([0, 1], n_samples, p=[0.7, 0.3])
        
        # Calculate attendance probability
        base_attendance = 0.9
        day_factor = np.where(day_of_week == 0, -0.05,  # Monday
                             np.where(day_of_week == 4, -0.02,  # Friday
                                     0.02))  # Other days
        time_factor = 1 - abs(time_of_day - 10) / 10 * 0.1  # Best at 10 AM
        weather_factor = weather_good * 0.05
        
        attendance_prob = base_attendance + day_factor + time_factor + weather_factor
        attendance_prob = np.clip(attendance_prob, 0.7, 0.98)
        
        # Generate attendance status
        attendance_status = np.random.binomial(1, attendance_prob, n_samples)
        
        return {
            'student_id': student_id,
            'day_of_week': day_of_week,
            'time_of_day': time_of_day,
            'weather_good': weather_good,
            'attendance_status': attendance_status
        }
    
    def _train_engagement_model(self, data: Dict[str, Any]):
        """Train engagement prediction model"""
        X = pd.DataFrame({
            'response_time': data['response_time'],
            'message_length': data['message_length'],
            'time_of_day': data['time_of_day'],
            'day_of_week': data['day_of_week'],
            'previous_engagement': data['previous_engagement']
        })
        y = data['engagement_score']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.engagement_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.engagement_model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        self.model_performance['engagement_accuracy'].append(1 - mse)
        
        print(f"📊 Engagement Model - MSE: {mse:.4f}")
    
    def _train_performance_model(self, data: Dict[str, Any]):
        """Train performance prediction model"""
        X = pd.DataFrame({
            'attendance_rate': data['attendance_rate'],
            'assignment_completion': data['assignment_completion'],
            'study_hours': data['study_hours'],
            'previous_grades': data['previous_grades'],
            'participation_rate': data['participation_rate']
        })
        y = data['final_grade']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.performance_model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = self.performance_model.predict(X_test_scaled)
        mse = mean_squared_error(y_test, y_pred)
        self.model_performance['performance_accuracy'].append(1 - mse)
        
        print(f"📈 Performance Model - MSE: {mse:.4f}")
    
    def _train_attendance_model(self, data: Dict[str, Any]):
        """Train attendance prediction model"""
        X = pd.DataFrame({
            'day_of_week': data['day_of_week'],
            'time_of_day': data['time_of_day'],
            'weather_good': data['weather_good']
        })
        y = data['attendance_status']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train model
        self.attendance_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = self.attendance_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        self.model_performance['attendance_accuracy'].append(accuracy)
        
        print(f"📋 Attendance Model - Accuracy: {accuracy:.4f}")
    
    def add_feedback(self, model_type: str, prediction: float, actual: float, features: Dict[str, Any]):
        """Add feedback to improve models"""
        feedback = {
            'timestamp': datetime.now().isoformat(),
            'prediction': prediction,
            'actual': actual,
            'features': features,
            'error': abs(prediction - actual)
        }
        
        self.feedback_data[f'{model_type}_feedback'].append(feedback)
        
        # Retrain model if we have enough new feedback
        if len(self.feedback_data[f'{model_type}_feedback']) >= 50:
            self._retrain_model_with_feedback(model_type)
    
    def _retrain_model_with_feedback(self, model_type: str):
        """Retrain model using feedback data"""
        feedback = self.feedback_data[f'{model_type}_feedback']
        
        if len(feedback) < 50:
            return
        
        # Prepare feedback data
        X_feedback = []
        y_feedback = []
        
        for item in feedback:
            features = item['features']
            if model_type == 'engagement':
                X_feedback.append([
                    features.get('response_time', 24),
                    features.get('message_length', 100),
                    features.get('time_of_day', 12),
                    features.get('day_of_week', 3),
                    features.get('previous_engagement', 0.5)
                ])
                y_feedback.append(item['actual'])
        
        if X_feedback:
            X_feedback = np.array(X_feedback)
            y_feedback = np.array(y_feedback)
            
            # Retrain model with feedback
            if model_type == 'engagement':
                X_scaled = self.scaler.transform(X_feedback)
                self.engagement_model.fit(X_scaled, y_feedback)
            
            # Clear feedback data after retraining
            self.feedback_data[f'{model_type}_feedback'] = []
            
            print(f"🔄 Retrained {model_type} model with feedback data")
    
    def predict_engagement_with_feedback(self, parent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict engagement with feedback learning"""
        try:
            features = [
                parent_data.get('response_time', 24),
                parent_data.get('message_length', 100),
                parent_data.get('time_of_day', 12),
                parent_data.get('day_of_week', 3),
                parent_data.get('previous_engagement', 0.5)
            ]
            
            # Make prediction
            X_scaled = self.scaler.transform([features])
            engagement_score = self.engagement_model.predict(X_scaled)[0]
            engagement_score = max(0.1, min(1.0, engagement_score))
            
            # Generate recommendations
            recommendations = self._generate_engagement_recommendations(engagement_score, parent_data)
            
            return {
                'predicted_engagement': round(engagement_score * 100, 2),
                'confidence': round(self._calculate_confidence(features) * 100, 2),
                'optimal_send_time': self._calculate_optimal_time(parent_data),
                'recommended_channel': self._get_recommended_channel(parent_data),
                'recommendations': recommendations,
                'model_version': len(self.model_performance['engagement_accuracy']),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'predicted_engagement': 70,
                'confidence': 60,
                'error': str(e)
            }
    
    def predict_student_performance_with_feedback(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict student performance with feedback learning"""
        try:
            features = [
                student_data.get('attendance_rate', 0.8),
                student_data.get('assignment_completion', 0.8),
                student_data.get('study_hours', 5),
                student_data.get('previous_grades', 75),
                student_data.get('participation_rate', 0.7)
            ]
            
            # Make prediction
            X_scaled = self.scaler.transform([features])
            predicted_grade = self.performance_model.predict(X_scaled)[0]
            predicted_grade = max(50, min(100, predicted_grade))
            
            # Determine risk level
            risk_level = self._assess_risk_level(student_data)
            
            return {
                'predicted_grade': round(predicted_grade, 2),
                'confidence': round(self._calculate_confidence(features) * 100, 2),
                'risk_level': risk_level,
                'risk_factors': self._identify_risk_factors(student_data),
                'recommendations': self._generate_performance_recommendations(predicted_grade, risk_level),
                'model_version': len(self.model_performance['performance_accuracy']),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'predicted_grade': 75,
                'confidence': 60,
                'error': str(e)
            }
    
    def _calculate_confidence(self, features: List[float]) -> float:
        """Calculate prediction confidence based on feature quality"""
        # Simple confidence calculation based on feature completeness
        non_zero_features = sum(1 for f in features if f > 0)
        confidence = non_zero_features / len(features)
        return min(confidence + 0.3, 0.95)  # Base confidence of 30%
    
    def get_model_performance(self) -> Dict[str, Any]:
        """Get current model performance metrics"""
        return {
            'engagement_model': {
                'accuracy': np.mean(self.model_performance['engagement_accuracy']) if self.model_performance['engagement_accuracy'] else 0,
                'version': len(self.model_performance['engagement_accuracy']),
                'last_updated': datetime.now().isoformat()
            },
            'performance_model': {
                'accuracy': np.mean(self.model_performance['performance_accuracy']) if self.model_performance['performance_accuracy'] else 0,
                'version': len(self.model_performance['performance_accuracy']),
                'last_updated': datetime.now().isoformat()
            },
            'attendance_model': {
                'accuracy': np.mean(self.model_performance['attendance_accuracy']) if self.model_performance['attendance_accuracy'] else 0,
                'version': len(self.model_performance['attendance_accuracy']),
                'last_updated': datetime.now().isoformat()
            }
        }
    
    def _save_models(self):
        """Save trained models"""
        models = {
            'engagement_model': self.engagement_model,
            'performance_model': self.performance_model,
            'attendance_model': self.attendance_model,
            'scaler': self.scaler,
            'model_performance': self.model_performance
        }
        
        for name, model in models.items():
            with open(os.path.join(self.models_dir, f'{name}.pkl'), 'wb') as f:
                pickle.dump(model, f)
    
    def _load_models(self):
        """Load trained models"""
        models = ['engagement_model', 'performance_model', 'attendance_model', 'scaler']
        
        for name in models:
            model_path = os.path.join(self.models_dir, f'{name}.pkl')
            if not os.path.exists(model_path):
                print(f"⚠️  Model {name} not found, will train new model")
                return False  # Indicate that models need to be trained
            
            try:
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                    setattr(self, name, model)
            except Exception as e:
                print(f"⚠️  Error loading model {name}: {e}")
                return False
        
        # Load performance data
        perf_path = os.path.join(self.models_dir, 'model_performance.pkl')
        if os.path.exists(perf_path):
            try:
                with open(perf_path, 'rb') as f:
                    self.model_performance = pickle.load(f)
            except Exception as e:
                print(f"⚠️  Error loading performance data: {e}")
                self.model_performance = {'engagement_accuracy': [], 'performance_accuracy': [], 'attendance_accuracy': []}
        else:
            self.model_performance = {'engagement_accuracy': [], 'performance_accuracy': [], 'attendance_accuracy': []}
        
        return True  # Indicate successful loading
    
    # Include all the existing methods from the original class
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Enhanced sentiment analysis with feedback learning"""
        try:
            # Clean text
            text = re.sub(r'[^\w\s]', '', text.lower())
            
            # Get VADER sentiment scores
            scores = self.sentiment_analyzer.polarity_scores(text)
            
            # Get TextBlob sentiment for additional analysis
            blob = TextBlob(text)
            
            # Determine sentiment category
            if scores['compound'] >= 0.05:
                sentiment = 'positive'
            elif scores['compound'] <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            # Calculate confidence
            confidence = abs(scores['compound'])
            
            # Detect urgency based on keywords
            urgency_keywords = ['urgent', 'emergency', 'immediate', 'asap', 'critical', 'important']
            urgency_level = sum(1 for word in urgency_keywords if word in text.lower())
            
            return {
                'sentiment': sentiment,
                'sentiment_score': round(scores['compound'] * 100, 2),
                'confidence': round(confidence * 100, 2),
                'urgency_level': min(urgency_level + 1, 5),
                'polarity': round(blob.sentiment.polarity, 3),
                'subjectivity': round(blob.sentiment.subjectivity, 3),
                'details': {
                    'positive': round(scores['pos'], 3),
                    'negative': round(scores['neg'], 3),
                    'neutral': round(scores['neu'], 3)
                },
                'model_version': 'v2.0',
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'sentiment': 'neutral',
                'sentiment_score': 0,
                'confidence': 0,
                'urgency_level': 1,
                'error': str(e)
            }
    
    # Include all other methods from the original class...
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Language detection using TextBlob"""
        try:
            blob = TextBlob(text)
            detected_lang = blob.detect_language()
            
            # Language confidence mapping
            lang_confidence = {
                'en': 0.95, 'es': 0.90, 'fr': 0.88, 'de': 0.85,
                'it': 0.82, 'pt': 0.80, 'ru': 0.75, 'ja': 0.70,
                'ko': 0.68, 'zh': 0.65
            }
            
            confidence = lang_confidence.get(detected_lang, 0.60)
            
            return {
                'language': detected_lang,
                'confidence': round(confidence * 100, 2),
                'language_name': self._get_language_name(detected_lang)
            }
        except Exception as e:
            return {
                'language': 'en',
                'confidence': 0,
                'error': str(e)
            }
    
    def _get_language_name(self, lang_code: str) -> str:
        """Get full language name from code"""
        lang_names = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
            'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese',
            'ko': 'Korean', 'zh': 'Chinese'
        }
        return lang_names.get(lang_code, 'Unknown')
    
    def _generate_engagement_recommendations(self, engagement_score: float, parent_data: Dict[str, Any]) -> List[str]:
        """Generate engagement recommendations"""
        recommendations = []
        
        if engagement_score < 0.5:
            recommendations.extend([
                "Send shorter, more frequent messages",
                "Use more visual content (images, videos)",
                "Schedule calls during preferred hours",
                "Provide immediate value in communications"
            ])
        elif engagement_score < 0.7:
            recommendations.extend([
                "Maintain consistent communication schedule",
                "Personalize messages based on preferences",
                "Include progress updates and achievements",
                "Ask for feedback and preferences"
            ])
        else:
            recommendations.extend([
                "Continue current communication strategy",
                "Consider advanced engagement features",
                "Explore additional communication channels"
            ])
        
        return recommendations[:3]
    
    def _generate_performance_recommendations(self, predicted_grade: float, risk_level: str) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        if risk_level == 'high':
            recommendations.extend([
                "Schedule immediate intervention meeting",
                "Provide additional academic support",
                "Implement daily progress monitoring",
                "Consider tutoring or mentoring program"
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                "Increase monitoring frequency",
                "Provide targeted support in weak areas",
                "Set up regular check-ins",
                "Encourage more active participation"
            ])
        else:
            recommendations.extend([
                "Maintain current support level",
                "Encourage advanced learning opportunities",
                "Provide positive reinforcement"
            ])
        
        return recommendations[:3]
    
    def _calculate_optimal_time(self, parent_data: Dict[str, Any]) -> str:
        """Calculate optimal send time"""
        preferred_time = parent_data.get('preferred_time', '18:00')
        return preferred_time
    
    def _get_recommended_channel(self, parent_data: Dict[str, Any]) -> str:
        """Get recommended communication channel"""
        return parent_data.get('preferred_channel', 'email')
    
    def _assess_risk_level(self, student_data: Dict[str, Any]) -> str:
        """Assess student risk level"""
        attendance = student_data.get('attendance_rate', 0.8)
        completion = student_data.get('assignment_completion', 0.8)
        
        if attendance < 0.7 or completion < 0.7:
            return 'high'
        elif attendance < 0.8 or completion < 0.8:
            return 'medium'
        else:
            return 'low'
    
    def _identify_risk_factors(self, student_data: Dict[str, Any]) -> List[str]:
        """Identify risk factors"""
        risk_factors = []
        
        if student_data.get('attendance_rate', 1) < 0.8:
            risk_factors.append('low_attendance')
        
        if student_data.get('assignment_completion', 1) < 0.8:
            risk_factors.append('late_assignments')
        
        if student_data.get('participation_rate', 1) < 0.6:
            risk_factors.append('low_participation')
        
        return risk_factors if risk_factors else ['none']

# Initialize the enhanced AI services
enhanced_ai_services = EnhancedAIServices() 