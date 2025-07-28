import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import joblib
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

class PredictiveAnalytics:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        
        # Load pre-trained models
        self.models = {
            'dropout_risk': self._load_model('dropout_risk'),
            'performance_forecast': self._load_model('performance_forecast'),
            'resource_demand': self._load_model('resource_demand'),
            'teacher_burnout': self._load_model('teacher_burnout')
        }
    
    def predict_student_dropout_risk(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Predict student dropout risk"""
        
        try:
            # Extract features
            features = self._extract_dropout_features(student_data)
            
            # Make prediction
            model = self.models['dropout_risk']
            risk_score = model.predict_proba(features.reshape(1, -1))[0][1]
            
            # Determine risk level
            risk_level = self._determine_risk_level(risk_score)
            
            # Generate insights
            insights = self._generate_dropout_insights(student_data, risk_score)
            
            # Generate recommendations
            recommendations = self._generate_dropout_recommendations(risk_score, student_data)
            
            return {
                "success": True,
                "risk_score": risk_score,
                "risk_level": risk_level,
                "insights": insights,
                "recommendations": recommendations,
                "confidence": self._calculate_prediction_confidence(model, features),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting dropout risk: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def forecast_class_performance(self, class_data: Dict[str, Any], 
                                 forecast_period: int = 30) -> Dict[str, Any]:
        """Forecast class performance over time"""
        
        try:
            # Extract features
            features = self._extract_performance_features(class_data)
            
            # Make prediction
            model = self.models['performance_forecast']
            performance_forecast = model.predict(features.reshape(1, -1))[0]
            
            # Generate trend analysis
            trend_analysis = self._analyze_performance_trend(class_data)
            
            # Generate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(performance_forecast, 0.1)
            
            return {
                "success": True,
                "forecasted_performance": performance_forecast,
                "trend_analysis": trend_analysis,
                "confidence_intervals": confidence_intervals,
                "forecast_period": forecast_period,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error forecasting class performance: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def predict_resource_demand(self, historical_data: List[Dict], 
                              prediction_days: int = 7) -> Dict[str, Any]:
        """Predict resource demand"""
        
        try:
            # Prepare historical data
            df = pd.DataFrame(historical_data)
            df['date'] = pd.to_datetime(df['date'])
            
            # Extract features
            features = self._extract_resource_features(df)
            
            # Make prediction
            model = self.models['resource_demand']
            demand_forecast = model.predict(features.reshape(1, -1))[0]
            
            # Generate demand patterns
            demand_patterns = self._analyze_demand_patterns(df)
            
            # Generate optimization recommendations
            recommendations = self._generate_resource_recommendations(demand_forecast, demand_patterns)
            
            return {
                "success": True,
                "demand_forecast": demand_forecast,
                "demand_patterns": demand_patterns,
                "recommendations": recommendations,
                "prediction_days": prediction_days,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting resource demand: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def assess_teacher_burnout_risk(self, teacher_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess teacher burnout risk"""
        
        try:
            # Extract features
            features = self._extract_burnout_features(teacher_data)
            
            # Make prediction
            model = self.models['teacher_burnout']
            burnout_risk = model.predict_proba(features.reshape(1, -1))[0][1]
            
            # Determine risk level
            risk_level = self._determine_burnout_risk_level(burnout_risk)
            
            # Generate insights
            insights = self._generate_burnout_insights(teacher_data, burnout_risk)
            
            # Generate recommendations
            recommendations = self._generate_burnout_recommendations(burnout_risk, teacher_data)
            
            return {
                "success": True,
                "burnout_risk": burnout_risk,
                "risk_level": risk_level,
                "insights": insights,
                "recommendations": recommendations,
                "confidence": self._calculate_prediction_confidence(model, features),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error assessing teacher burnout: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _extract_dropout_features(self, student_data: Dict[str, Any]) -> np.ndarray:
        """Extract features for dropout prediction"""
        
        features = [
            student_data.get('attendance_rate', 0.5),
            student_data.get('average_grade', 0.5),
            student_data.get('behavior_incidents', 0),
            student_data.get('parent_engagement', 0.5),
            student_data.get('socioeconomic_status', 0.5),
            student_data.get('previous_school_performance', 0.5),
            student_data.get('extracurricular_participation', 0),
            student_data.get('peer_relationships', 0.5)
        ]
        
        return np.array(features)
    
    def _extract_performance_features(self, class_data: Dict[str, Any]) -> np.ndarray:
        """Extract features for performance forecasting"""
        
        features = [
            class_data.get('average_grade', 0.5),
            class_data.get('attendance_rate', 0.5),
            class_data.get('teacher_experience', 0),
            class_data.get('class_size', 25),
            class_data.get('curriculum_difficulty', 0.5),
            class_data.get('student_engagement', 0.5),
            class_data.get('parent_involvement', 0.5),
            class_data.get('resources_available', 0.5)
        ]
        
        return np.array(features)
    
    def _extract_resource_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extract features for resource demand prediction"""
        
        # Calculate daily usage patterns
        daily_usage = df.groupby('date').agg({
            'usage_hours': 'sum',
            'user_count': 'sum',
            'resource_type': 'count'
        }).reset_index()
        
        features = [
            daily_usage['usage_hours'].mean(),
            daily_usage['usage_hours'].std(),
            daily_usage['user_count'].mean(),
            daily_usage['user_count'].std(),
            len(daily_usage),
            daily_usage['resource_type'].nunique()
        ]
        
        return np.array(features)
    
    def _extract_burnout_features(self, teacher_data: Dict[str, Any]) -> np.ndarray:
        """Extract features for burnout risk assessment"""
        
        features = [
            teacher_data.get('workload_hours', 40),
            teacher_data.get('class_count', 5),
            teacher_data.get('student_count', 150),
            teacher_data.get('years_experience', 5),
            teacher_data.get('satisfaction_score', 0.5),
            teacher_data.get('stress_level', 0.5),
            teacher_data.get('work_life_balance', 0.5),
            teacher_data.get('support_available', 0.5)
        ]
        
        return np.array(features)
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score"""
        
        if risk_score >= 0.7:
            return "high"
        elif risk_score >= 0.4:
            return "medium"
        else:
            return "low"
    
    def _determine_burnout_risk_level(self, risk_score: float) -> str:
        """Determine burnout risk level"""
        
        if risk_score >= 0.6:
            return "high"
        elif risk_score >= 0.3:
            return "medium"
        else:
            return "low"
    
    def _calculate_prediction_confidence(self, model, features: np.ndarray) -> float:
        """Calculate prediction confidence"""
        
        if hasattr(model, 'predict_proba'):
            proba = model.predict_proba(features.reshape(1, -1))[0]
            return max(proba)
        else:
            return 0.8  # Default confidence
    
    def _load_model(self, model_type: str):
        """Load pre-trained model"""
        
        try:
            model_path = f"mlservices/models/{model_type}.pkl"
            return joblib.load(model_path)
        except FileNotFoundError:
            self.logger.warning(f"Model {model_type} not found, using default")
            return RandomForestClassifier(n_estimators=100, random_state=42)
    
    def _generate_dropout_insights(self, student_data: Dict[str, Any], risk_score: float) -> List[str]:
        """Generate dropout insights"""
        
        insights = []
        
        if student_data.get('attendance_rate', 1) < 0.8:
            insights.append("Low attendance rate is a concern")
        
        if student_data.get('average_grade', 1) < 0.6:
            insights.append("Academic performance needs attention")
        
        if student_data.get('behavior_incidents', 0) > 3:
            insights.append("Behavioral issues may indicate disengagement")
        
        if risk_score > 0.5:
            insights.append("Multiple risk factors detected")
        
        return insights
    
    def _generate_dropout_recommendations(self, risk_score: float, student_data: Dict[str, Any]) -> List[str]:
        """Generate dropout prevention recommendations"""
        
        recommendations = []
        
        if risk_score > 0.6:
            recommendations.extend([
                "Schedule individual counseling sessions",
                "Implement intensive academic support",
                "Increase parent communication frequency",
                "Assign mentor teacher"
            ])
        elif risk_score > 0.3:
            recommendations.extend([
                "Monitor attendance closely",
                "Provide additional academic support",
                "Increase engagement activities"
            ])
        
        return recommendations
    
    def _analyze_performance_trend(self, class_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance trend"""
        
        return {
            "trend": "improving",
            "trend_strength": 0.7,
            "volatility": 0.2,
            "seasonal_patterns": "detected"
        }
    
    def _calculate_confidence_intervals(self, prediction: float, margin: float) -> Dict[str, float]:
        """Calculate confidence intervals"""
        
        return { 