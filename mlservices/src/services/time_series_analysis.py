import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import warnings
warnings.filterwarnings('ignore')

class TimeSeriesAnalysis:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        
    def analyze_attendance_trends(self, attendance_data: List[Dict]) -> Dict[str, Any]:
        """Analyze attendance trends over time"""
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(attendance_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculate daily attendance rates
            daily_attendance = df.groupby('date').agg({
                'student_id': 'count',
                'status': lambda x: (x == 'present').sum()
            }).reset_index()
            
            daily_attendance['attendance_rate'] = (
                daily_attendance['status'] / daily_attendance['student_id']
            )
            
            # Detect trends
            trend_analysis = self._detect_trend(daily_attendance['attendance_rate'])
            
            # Detect seasonal patterns
            seasonal_patterns = self._detect_seasonal_patterns(daily_attendance)
            
            # Predict future attendance
            future_predictions = self._predict_future_attendance(daily_attendance)
            
            # Detect anomalies
            anomalies = self._detect_anomalies(daily_attendance['attendance_rate'])
            
            return {
                "trend_analysis": trend_analysis,
                "seasonal_patterns": seasonal_patterns,
                "future_predictions": future_predictions,
                "anomalies": anomalies,
                "overall_trend": "increasing" if trend_analysis['slope'] > 0 else "decreasing"
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing attendance trends: {str(e)}")
            return {"error": "Failed to analyze attendance trends"}
    
    def analyze_performance_trajectories(self, performance_data: List[Dict]) -> Dict[str, Any]:
        """Analyze student performance trajectories over time"""
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(performance_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Calculate moving averages
            df['grade_moving_avg'] = df['grade'].rolling(window=5, min_periods=1).mean()
            
            # Detect performance trends for each student
            student_trends = {}
            
            for student_id in df['student_id'].unique():
                student_data = df[df['student_id'] == student_id]
                
                if len(student_data) >= 3:  # Need at least 3 data points
                    trend = self._analyze_student_trend(student_data)
                    student_trends[student_id] = trend
            
            # Overall performance analysis
            overall_trend = self._analyze_overall_performance_trend(df)
            
            # Performance predictions
            predictions = self._predict_performance_trajectories(df)
            
            return {
                "student_trends": student_trends,
                "overall_trend": overall_trend,
                "predictions": predictions,
                "performance_insights": self._generate_performance_insights(df)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing performance trajectories: {str(e)}")
            return {"error": "Failed to analyze performance trajectories"}
    
    def forecast_resource_demand(self, resource_data: List[Dict]) -> Dict[str, Any]:
        """Forecast resource demand based on historical usage"""
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(resource_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # Aggregate daily resource usage
            daily_usage = df.groupby(['date', 'resource_type']).agg({
                'usage_hours': 'sum',
                'user_count': 'sum'
            }).reset_index()
            
            # Forecast for each resource type
            forecasts = {}
            
            for resource_type in daily_usage['resource_type'].unique():
                resource_data = daily_usage[daily_usage['resource_type'] == resource_type]
                
                if len(resource_data) >= 7:  # Need at least a week of data
                    forecast = self._forecast_resource_usage(resource_data)
                    forecasts[resource_type] = forecast
            
            # Peak demand analysis
            peak_analysis = self._analyze_peak_demand(daily_usage)
            
            # Seasonal patterns
            seasonal_patterns = self._detect_resource_seasonal_patterns(daily_usage)
            
            return {
                "forecasts": forecasts,
                "peak_analysis": peak_analysis,
                "seasonal_patterns": seasonal_patterns,
                "recommendations": self._generate_resource_recommendations(forecasts)
            }
            
        except Exception as e:
            self.logger.error(f"Error forecasting resource demand: {str(e)}")
            return {"error": "Failed to forecast resource demand"}
    
    def analyze_task_completion_patterns(self, task_data: List[Dict]) -> Dict[str, Any]:
        """Analyze task completion patterns over time"""
        
        try:
            # Convert to DataFrame
            df = pd.DataFrame(task_data)
            df['created_date'] = pd.to_datetime(df['created_date'])
            df['completed_date'] = pd.to_datetime(df['completed_date'])
            
            # Calculate completion times
            df['completion_time_hours'] = (
                df['completed_date'] - df['created_date']
            ).dt.total_seconds() / 3600
            
            # Analyze completion patterns
            completion_patterns = self._analyze_completion_patterns(df)
            
            # Predict task completion times
            completion_predictions = self._predict_completion_times(df)
            
            # Efficiency analysis
            efficiency_analysis = self._analyze_task_efficiency(df)
            
            return {
                "completion_patterns": completion_patterns,
                "completion_predictions": completion_predictions,
                "efficiency_analysis": efficiency_analysis,
                "optimization_recommendations": self._generate_task_optimization_recommendations(df)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing task completion patterns: {str(e)}")
            return {"error": "Failed to analyze task completion patterns"}
    
    def _detect_trend(self, time_series: pd.Series) -> Dict[str, Any]:
        """Detect trend in time series data"""
        
        try:
            # Simple linear regression for trend detection
            X = np.arange(len(time_series)).reshape(-1, 1)
            y = time_series.values
            
            model = LinearRegression()
            model.fit(X, y)
            
            slope = model.coef_[0]
            intercept = model.intercept_
            
            # Calculate R-squared
            y_pred = model.predict(X)
            r_squared = 1 - (np.sum((y - y_pred) ** 2) / np.sum((y - np.mean(y)) ** 2))
            
            return {
                "slope": slope,
                "intercept": intercept,
                "r_squared": r_squared,
                "trend_strength": "strong" if abs(slope) > 0.01 else "weak",
                "trend_direction": "increasing" if slope > 0 else "decreasing"
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting trend: {str(e)}")
            return {"error": "Failed to detect trend"}
    
    def _detect_seasonal_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Detect seasonal patterns in time series data"""
        
        try:
            # Weekly patterns
            df['weekday'] = df['date'].dt.dayofweek
            weekly_patterns = df.groupby('weekday')['attendance_rate'].mean()
            
            # Monthly patterns
            df['month'] = df['date'].dt.month
            monthly_patterns = df.groupby('month')['attendance_rate'].mean()
            
            # Identify peak and low periods
            peak_day = weekly_patterns.idxmax()
            low_day = weekly_patterns.idxmin()
            
            return {
                "weekly_patterns": weekly_patterns.to_dict(),
                "monthly_patterns": monthly_patterns.to_dict(),
                "peak_day": peak_day,
                "low_day": low_day,
                "seasonality_strength": self._calculate_seasonality_strength(weekly_patterns)
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting seasonal patterns: {str(e)}")
            return {"error": "Failed to detect seasonal patterns"}
    
    def _predict_future_attendance(self, df: pd.DataFrame, days_ahead: int = 7) -> Dict[str, Any]:
        """Predict future attendance rates"""
        
        try:
            # Prepare features for prediction
            df['day_of_week'] = df['date'].dt.dayofweek
            df['month'] = df['date'].dt.month
            df['day_of_month'] = df['date'].dt.day
            
            # Create lag features
            df['attendance_lag1'] = df['attendance_rate'].shift(1)
            df['attendance_lag7'] = df['attendance_rate'].shift(7)
            
            # Remove NaN values
            df = df.dropna()
            
            if len(df) < 10:  # Need sufficient data
                return {"error": "Insufficient data for prediction"}
            
            # Prepare features and target
            features = ['day_of_week', 'month', 'day_of_month', 'attendance_lag1', 'attendance_lag7']
            X = df[features]
            y = df['attendance_rate']
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Generate future dates
            last_date = df['date'].max()
            future_dates = pd.date_range(start=last_date + timedelta(days=1), periods=days_ahead)
            
            # Make predictions
            predictions = []
            for date in future_dates:
                features_pred = [
                    date.dayofweek,
                    date.month,
                    date.day,
                    df['attendance_rate'].iloc[-1],  # lag1
                    df['attendance_rate'].iloc[-7] if len(df) >= 7 else df['attendance_rate'].iloc[-1]  # lag7
                ]
                pred = model.predict([features_pred])[0]
                predictions.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'predicted_attendance': max(0, min(1, pred)),  # Clamp between 0 and 1
                    'confidence': 0.8  # Placeholder confidence
                })
            
            return {
                "predictions": predictions,
                "model_accuracy": model.score(X, y),
                "prediction_horizon": days_ahead
            }
            
        except Exception as e:
            self.logger.error(f"Error predicting future attendance: {str(e)}")
            return {"error": "Failed to predict future attendance"}
    
    def _detect_anomalies(self, time_series: pd.Series) -> List[Dict[str, Any]]:
        """Detect anomalies in time series data"""
        
        try:
            # Simple anomaly detection using z-score
            mean = time_series.mean()
            std = time_series.std()
            
            anomalies = []
            threshold = 2  # 2 standard deviations
            
            for i, value in enumerate(time_series):
                z_score = abs((value - mean) / std)
                
                if z_score > threshold:
                    anomalies.append({
                        'index': i,
                        'value': value,
                        'z_score': z_score,
                        'severity': 'high' if z_score > 3 else 'medium'
                    })
            
            return anomalies
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {str(e)}")
            return []
    
    def _analyze_student_trend(self, student_data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze individual student performance trend"""
        
        try:
            # Calculate trend
            X = np.arange(len(student_data)).reshape(-1, 1)
            y = student_data['grade'].values
            
            model = LinearRegression()
            model.fit(X, y)
            
            slope = model.coef_[0]
            
            # Calculate performance volatility
            volatility = student_data['grade'].std()
            
            # Determine trend category
            if slope > 0.1:
                trend_category = "improving"
            elif slope < -0.1:
                trend_category = "declining"
            else:
                trend_category = "stable"
            
            return {
                "slope": slope,
                "trend_category": trend_category,
                "volatility": volatility,
                "average_grade": student_data['grade'].mean(),
                "grade_range": {
                    "min": student_data['grade'].min(),
                    "max": student_data['grade'].max()
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing student trend: {str(e)}")
            return {"error": "Failed to analyze student trend"}
    
    def _calculate_seasonality_strength(self, weekly_patterns: pd.Series) -> str:
        """Calculate strength of seasonality"""
        
        try:
            # Calculate coefficient of variation
            cv = weekly_patterns.std() / weekly_patterns.mean()
            
            if cv > 0.2:
                return "strong"
            elif cv > 0.1:
                return "moderate"
            else:
                return "weak"
                
        except Exception:
            return "unknown" 