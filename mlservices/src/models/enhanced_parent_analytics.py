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
```

## **2. Enhanced Teacher Analytics with Feedback Integration**

```python:mlservices/src/models/enhanced_teacher_analytics.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import joblib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

from ..services.feedback_learning import FeedbackLearningService

class EnhancedTeacherAnalytics:
    def __init__(self):
        self.feedback_service = FeedbackLearningService()
        self.scaler = StandardScaler()
        self.logger = logging.getLogger(__name__)
        
        # Load pre-trained models
        self.models = {
            'attendance_prediction': self._load_model('attendance_prediction'),
            'task_priority': self._load_model('task_priority'),
            'resource_optimization': self._load_model('resource_optimization'),
            'grade_prediction': self._load_model('grade_prediction')
        }
    
    def predict_attendance_patterns(self, student_data: List[Dict]) -> Dict[str, Any]:
        """Enhanced attendance prediction with feedback learning"""
        
        # Prepare features
        features = self._extract_attendance_features(student_data)
        
        # Make prediction
        model = self.models['attendance_prediction']
        prediction = model.predict(features.reshape(1, -1))[0]
        
        # Get confidence score
        confidence = self._calculate_prediction_confidence(model, features)
        
        # Collect implicit feedback (will be updated when actual attendance is recorded)
        self.feedback_service.collect_feedback(
            model_type='attendance_prediction',
            prediction=prediction,
            actual_outcome=None,  # Will be updated later
            user_rating=None,
            context={
                'student_data': student_data,
                'prediction_confidence': confidence,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        return {
            'predicted_attendance_rate': prediction,
            'confidence': confidence,
            'risk_level': 'high' if prediction < 0.7 else 'medium' if prediction < 0.85 else 'low',
            'recommendations': self._generate_attendance_recommendations(prediction, student_data)
        }
    
    def optimize_task_priority(self, tasks: List[Dict], teacher_context: Dict) -> List[Dict]:
        """Enhanced task priority optimization with feedback learning"""
        
        optimized_tasks = []
        
        for task in tasks:
            # Prepare features
            features = self._extract_task_features(task, teacher_context)
            
            # Predict priority score
            model = self.models['task_priority']
            priority_score = model.predict_proba(features.reshape(1, -1))[0][1]  # Probability of high priority
            
            # Update task with ML insights
            task['ml_priority_score'] = priority_score
            task['recommended_order'] = len(optimized_tasks) + 1
            
            # Collect feedback opportunity
            self.feedback_service.collect_feedback(
                model_type='task_priority',
                prediction=priority_score,
                actual_outcome=None,  # Will be updated when task is completed
                user_rating=None,
                context={
                    'task': task,
                    'teacher_context': teacher_context,
                    'timestamp': datetime.now().isoformat()
                }
            )
            
            optimized_tasks.append(task)
        
        # Sort by ML priority score
        optimized_tasks.sort(key=lambda x: x['ml_priority_score'], reverse=True)
        
        return optimized_tasks
    
    def predict_student_performance(self, student_data: Dict, assignment_data: Dict) -> Dict[str, Any]:
        """Enhanced grade prediction with feedback learning"""
        
        # Prepare features
        features = self._extract_performance_features(student_data, assignment_data)
        
        # Make prediction
        model = self.models['grade_prediction']
        predicted_grade = model.predict(features.reshape(1, -1))[0]
        
        # Calculate confidence
        confidence = self._calculate_prediction_confidence(model, features)
        
        # Generate insights
        insights = self._generate_performance_insights(predicted_grade, student_data)
        
        # Collect feedback
        self.feedback_service.collect_feedback(
            model_type='grade_prediction',
            prediction=predicted_grade,
            actual_outcome=None,  # Will be updated when grade is recorded
            user_rating=None,
            context={
                'student_data': student_data,
                'assignment_data': assignment_data,
                'prediction_confidence': confidence,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        return {
            'predicted_grade': predicted_grade,
            'confidence': confidence,
            'grade_range': self._get_grade_range(predicted_grade),
            'insights': insights,
            'recommendations': self._generate_performance_recommendations(predicted_grade, student_data)
        }
    
    def optimize_resource_allocation(self, resources: List[Dict], demand_data: Dict) -> Dict[str, Any]:
        """Enhanced resource optimization with feedback learning"""
        
        # Prepare features
        features = self._extract_resource_features(resources, demand_data)
        
        # Make optimization prediction
        model = self.models['resource_optimization']
        optimization_score = model.predict(features.reshape(1, -1))[0]
        
        # Generate optimization recommendations
        recommendations = self._generate_resource_recommendations(optimization_score, resources, demand_data)
        
        # Collect feedback
        self.feedback_service.collect_feedback(
            model_type='resource_optimization',
            prediction=optimization_score,
            actual_outcome=None,  # Will be updated when resource usage is recorded
            user_rating=None,
            context={
                'resources': resources,
                'demand_data': demand_data,
                'optimization_score': optimization_score,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        return {
            'optimization_score': optimization_score,
            'recommendations': recommendations,
            'efficiency_gain': self._calculate_efficiency_gain(optimization_score),
            'resource_utilization': self._calculate_resource_utilization(recommendations)
        }
    
    def get_ml_insights_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive ML insights for dashboard"""
        
        insights = {}
        
        for model_type in self.models.keys():
            model_insights = self.feedback_service.get_model_insights(model_type)
            insights[model_type] = model_insights
        
        # Overall system insights
        total_feedback = len(self.feedback_service.feedback_data)
        avg_rating = np.mean([f['user_rating'] for f in self.feedback_service.feedback_data 
                            if f['user_rating'] is not None]) if self.feedback_service.feedback_data else 0
        
        insights['system_overview'] = {
            'total_feedback_collected': total_feedback,
            'average_user_rating': avg_rating,
            'models_retrained': len([m for m in self.models.values() if m.get('last_updated')]),
            'system_health': 'excellent' if avg_rating > 4.0 else 'good' if avg_rating > 3.0 else 'needs_improvement'
        }
        
        return insights
    
    def _extract_attendance_features(self, student_data: List[Dict]) -> np.ndarray:
        """Extract features for attendance prediction"""
        
        features = []
        
        for student in student_data:
            attendance_history = student.get('attendance_history', [])
            recent_attendance = attendance_history[-30:] if len(attendance_history) >= 30 else attendance_history
            
            features.extend([
                len(recent_attendance),
                sum(1 for a in recent_attendance if a['status'] == 'present'),
                sum(1 for a in recent_attendance if a['status'] == 'late'),
                sum(1 for a in recent_attendance if a['status'] == 'absent'),
                student.get('grade_level', 0),
                student.get('previous_performance', 0.5),
                len(student.get('extracurricular_activities', [])),
                student.get('parent_engagement_score', 0.5)
            ])
        
        return np.array(features)
    
    def _extract_task_features(self, task: Dict, teacher_context: Dict) -> np.ndarray:
        """Extract features for task priority prediction"""
        
        features = [
            task.get('estimated_duration', 0),
            task.get('deadline_days_remaining', 30),
            task.get('complexity', 1),
            task.get('dependencies_count', 0),
            task.get('student_count', 0),
            teacher_context.get('current_workload', 0.5),
            teacher_context.get('experience_level', 1),
            task.get('type', 'general'),
            task.get('priority', 1)
        ]
        
        return np.array(features)
    
    def _extract_performance_features(self, student_data: Dict, assignment_data: Dict) -> np.ndarray:
        """Extract features for performance prediction"""
        
        features = [
            student_data.get('average_grade', 0.5),
            student_data.get('attendance_rate', 0.5),
            student_data.get('homework_completion_rate', 0.5),
            assignment_data.get('difficulty', 1),
            assignment_data.get('type', 'general'),
            student_data.get('study_time_hours', 0),
            student_data.get('parent_support_score', 0.5),
            student_data.get('previous_similar_assignments', 0)
        ]
        
        return np.array(features)
    
    def _extract_resource_features(self, resources: List[Dict], demand_data: Dict) -> np.ndarray:
        """Extract features for resource optimization"""
        
        features = [
            len(resources),
            sum(r.get('availability', 0) for r in resources),
            sum(r.get('utilization_rate', 0) for r in resources),
            demand_data.get('total_demand', 0),
            demand_data.get('peak_hours', 0),
            demand_data.get('seasonal_factor', 1.0)
        ]
        
        return np.array(features)
    
    def _calculate_prediction_confidence(self, model, features: np.ndarray) -> float:
        """Calculate confidence score for prediction"""
        
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features.reshape(1, -1))[0]
            return max(proba)
        else:
            # For regression models, use standard deviation of predictions
            predictions = []
            for _ in range(10):
                pred = model.predict(features.reshape(1, -1))[0]
                predictions.append(pred)
            
            std_dev = np.std(predictions)
            return max(0.1, 1 - std_dev)  # Higher confidence for lower std dev
    
    def _load_model(self, model_type: str):
        """Load pre-trained model"""
        
        try:
            model_path = f"mlservices/models/{model_type}.pkl"
            return joblib.load(model_path)
        except FileNotFoundError:
            self.logger.warning(f"Model {model_type} not found, using default")
            return RandomForestRegressor(n_estimators=100, random_state=42)
    
    def _generate_attendance_recommendations(self, prediction: float, student_data: List[Dict]) -> List[str]:
        """Generate attendance recommendations"""
        
        recommendations = []
        
        if prediction < 0.7:
            recommendations.extend([
                "Consider sending attendance reminders to parents",
                "Schedule one-on-one meetings with students",
                "Implement attendance incentives"
            ])
        elif prediction < 0.85:
            recommendations.extend([
                "Monitor attendance patterns closely",
                "Send gentle reminders for missed classes"
            ])
        
        return recommendations
    
    def _generate_performance_recommendations(self, predicted_grade: float, student_data: Dict) -> List[str]:
        """Generate performance recommendations"""
        
        recommendations = []
        
        if predicted_grade < 0.6:
            recommendations.extend([
                "Provide additional tutoring support",
                "Break down assignments into smaller tasks",
                "Increase parent communication"
            ])
        elif predicted_grade < 0.8:
            recommendations.extend([
                "Offer extra practice materials",
                "Schedule regular check-ins"
            ])
        
        return recommendations
    
    def _generate_resource_recommendations(self, optimization_score: float, resources: List[Dict], demand_data: Dict) -> List[Dict]:
        """Generate resource optimization recommendations"""
        
        recommendations = []
        
        if optimization_score < 0.6:
            recommendations.append({
                'type': 'increase_capacity',
                'message': 'Consider adding more resources',
                'priority': 'high'
            })
        elif optimization_score < 0.8:
            recommendations.append({
                'type': 'optimize_schedule',
                'message': 'Optimize resource scheduling',
                'priority': 'medium'
            })
        
        return recommendations
```

## **3. Enhanced Parent Communication ML with Feedback**

```python:mlservices/src/models/enhanced_parent_analytics.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
import joblib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

from ..services.feedback_learning import FeedbackLearningService

class EnhancedParentAnalytics:
    def __init__(self):
        self.feedback_service = FeedbackLearningService()
        self.sentiment_vectorizer = TfidfVectorizer(max_features=1000)
        self.language_detector = self._load_language_detector()
        self.logger = logging.getLogger(__name__)
        
        # Load pre-trained models
        self.models = {
            'engagement_prediction': self._load_model('engagement_prediction'),
            'communication_optimization': self._load_model('communication_optimization'),
            'sentiment_analysis': self._load_model('sentiment_analysis'),
            'language_detection': self._load_model('language_detection')
        }
    
    def predict_parent_engagement(self, parent_data: Dict, communication_history: List[Dict]) -> Dict[str, Any]:
        """Enhanced parent engagement prediction with feedback learning"""
        
        # Prepare features
        features = self._extract_engagement_features(parent_data, communication_history)
        
        # Make prediction
        model = self.models['engagement_prediction']
        engagement_score = model.predict(features.reshape(1, -1))[0]
        
        # Calculate confidence
        confidence = self._calculate_prediction_confidence(model, features)
        
        # Generate recommendations
        recommendations = self._generate_engagement_recommendations(engagement_score, parent_data)
        
        # Collect feedback
        self.feedback_service.collect_feedback(
            model_type='engagement_prediction',
            prediction=engagement_score,
            actual_outcome=None,  # Will be updated when engagement is measured
            user_rating=None,
            context={
                'parent_data': parent_data,
                'communication_history': communication_history,
                'prediction_confidence': confidence,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        return {
            'engagement_score': engagement_score,
            'confidence': confidence,
            'engagement_level': self._get_engagement_level(engagement_score),
            'recommendations': recommendations,
            'communication_preferences': self._analyze_communication_preferences(communication_history)
        }
    
    def optimize_communication_strategy(self, parent_data: Dict, message_content: str, 
                                     communication_goals: Dict) -> Dict[str, Any]:
        """Enhanced communication optimization with feedback learning"""
        
        # Prepare features
        features = self._extract_communication_features(parent_data, message_content, communication_goals)
        
        # Make optimization prediction
        model = self.models['communication_optimization']
        optimization_score = model.predict(features.reshape(1, -1))[0]
        
        # Generate optimized communication strategy
        strategy = self._generate_communication_strategy(optimization_score, parent_data, message_content)
        
        # Collect feedback
        self.feedback_service.collect_feedback(
            model_type='communication_optimization',
            prediction=optimization_score,
            actual_outcome=None,  # Will be updated when communication is sent
            user_rating=None,
            context={
                'parent_data': parent_data,
                'message_content': message_content,
                'communication_goals': communication_goals,
                'optimization_score': optimization_score,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        return {
            'optimization_score': optimization_score,
            'recommended_channel': strategy['channel'],
            'recommended_timing': strategy['timing'],
            'message_tone': strategy['tone'],
            'personalization_level': strategy['personalization'],
            'expected_effectiveness': optimization_score
        }
    
    def analyze_sentiment_and_language(self, messages: List[Dict]) -> Dict[str, Any]:
        """Enhanced sentiment and language analysis with feedback learning"""
        
        results = {
            'sentiment_analysis': [],
            'language_detection': [],
            'overall_sentiment': 'neutral',
            'language_distribution': {},
            'engagement_insights': []
        }
        
        for message in messages:
            # Sentiment analysis
            sentiment_features = self._extract_sentiment_features(message['content'])
            sentiment_model = self.models['sentiment_analysis']
            sentiment_score = sentiment_model.predict(sentiment_features.reshape(1, -1))[0]
            
            # Language detection
            language_features = self._extract_language_features(message['content'])
            language_model = self.models['language_detection']
            detected_language = language_model.predict(language_features.reshape(1, -1))[0]
            
            # Collect feedback
            self.feedback_service.collect_feedback(
                model_type='sentiment_analysis',
                prediction=sentiment_score,
                actual_outcome=message.get('actual_sentiment'),
                user_rating=message.get('user_rating'),
                context={
                    'message_content': message['content'],
                    'detected_language': detected_language,
                    'timestamp': message.get('timestamp', datetime.now().isoformat())
                }
            )
            
            results['sentiment_analysis'].append({
                'message_id': message.get('id'),
                'sentiment_score': sentiment_score,
                'sentiment_label': self._get_sentiment_label(sentiment_score),
                'confidence': self._calculate_prediction_confidence(sentiment_model, sentiment_features)
            })
            
            results['language_detection'].append({
                'message_id': message.get('id'),
                'detected_language': detected_language,
                'confidence': self._calculate_prediction_confidence(language_model, language_features)
            })
        
        # Calculate overall metrics
        sentiment_scores = [r['sentiment_score'] for r in results['sentiment_analysis']]
        results['overall_sentiment'] = self._get_sentiment_label(np.mean(sentiment_scores))
        
        language_counts = {}
        for detection in results['language_detection']:
            lang = detection['detected_language']
            language_counts[lang] = language_counts.get(lang, 0) + 1
        results['language_distribution'] = language_counts
        
        return results
    
    def generate_personalized_notifications(self, parent_data: Dict, notification_type: str, 
                                         context: Dict) -> Dict[str, Any]:
        """Enhanced personalized notification generation with feedback learning"""
        
        # Prepare features
        features = self._extract_notification_features(parent_data, notification_type, context)
        
        # Generate personalized notification
        notification = self._generate_notification_content(parent_data, notification_type, context)
        
        # Predict effectiveness
        effectiveness_score = self._predict_notification_effectiveness(features)
        
        # Collect feedback
        self.feedback_service.collect_feedback(
            model_type='notification_effectiveness',
            prediction=effectiveness_score,
            actual_outcome=None,  # Will be updated when notification is sent
            user_rating=None,
            context={
                'parent_data': parent_data,
                'notification_type': notification_type,
                'context': context,
                'effectiveness_score': effectiveness_score,
                'timestamp': datetime.now().isoformat()
            }
        )
        
        return {
            'notification_content': notification['content'],
            'personalization_level': notification['personalization_level'],
            'expected_effectiveness': effectiveness_score,
            'recommended_channel': notification['channel'],
            'optimal_timing': notification['timing']
        }
    
    def _extract_engagement_features(self, parent_data: Dict, communication_history: List[Dict]) -> np.ndarray:
        """Extract features for engagement prediction"""
        
        features = [
            parent_data.get('response_rate', 0.5),
            parent_data.get('average_response_time', 24),  # hours
            len(communication_history),
            sum(1 for c in communication_history if c.get('parent_responded', False)),
            parent_data.get('preferred_channel', 'email'),
            parent_data.get('language_preference', 'english'),
            parent_data.get('notification_frequency', 'weekly'),
            parent_data.get('involvement_level', 1)
        ]
        
        return np.array(features)
    
    def _extract_communication_features(self, parent_data: Dict, message_content: str, 
                                     communication_goals: Dict) -> np.ndarray:
        """Extract features for communication optimization"""
        
        features = [
            len(message_content),
            parent_data.get('preferred_channel', 'email'),
            parent_data.get('language_preference', 'english'),
            communication_goals.get('urgency', 1),
            communication_goals.get('formality', 1),
            communication_goals.get('personalization_level', 1),
            parent_data.get('previous_engagement', 0.5),
            parent_data.get('response_rate', 0.5)
        ]
        
        return np.array(features)
    
    def _extract_sentiment_features(self, content: str) -> np.ndarray:
        """Extract features for sentiment analysis"""
        
        # Use TF-IDF vectorization for text features
        vectorized = self.sentiment_vectorizer.fit_transform([content])
        return vectorized.toarray()[0]
    
    def _extract_language_features(self, content: str) -> np.ndarray:
        """Extract features for language detection"""
        
        # Character-based features for language detection
        features = []
        
        # Character frequency
        char_freq = {}
        for char in content.lower():
            if char.isalpha():
                char_freq[char] = char_freq.get(char, 0) + 1
        
        # Normalize character frequencies
        total_chars = sum(char_freq.values()) if char_freq else 1
        for char in 'abcdefghijklmnopqrstuvwxyz':
            features.append(char_freq.get(char, 0) / total_chars)
        
        # Word length distribution
        words = content.split()
        word_lengths = [len(word) for word in words if word.isalpha()]
        if word_lengths:
            features.extend([
                np.mean(word_lengths),
                np.std(word_lengths),
                len(word_lengths)
            ])
        else:
            features.extend([0, 0, 0])
        
        return np.array(features)
    
    def _extract_notification_features(self, parent_data: Dict, notification_type: str, 
                                     context: Dict) -> np.ndarray:
        """Extract features for notification effectiveness"""
        
        features = [
            parent_data.get('response_rate', 0.5),
            parent_data.get('preferred_channel', 'email'),
            parent_data.get('notification_frequency', 'weekly'),
            context.get('urgency', 1),
            context.get('importance', 1),
            len(parent_data.get('children', [])),
            parent_data.get('involvement_level', 1)
        ]
        
        return np.array(features)
    
    def _calculate_prediction_confidence(self, model, features: np.ndarray) -> float:
        """Calculate confidence score for prediction"""
        
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features.reshape(1, -1))[0]
            return max(proba)
        else:
            # For regression models, use standard deviation
            predictions = []
            for _ in range(10):
                pred = model.predict(features.reshape(1, -1))[0]
                predictions.append(pred)
            
            std_dev = np.std(predictions)
            return max(0.1, 1 - std_dev)
    
    def _load_model(self, model_type: str):
        """Load pre-trained model"""
        
        try:
            model_path = f"mlservices/models/{model_type}.pkl"
            return joblib.load(model_path)
        except FileNotFoundError:
            self.logger.warning(f"Model {model_type} not found, using default")
            return RandomForestClassifier(n_estimators=100, random_state=42)
    
    def _load_language_detector(self):
        """Load language detection model"""
        
        try:
            return joblib.load("mlservices/models/language_detector.pkl")
        except FileNotFoundError:
            return MultinomialNB()
    
    def _get_engagement_level(self, score: float) -> str:
        """Get engagement level from score"""
        
        if score >= 0.8:
            return 'high'
        elif score >= 0.6:
            return 'medium'
        else:
            return 'low'
    
    def _get_sentiment_label(self, score: float) -> str:
        """Get sentiment label from score"""
        
        if score >= 0.6:
            return 'positive'
        elif score <= 0.4:
            return 'negative'
        else:
            return 'neutral'
    
    def _generate_engagement_recommendations(self, engagement_score: float, parent_data: Dict) -> List[str]:
        """Generate engagement recommendations"""
        
        recommendations = []
        
        if engagement_score < 0.5:
            recommendations.extend([
                "Increase communication frequency",
                "Use multiple communication channels",
                "Personalize messages more",
                "Offer incentives for engagement"
            ])
        elif engagement_score < 0.7:
            recommendations.extend([
                "Maintain current communication level",
                "Add more interactive elements",
                "Request feedback regularly"
            ])
        
        return recommendations
    
    def _generate_communication_strategy(self, optimization_score: float, parent_data: Dict, 
                                       message_content: str) -> Dict[str, Any]:
        """Generate optimized communication strategy"""
        
        strategy = {
            'channel': parent_data.get('preferred_channel', 'email'),
            'timing': 'morning',  # Default
            'tone': 'professional',
            'personalization': 'medium'
        }
        
        if optimization_score < 0.6:
            strategy['personalization'] = 'high'
            strategy['channel'] = 'multiple'
        
        return strategy
    
    def _analyze_communication_preferences(self, communication_history: List[Dict]) -> Dict[str, Any]:
        """Analyze communication preferences from history"""
        
        if not communication_history:
            return {}
        
        channels = [c.get('channel', 'email') for c in communication_history]
        response_times = [c.get('response_time', 24) for c in communication_history if c.get('response_time')]
        
        return {
            'preferred_channel': max(set(channels), key=channels.count) if channels else 'email',
            'average_response_time': np.mean(response_times) if response_times else 24,
            'total_communications': len(communication_history),
            'response_rate': sum(1 for c in communication_history if c.get('parent_responded', False)) / len(communication_history)
        }
    
    def _predict_notification_effectiveness(self, features: np.ndarray) -> float:
        """Predict notification effectiveness"""
        
        # Simple heuristic-based prediction
        base_score = 0.7
        
        # Adjust based on features
        if features[0] > 0.7:  # High response rate
            base_score += 0.2
        if features[1] == 'sms':  # SMS preference
            base_score += 0.1
        if features[3] > 0.8:  # High urgency
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def _generate_notification_content(self, parent_data: Dict, notification_type: str, 
                                     context: Dict) -> Dict[str, Any]:
        """Generate personalized notification content"""
        
        templates = {
            'attendance': {
                'content': f"Dear {parent_data.get('first_name', 'Parent')}, your child's attendance has been updated.",
                'personalization_level': 'medium',
                'channel': parent_data.get('preferred_channel', 'email'),
                'timing': 'immediate'
            },
            'grade': {
                'content': f"Dear {parent_data.get('first_name', 'Parent')}, new grades have been posted for your child.",
                'personalization_level': 'high',
                'channel': parent_data.get('preferred_channel', 'email'),
                'timing': 'evening'
            },
            'event': {
                'content': f"Dear {parent_data.get('first_name', 'Parent')}, there's an upcoming school event you might be interested in.",
                'personalization_level': 'medium',
                'channel': parent_data.get('preferred_channel', 'email'),
                'timing': 'morning'
            }
        }
        
        return templates.get(notification_type, templates['attendance']) 