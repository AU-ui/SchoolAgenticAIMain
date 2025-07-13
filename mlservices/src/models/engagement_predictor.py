import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from datetime import datetime, timedelta
import json

class EngagementPredictor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.response_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.response_time_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.channel_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.label_encoder = LabelEncoder()
        
        # Load pre-trained models (in real implementation, these would be trained on historical data)
        self._load_pretrained_models()
    
    def predict_engagement(self, parent_data, message_content, message_type, send_time):
        """Predict engagement likelihood for a specific message"""
        try:
            # Extract features
            features = self._extract_engagement_features(parent_data, message_content, message_type, send_time)
            
            # Predict response likelihood
            response_probability = self._predict_response_likelihood(features)
            
            # Predict response time
            predicted_response_time = self._predict_response_time(features)
            
            # Predict optimal channel
            optimal_channel = self._predict_optimal_channel(features)
            
            # Calculate engagement score
            engagement_score = self._calculate_engagement_score(
                response_probability, 
                predicted_response_time, 
                parent_data
            )
            
            return {
                "response_probability": round(response_probability, 3),
                "predicted_response_time": round(predicted_response_time, 2),
                "optimal_channel": optimal_channel,
                "engagement_score": round(engagement_score, 3),
                "recommendations": self._generate_engagement_recommendations(features, engagement_score),
                "confidence": self._calculate_prediction_confidence(features)
            }
            
        except Exception as e:
            print(f"Error predicting engagement: {e}")
            return {
                "response_probability": 0.5,
                "predicted_response_time": 24.0,
                "optimal_channel": "email",
                "engagement_score": 0.5,
                "recommendations": ["Use standard communication approach"],
                "confidence": 0.5
            }
    
    def _extract_engagement_features(self, parent_data, message_content, message_type, send_time):
        """Extract features for engagement prediction"""
        features = {}
        
        # Parent engagement features
        features['response_rate'] = parent_data.get('response_rate', 0.5)
        features['response_time'] = parent_data.get('response_time', 24.0)
        features['read_rate'] = parent_data.get('read_rate', 0.7)
        features['total_messages'] = parent_data.get('total_messages', 10)
        
        # Message features
        features['message_length'] = len(message_content)
        features['message_type'] = message_type
        features['has_urgency_indicators'] = self._check_urgency_indicators(message_content)
        features['has_personalization'] = self._check_personalization(message_content)
        
        # Time features
        send_hour = datetime.strptime(send_time, "%H:%M").hour
        features['send_hour'] = send_hour
        features['is_business_hours'] = 8 <= send_hour <= 18
        features['is_weekend'] = datetime.now().weekday() >= 5
        
        # Channel features
        features['preferred_channel'] = parent_data.get('preferred_channel', 'email')
        features['channel_match'] = 1 if message_type == features['preferred_channel'] else 0
        
        return features
    
    def _predict_response_likelihood(self, features):
        """Predict likelihood of parent responding to message"""
        # Simple rule-based prediction (in real implementation, use trained ML model)
        base_probability = 0.5
        
        # Adjust based on parent engagement
        if features['response_rate'] > 0.8:
            base_probability += 0.2
        elif features['response_rate'] < 0.3:
            base_probability -= 0.2
        
        # Adjust based on message characteristics
        if features['has_urgency_indicators']:
            base_probability += 0.15
        
        if features['has_personalization']:
            base_probability += 0.1
        
        if features['channel_match']:
            base_probability += 0.1
        
        # Adjust based on timing
        if features['is_business_hours']:
            base_probability += 0.05
        
        return min(1.0, max(0.0, base_probability))
    
    def _predict_response_time(self, features):
        """Predict response time in hours"""
        # Simple rule-based prediction
        base_time = 24.0
        
        # Adjust based on parent engagement
        if features['response_rate'] > 0.8:
            base_time *= 0.5
        elif features['response_rate'] < 0.3:
            base_time *= 2.0
        
        # Adjust based on urgency
        if features['has_urgency_indicators']:
            base_time *= 0.3
        
        # Adjust based on channel
        if features['message_type'] == 'sms':
            base_time *= 0.5
        elif features['message_type'] == 'phone':
            base_time *= 0.2
        
        return max(0.1, base_time)
    
    def _predict_optimal_channel(self, features):
        """Predict optimal communication channel"""
        channels = ['email', 'sms', 'notification', 'phone']
        
        # Simple rule-based prediction
        if features['response_rate'] > 0.8:
            return 'email'
        elif features['response_time'] < 2:
            return 'sms'
        elif features['read_rate'] > 0.9:
            return 'notification'
        else:
            return 'phone'
    
    def _calculate_engagement_score(self, response_probability, predicted_response_time, parent_data):
        """Calculate overall engagement score"""
        # Weighted combination of factors
        response_weight = 0.4
        time_weight = 0.3
        historical_weight = 0.3
        
        # Normalize response time (lower is better)
        normalized_time = max(0, 1 - (predicted_response_time / 24))
        
        # Historical engagement
        historical_score = (parent_data.get('response_rate', 0.5) + parent_data.get('read_rate', 0.7)) / 2
        
        engagement_score = (
            response_probability * response_weight +
            normalized_time * time_weight +
            historical_score * historical_weight
        )
        
        return min(1.0, max(0.0, engagement_score))
    
    def _generate_engagement_recommendations(self, features, engagement_score):
        """Generate recommendations to improve engagement"""
        recommendations = []
        
        if engagement_score < 0.5:
            recommendations.append("Consider phone call for urgent matters")
            recommendations.append("Send follow-up reminders")
            recommendations.append("Use multiple communication channels")
        
        if features['response_time'] > 12:
            recommendations.append("Send messages during peak engagement hours")
            recommendations.append("Use shorter, more direct messages")
        
        if not features['has_personalization']:
            recommendations.append("Include student-specific information")
            recommendations.append("Personalize greeting and closing")
        
        if not features['channel_match']:
            recommendations.append(f"Try using {features['preferred_channel']} channel")
        
        return recommendations
    
    def _calculate_prediction_confidence(self, features):
        """Calculate confidence in prediction"""
        # Higher confidence with more data and consistent patterns
        confidence_factors = [
            features['total_messages'] / 100,  # More messages = higher confidence
            features['response_rate'],  # Higher response rate = higher confidence
            features['read_rate'],  # Higher read rate = higher confidence
            1 - abs(features['response_time'] - 24) / 24  # More predictable response time
        ]
        
        confidence = sum(confidence_factors) / len(confidence_factors)
        return min(1.0, max(0.0, confidence))
    
    def _check_urgency_indicators(self, message_content):
        """Check if message contains urgency indicators"""
        urgency_words = ["urgent", "immediate", "asap", "emergency", "critical", "important", "now"]
        return any(word in message_content.lower() for word in urgency_words)
    
    def _check_personalization(self, message_content):
        """Check if message contains personalization"""
        personalization_indicators = ["your child", "student", "son", "daughter", "family"]
        return any(indicator in message_content.lower() for indicator in personalization_indicators)
    
    def _load_pretrained_models(self):
        """Load pre-trained models (placeholder for real implementation)"""
        # In real implementation, load trained models from files
        print("Loading pre-trained engagement prediction models...")
        # self.response_model = joblib.load('models/response_model.pkl')
        # self.response_time_model = joblib.load('models/response_time_model.pkl')
        # self.channel_model = joblib.load('models/channel_model.pkl') 