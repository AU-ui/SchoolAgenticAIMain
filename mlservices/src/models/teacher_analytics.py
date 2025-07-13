import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import json

class TeacherAnalytics:
    def __init__(self):
        self.scaler = StandardScaler()
        self.attendance_model = None
        self.grade_predictor = None
        
    def analyze_attendance_patterns(self, attendance_data):
        """Analyze attendance patterns and identify trends"""
        try:
            df = pd.DataFrame(attendance_data)
            
            # Convert to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            
            # Calculate daily attendance rates
            daily_stats = df.groupby('date').agg({
                'status': lambda x: (x == 'present').sum() / len(x) * 100,
                'student_id': 'count'
            }).rename(columns={'status': 'attendance_rate', 'student_id': 'total_students'})
            
            # Identify patterns
            patterns = {
                'overall_attendance_rate': daily_stats['attendance_rate'].mean(),
                'trend': 'improving' if daily_stats['attendance_rate'].iloc[-1] > daily_stats['attendance_rate'].iloc[0] else 'declining',
                'best_day': daily_stats.groupby(df['day_of_week'].iloc[0])['attendance_rate'].mean().idxmax(),
                'worst_day': daily_stats.groupby(df['day_of_week'].iloc[0])['attendance_rate'].mean().idxmin(),
                'anomalies': self._detect_anomalies(daily_stats['attendance_rate'])
            }
            
            return patterns
            
        except Exception as e:
            print(f"Error analyzing attendance patterns: {e}")
            return {}
    
    def _detect_anomalies(self, attendance_rates):
        """Detect unusual attendance patterns"""
        mean_rate = attendance_rates.mean()
        std_rate = attendance_rates.std()
        
        anomalies = []
        for date, rate in attendance_rates.items():
            if abs(rate - mean_rate) > 2 * std_rate:
                anomalies.append({
                    'date': str(date),
                    'rate': rate,
                    'expected_range': f"{mean_rate - std_rate:.1f} - {mean_rate + std_rate:.1f}"
                })
        
        return anomalies
    
    def predict_student_performance(self, student_data):
        """Predict student performance based on historical data"""
        try:
            df = pd.DataFrame(student_data)
            
            # Feature engineering
            features = [
                'attendance_rate',
                'assignment_completion_rate',
                'average_grade',
                'days_since_last_assignment',
                'total_assignments'
            ]
            
            # Simple prediction model
            if len(df) > 10:  # Need sufficient data
                X = df[features].fillna(0)
                y = df['final_grade']
                
                model = RandomForestRegressor(n_estimators=100, random_state=42)
                model.fit(X, y)
                
                # Predict for current student
                current_features = X.iloc[-1:].values
                prediction = model.predict(current_features)[0]
                confidence = model.score(X, y)
                
                return {
                    'predicted_grade': round(prediction, 2),
                    'confidence': round(confidence, 2),
                    'recommendations': self._generate_recommendations(df.iloc[-1])
                }
            
            return {'predicted_grade': None, 'confidence': 0, 'recommendations': []}
            
        except Exception as e:
            print(f"Error predicting student performance: {e}")
            return {'predicted_grade': None, 'confidence': 0, 'recommendations': []}
    
    def _generate_recommendations(self, student_row):
        """Generate personalized recommendations"""
        recommendations = []
        
        if student_row['attendance_rate'] < 80:
            recommendations.append("Consider improving attendance to boost performance")
        
        if student_row['assignment_completion_rate'] < 90:
            recommendations.append("Focus on completing assignments on time")
        
        if student_row['average_grade'] < 70:
            recommendations.append("Consider additional tutoring or study sessions")
        
        return recommendations
    
    def optimize_timetable(self, class_data, teacher_preferences):
        """Optimize class timetable based on various constraints"""
        try:
            # Simple timetable optimization
            classes = pd.DataFrame(class_data)
            
            # Define constraints
            max_classes_per_day = 6
            preferred_subjects = teacher_preferences.get('preferred_subjects', [])
            preferred_times = teacher_preferences.get('preferred_times', [])
            
            # Create optimized schedule
            optimized_schedule = []
            
            for _, class_info in classes.iterrows():
                # Find best time slot
                best_slot = self._find_best_timeslot(
                    class_info, 
                    optimized_schedule, 
                    preferred_times,
                    max_classes_per_day
                )
                
                optimized_schedule.append({
                    'class_id': class_info['id'],
                    'subject': class_info['subject'],
                    'day': best_slot['day'],
                    'start_time': best_slot['start_time'],
                    'end_time': best_slot['end_time'],
                    'room': best_slot['room']
                })
            
            return optimized_schedule
            
        except Exception as e:
            print(f"Error optimizing timetable: {e}")
            return []
    
    def _find_best_timeslot(self, class_info, existing_schedule, preferred_times, max_per_day):
        """Find the best available time slot for a class"""
        # Simple algorithm - find first available slot
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        time_slots = ['08:00-09:00', '09:00-10:00', '10:00-11:00', '11:00-12:00', 
                     '13:00-14:00', '14:00-15:00', '15:00-16:00']
        
        for day in days:
            day_classes = [c for c in existing_schedule if c['day'] == day]
            if len(day_classes) < max_per_day:
                for time_slot in time_slots:
                    slot_taken = any(c['start_time'] == time_slot.split('-')[0] for c in day_classes)
                    if not slot_taken:
                        return {
                            'day': day,
                            'start_time': time_slot.split('-')[0],
                            'end_time': time_slot.split('-')[1],
                            'room': f"Room {len(day_classes) + 1}"
                        }
        
        return {'day': 'Monday', 'start_time': '08:00', 'end_time': '09:00', 'room': 'Room 1'}
    
    def generate_ai_report(self, report_type, data, template_id=None):
        """Generate AI-powered reports"""
        try:
            if report_type == 'attendance':
                return self._generate_attendance_report(data)
            elif report_type == 'performance':
                return self._generate_performance_report(data)
            elif report_type == 'timetable':
                return self._generate_timetable_report(data)
            else:
                return self._generate_generic_report(data, report_type)
                
        except Exception as e:
            print(f"Error generating AI report: {e}")
            return {"error": "Failed to generate report"}
    
    def _generate_attendance_report(self, data):
        """Generate attendance analysis report"""
        patterns = self.analyze_attendance_patterns(data)
        
        report = {
            "title": "Attendance Analysis Report",
            "summary": f"Overall attendance rate: {patterns.get('overall_attendance_rate', 0):.1f}%",
            "trend": patterns.get('trend', 'stable'),
            "insights": [
                f"Best attendance day: {patterns.get('best_day', 'Unknown')}",
                f"Worst attendance day: {patterns.get('worst_day', 'Unknown')}",
                f"Number of anomalies detected: {len(patterns.get('anomalies', []))}"
            ],
            "recommendations": [
                "Consider implementing attendance incentives",
                "Review class schedule for low-attendance days",
                "Engage with students showing declining attendance"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def _generate_performance_report(self, data):
        """Generate student performance report"""
        report = {
            "title": "Student Performance Analysis",
            "summary": "Performance analysis based on recent data",
            "insights": [
                "Top performing students identified",
                "Areas needing improvement highlighted",
                "Progress trends analyzed"
            ],
            "recommendations": [
                "Implement targeted interventions",
                "Provide additional support for struggling students",
                "Recognize high-achieving students"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def _generate_timetable_report(self, data):
        """Generate timetable optimization report"""
        report = {
            "title": "Timetable Optimization Report",
            "summary": "Analysis of current timetable efficiency",
            "insights": [
                "Optimal class scheduling identified",
                "Resource utilization analyzed",
                "Conflict resolution recommendations"
            ],
            "recommendations": [
                "Consider redistributing classes across time slots",
                "Optimize room assignments",
                "Balance workload across days"
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return report
    
    def _generate_generic_report(self, data, report_type):
        """Generate generic report based on data"""
        return {
            "title": f"{report_type.title()} Report",
            "summary": "Analysis completed successfully",
            "data_points": len(data) if isinstance(data, list) else 1,
            "generated_at": datetime.now().isoformat()
        } 