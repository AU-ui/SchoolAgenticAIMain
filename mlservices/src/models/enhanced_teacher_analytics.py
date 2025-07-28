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