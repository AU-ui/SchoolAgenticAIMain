import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from datetime import datetime, timedelta
import json

class ParentAnalytics:
    def __init__(self):
        self.scaler = StandardScaler()
        self.engagement_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.response_time_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.channel_preference_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.label_encoder = LabelEncoder()
        
    def optimize_communication_strategy(self, parent_data):
        """Optimize communication strategy for a parent"""
        try:
            # Analyze parent engagement patterns
            engagement_score = self._calculate_engagement_score(parent_data)
            optimal_channel = self._predict_optimal_channel(parent_data)
            optimal_time = self._predict_optimal_time(parent_data)
            message_frequency = self._calculate_optimal_frequency(parent_data)
            
            strategy = {
                "engagement_score": engagement_score,
                "optimal_channel": optimal_channel,
                "optimal_time": optimal_time,
                "message_frequency": message_frequency,
                "personalization_level": self._determine_personalization_level(parent_data),
                "recommendations": self._generate_communication_recommendations(parent_data)
            }
            
            return strategy
            
        except Exception as e:
            print(f"Error optimizing communication strategy: {e}")
            return {}
    
    def _calculate_engagement_score(self, parent_data):
        """Calculate overall engagement score for a parent"""
        factors = {
            'response_rate': parent_data.get('response_rate', 0) * 0.4,
            'response_time': max(0, 1 - (parent_data.get('response_time', 24) / 24)) * 0.3,
            'read_rate': parent_data.get('read_rate', 0) * 0.3
        }
        
        return sum(factors.values())
    
    def _predict_optimal_channel(self, parent_data):
        """Predict the optimal communication channel for a parent"""
        channels = ['email', 'sms', 'notification', 'phone']
        
        # Simple rule-based prediction (in real implementation, use ML model)
        if parent_data.get('response_rate', 0) > 0.8:
            return 'email'
        elif parent_data.get('response_time', 24) < 2:
            return 'sms'
        elif parent_data.get('read_rate', 0) > 0.9:
            return 'notification'
        else:
            return 'phone'
    
    def _predict_optimal_time(self, parent_data):
        """Predict optimal time to send messages"""
        # Analyze historical response patterns
        preferred_time = parent_data.get('preferred_time', '09:00')
        
        # Adjust based on engagement patterns
        if parent_data.get('response_time', 24) < 1:
            return preferred_time
        elif parent_data.get('response_rate', 0) > 0.7:
            return "08:00"  # Early morning for engaged parents
        else:
            return "18:00"  # Evening for less engaged parents
    
    def _calculate_optimal_frequency(self, parent_data):
        """Calculate optimal message frequency"""
        engagement_score = self._calculate_engagement_score(parent_data)
        
        if engagement_score > 0.8:
            return "daily"
        elif engagement_score > 0.6:
            return "weekly"
        elif engagement_score > 0.4:
            return "bi-weekly"
        else:
            return "monthly"
    
    def _determine_personalization_level(self, parent_data):
        """Determine the level of personalization needed"""
        engagement_score = self._calculate_engagement_score(parent_data)
        
        if engagement_score > 0.7:
            return "high"
        elif engagement_score > 0.4:
            return "medium"
        else:
            return "low"
    
    def _generate_communication_recommendations(self, parent_data):
        """Generate personalized communication recommendations"""
        recommendations = []
        engagement_score = self._calculate_engagement_score(parent_data)
        
        if engagement_score < 0.5:
            recommendations.append("Consider phone calls for urgent matters")
            recommendations.append("Send follow-up reminders for important messages")
            recommendations.append("Use multiple channels to ensure message delivery")
        
        if parent_data.get('response_time', 24) > 12:
            recommendations.append("Send messages during peak engagement hours")
            recommendations.append("Use shorter, more direct messages")
        
        if parent_data.get('read_rate', 0) < 0.7:
            recommendations.append("Use attention-grabbing subject lines")
            recommendations.append("Include clear call-to-action in messages")
        
        return recommendations
    
    def generate_parent_insights(self, parent_id):
        """Generate comprehensive insights for a parent"""
        try:
            # Mock data - in real implementation, fetch from database
            insights = {
                "engagement_metrics": {
                    "overall_score": 0.75,
                    "response_rate": 0.82,
                    "average_response_time": 2.5,
                    "preferred_channel": "email",
                    "peak_activity_hours": "09:00-11:00"
                },
                "communication_patterns": {
                    "most_responsive_day": "Tuesday",
                    "least_responsive_day": "Friday",
                    "preferred_message_length": "medium",
                    "response_to_urgency": "high"
                },
                "personalization_insights": {
                    "responds_best_to": "Personalized messages with student names",
                    "avoids": "Generic mass communications",
                    "engagement_triggers": ["Academic progress", "Behavioral updates", "Event reminders"]
                },
                "recommendations": [
                    "Send academic updates on Tuesday mornings",
                    "Use email for detailed communications",
                    "Include student-specific examples in messages",
                    "Follow up on urgent matters within 2 hours"
                ]
            }
            
            return insights
            
        except Exception as e:
            print(f"Error generating parent insights: {e}")
            return {}
    
    def schedule_smart_notifications(self, parent_data):
        """Schedule notifications at optimal times for maximum engagement"""
        try:
            engagement_score = self._calculate_engagement_score(parent_data)
            optimal_channel = self._predict_optimal_channel(parent_data)
            optimal_time = self._predict_optimal_time(parent_data)
            
            schedule = {
                "optimal_send_times": {
                    "academic_updates": optimal_time,
                    "behavioral_alerts": "immediate",
                    "event_reminders": "09:00",
                    "progress_reports": "10:00"
                },
                "channel_strategy": {
                    "urgent": "sms",
                    "important": optimal_channel,
                    "informational": "notification"
                },
                "frequency_limits": {
                    "daily_max": 3 if engagement_score > 0.7 else 1,
                    "weekly_max": 10 if engagement_score > 0.7 else 3,
                    "monthly_max": 30 if engagement_score > 0.7 else 8
                },
                "personalization_rules": {
                    "include_student_name": True,
                    "customize_greeting": engagement_score > 0.6,
                    "add_personal_notes": engagement_score > 0.8
                }
            }
            
            return schedule
            
        except Exception as e:
            print(f"Error scheduling smart notifications: {e}")
            return {}
    
    def analyze_communication_effectiveness(self, communication_history):
        """Analyze the effectiveness of past communications"""
        try:
            df = pd.DataFrame(communication_history)
            
            if df.empty:
                return {}
            
            # Calculate effectiveness metrics
            effectiveness = {
                "response_rate": (df['responded'] == True).mean() if 'responded' in df.columns else 0,
                "average_response_time": df['response_time'].mean() if 'response_time' in df.columns else 0,
                "read_rate": (df['read'] == True).mean() if 'read' in df.columns else 0,
                "channel_effectiveness": df.groupby('channel')['responded'].mean().to_dict() if 'channel' in df.columns else {},
                "time_effectiveness": df.groupby('send_hour')['responded'].mean().to_dict() if 'send_hour' in df.columns else {},
                "content_effectiveness": self._analyze_content_effectiveness(df)
            }
            
            return effectiveness
            
        except Exception as e:
            print(f"Error analyzing communication effectiveness: {e}")
            return {}
    
    def _analyze_content_effectiveness(self, df):
        """Analyze which content types are most effective"""
        if 'content_type' not in df.columns or 'responded' not in df.columns:
            return {}
        
        return df.groupby('content_type')['responded'].mean().to_dict() 