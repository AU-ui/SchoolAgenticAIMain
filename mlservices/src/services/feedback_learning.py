import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.preprocessing import StandardScaler
import joblib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

class FeedbackLearningService:
    def __init__(self):
        self.models = {}
        self.feedback_data = []
        self.model_performance = {}
        self.retraining_threshold = 0.1  # Retrain if performance drops by 10%
        self.min_feedback_samples = 50
        self.logger = logging.getLogger(__name__)
        
    def collect_feedback(self, model_type: str, prediction: Any, 
                        actual_outcome: Any, user_rating: int, 
                        context: Dict[str, Any]) -> None:
        """Collect user feedback for model improvement"""
        
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'model_type': model_type,
            'prediction': prediction,
            'actual_outcome': actual_outcome,
            'user_rating': user_rating,  # 1-5 scale
            'context': context,
            'feedback_type': 'explicit' if user_rating else 'implicit'
        }
        
        self.feedback_data.append(feedback_entry)
        self.logger.info(f"Feedback collected for {model_type}: Rating={user_rating}")
        
        # Check if retraining is needed
        if len(self.feedback_data) >= self.min_feedback_samples:
            self._evaluate_model_performance(model_type)
    
    def _evaluate_model_performance(self, model_type: str) -> None:
        """Evaluate model performance and trigger retraining if needed"""
        
        recent_feedback = [f for f in self.feedback_data 
                          if f['model_type'] == model_type 
                          and f['timestamp'] > (datetime.now() - timedelta(days=30)).isoformat()]
        
        if len(recent_feedback) < 20:
            return
            
        # Calculate performance metrics
        predictions = [f['prediction'] for f in recent_feedback]
        actuals = [f['actual_outcome'] for f in recent_feedback]
        ratings = [f['user_rating'] for f in recent_feedback]
        
        # Calculate accuracy and user satisfaction
        accuracy = self._calculate_accuracy(predictions, actuals)
        avg_rating = np.mean(ratings)
        
        # Store performance metrics
        if model_type not in self.model_performance:
            self.model_performance[model_type] = []
            
        self.model_performance[model_type].append({
            'timestamp': datetime.now().isoformat(),
            'accuracy': accuracy,
            'avg_rating': avg_rating,
            'sample_count': len(recent_feedback)
        })
        
        # Check if retraining is needed
        if len(self.model_performance[model_type]) > 1:
            prev_performance = self.model_performance[model_type][-2]
            performance_drop = prev_performance['accuracy'] - accuracy
            
            if performance_drop > self.retraining_threshold or avg_rating < 3.0:
                self.logger.info(f"Triggering retraining for {model_type}")
                self._retrain_model(model_type)
    
    def _retrain_model(self, model_type: str) -> None:
        """Retrain model with new feedback data"""
        
        # Prepare training data from feedback
        training_data = self._prepare_training_data(model_type)
        
        if len(training_data['X']) < 100:  # Need sufficient data
            return
            
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            training_data['X'], training_data['y'], test_size=0.2, random_state=42
        )
        
        # Retrain model based on type
        if model_type == 'attendance_prediction':
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        elif model_type == 'task_priority':
            model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        else:
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        
        # Train and evaluate
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        # Save updated model
        model_path = f"mlservices/models/{model_type}_updated.pkl"
        joblib.dump(model, model_path)
        
        # Update model registry
        self.models[model_type] = {
            'model': model,
            'path': model_path,
            'last_updated': datetime.now().isoformat(),
            'accuracy': accuracy
        }
        
        self.logger.info(f"Model {model_type} retrained with accuracy: {accuracy:.3f}")
    
    def _prepare_training_data(self, model_type: str) -> Dict[str, np.ndarray]:
        """Prepare training data from feedback"""
        
        relevant_feedback = [f for f in self.feedback_data 
                           if f['model_type'] == model_type]
        
        X = []
        y = []
        
        for feedback in relevant_feedback:
            # Extract features from context
            features = self._extract_features(feedback['context'])
            X.append(features)
            y.append(feedback['actual_outcome'])
        
        return {
            'X': np.array(X),
            'y': np.array(y)
        }
    
    def _extract_features(self, context: Dict[str, Any]) -> List[float]:
        """Extract numerical features from context"""
        
        features = []
        
        # Time-based features
        if 'timestamp' in context:
            dt = datetime.fromisoformat(context['timestamp'])
            features.extend([
                dt.hour,
                dt.weekday(),
                dt.month,
                dt.day
            ])
        
        # User behavior features
        features.extend([
            context.get('user_id', 0),
            context.get('session_duration', 0),
            context.get('interaction_count', 0),
            context.get('previous_accuracy', 0.5)
        ])
        
        # Context-specific features
        if 'attendance' in context:
            features.extend([
                context['attendance'].get('present_days', 0),
                context['attendance'].get('total_days', 1),
                context['attendance'].get('late_count', 0)
            ])
        
        if 'task' in context:
            features.extend([
                context['task'].get('priority', 1),
                context['task'].get('estimated_duration', 0),
                context['task'].get('complexity', 1)
            ])
        
        return features
    
    def get_model_insights(self, model_type: str) -> Dict[str, Any]:
        """Get insights about model performance and feedback"""
        
        if model_type not in self.model_performance:
            return {}
        
        performance_history = self.model_performance[model_type]
        recent_feedback = [f for f in self.feedback_data 
                          if f['model_type'] == model_type 
                          and f['timestamp'] > (datetime.now() - timedelta(days=7)).isoformat()]
        
        return {
            'model_type': model_type,
            'current_accuracy': performance_history[-1]['accuracy'] if performance_history else 0,
            'avg_user_rating': np.mean([f['user_rating'] for f in recent_feedback]) if recent_feedback else 0,
            'feedback_count': len(recent_feedback),
            'last_retrained': self.models.get(model_type, {}).get('last_updated', 'Never'),
            'performance_trend': 'improving' if len(performance_history) > 1 and 
                               performance_history[-1]['accuracy'] > performance_history[-2]['accuracy'] else 'declining'
        } 