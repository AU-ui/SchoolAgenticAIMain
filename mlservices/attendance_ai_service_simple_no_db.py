# ============================================================================
# SMART ATTENDANCE AI/ML SERVICE - SIMPLE VERSION (NO DATABASE)
# ============================================================================
# Works without database connection for testing
# ============================================================================

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import json
from datetime import datetime, timedelta
import warnings
import os

warnings.filterwarnings('ignore')

class AttendanceAIService:
    def __init__(self):
        """Initialize the AI service without database"""
        print("�� Initializing Smart Attendance AI Service (No Database Mode)")
        
        # Initialize models
        self.attendance_predictor = None
        self.scaler = StandardScaler()
        
        # Create sample data for testing
        self.create_sample_data()
        
        # Train models with sample data
        self.train_models()
    
    def create_sample_data(self):
        """Create sample attendance data for testing"""
        print("📊 Creating sample attendance data...")
        
        # Generate sample data
        np.random.seed(42)
        n_students = 50
        n_days = 30
        
        data = []
        for student_id in range(1, n_students + 1):
            for day in range(n_days):
                # Realistic attendance patterns
                if np.random.random() < 0.85:  # 85% attendance rate
                    status = 'present'
                elif np.random.random() < 0.7:  # 70% of absences are excused
                    status = 'excused'
                else:
                    status = 'absent'
                
                data.append({
                    'student_id': student_id,
                    'status': status,
                    'day_of_week': (day % 7) + 1,
                    'hour': 9,
                    'is_morning': 1,
                    'is_monday': 1 if (day % 7) == 0 else 0,
                    'is_friday': 1 if (day % 7) == 4 else 0
                })
        
        self.sample_data = pd.DataFrame(data)
        print(f"✅ Created {len(data)} sample attendance records")
    
    def prepare_features(self, df):
        """Prepare features for ML models"""
        # Convert status to numeric
        status_map = {'present': 1, 'absent': 0, 'late': 0.5, 'excused': 0.5}
        df['status_numeric'] = df['status'].map(status_map)
        
        # Rolling averages
        df['attendance_7d'] = df.groupby('student_id')['status_numeric'].rolling(7).mean().reset_index(0, drop=True)
        df['attendance_30d'] = df.groupby('student_id')['status_numeric'].rolling(30).mean().reset_index(0, drop=True)
        
        # Lag features
        df['status_lag1'] = df.groupby('student_id')['status_numeric'].shift(1)
        df['status_lag2'] = df.groupby('student_id')['status_numeric'].shift(2)
        
        return df
    
    def train_models(self):
        """Train ML models on sample data"""
        print("�� Training ML models with sample data...")
        
        # Prepare features
        df = self.prepare_features(self.sample_data)
        df = df.dropna()
        
        # Features for prediction
        feature_cols = ['hour', 'is_morning', 'is_monday', 'is_friday', 
                       'attendance_7d', 'attendance_30d', 'status_lag1', 'status_lag2']
        
        X = df[feature_cols]
        y = df['status_numeric']
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train attendance predictor
        self.attendance_predictor = RandomForestClassifier(n_estimators=100, random_state=42)
        self.attendance_predictor.fit(X_scaled, y)
        
        print("✅ Models trained successfully!")
    
    def predict_attendance(self, student_id, days_ahead=7):
        """Predict attendance for a student"""
        if self.attendance_predictor is None:
            return None
        
        # Get sample data for the student
        student_data = self.sample_data[self.sample_data['student_id'] == student_id]
        
        if student_data.empty:
            return None
        
        # Prepare features
        df = self.prepare_features(student_data)
        
        if df.empty:
            return None
        
        # Get latest features
        latest_features = df[['hour', 'is_morning', 'is_monday', 'is_friday', 
                             'attendance_7d', 'attendance_30d', 'status_lag1', 'status_lag2']].iloc[-1:]
        
        # Scale features
        latest_scaled = self.scaler.transform(latest_features)
        
        # Make prediction
        prediction = self.attendance_predictor.predict_proba(latest_scaled)[0]
        
        return {
            'present_probability': prediction[1] if len(prediction) > 1 else 0.5,
            'absent_probability': prediction[0] if len(prediction) > 1 else 0.5,
            'confidence': max(prediction),
            'next_week_attendance': prediction[1] if len(prediction) > 1 else 0.5,
            'risk_level': 'low' if prediction[1] > 0.8 else 'medium' if prediction[1] > 0.6 else 'high',
            'pattern': 'consistent' if prediction[1] > 0.8 else 'variable',
            'recommendations': [
                'Student shows good attendance pattern',
                'Continue monitoring for consistency',
                'Consider early intervention if pattern changes'
            ]
        }
    
    def analyze_patterns(self, student_id=None, class_id=None):
        """Analyze attendance patterns"""
        if student_id:
            df = self.sample_data[self.sample_data['student_id'] == student_id]
        else:
            df = self.sample_data
        
        if df.empty:
            return None
        
        # Basic statistics
        total_sessions = len(df)
        present_count = len(df[df['status'] == 'present'])
        absent_count = len(df[df['status'] == 'absent'])
        excused_count = len(df[df['status'] == 'excused'])
        
        attendance_rate = present_count / total_sessions if total_sessions > 0 else 0
        
        return {
            'total_sessions': total_sessions,
            'present_count': present_count,
            'absent_count': absent_count,
            'excused_count': excused_count,
            'attendance_rate': attendance_rate,
            'trend': 'improving' if attendance_rate > 0.8 else 'declining' if attendance_rate < 0.7 else 'stable',
            'recommendation': 'Student attendance is good' if attendance_rate > 0.8 else 'Consider intervention',
            'risk_students': [1, 5, 12] if student_id is None else []
        }
    
    def get_risk_students(self, class_id=None, threshold=0.7):
        """Identify students at risk based on attendance patterns"""
        # Calculate attendance rates per student
        student_stats = self.sample_data.groupby('student_id').agg({
            'status': lambda x: (x == 'present').mean()
        }).reset_index()
        
        # Identify at-risk students
        at_risk = student_stats[student_stats['status'] < threshold]
        
        # Return sample risk students
        return [
            {
                'student_id': row['student_id'],
                'name': f'Student {row["student_id"]}',
                'email': f'student{row["student_id"]}@school.edu',
                'risk_level': 'high' if row['status'] < 0.5 else 'medium',
                'attendance_probability': row['status']
            }
            for _, row in at_risk.head(5).iterrows()
        ]

# ============================================================================
# FLASK API ENDPOINTS
# ============================================================================

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ai_service = AttendanceAIService()

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'message': 'Smart Attendance AI Service is running (No Database Mode)',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict/<int:student_id>', methods=['GET'])
def predict_attendance(student_id):
    try:
        prediction = ai_service.predict_attendance(student_id)
        if prediction:
            return jsonify({
                'success': True,
                'data': prediction
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No data available for prediction'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/analyze', methods=['GET'])
def analyze_patterns():
    try:
        student_id = request.args.get('student_id', type=int)
        class_id = request.args.get('class_id', type=int)
        
        analysis = ai_service.analyze_patterns(student_id, class_id)
        if analysis:
            return jsonify({
                'success': True,
                'data': analysis
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No data available for analysis'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/risk-students', methods=['GET'])
def get_risk_students():
    try:
        class_id = request.args.get('class_id', type=int)
        threshold = request.args.get('threshold', 0.7, type=float)
        
        risk_students = ai_service.get_risk_students(class_id, threshold)
        return jsonify({
            'success': True,
            'data': risk_students
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/train', methods=['POST'])
def train_models():
    try:
        ai_service.train_models()
        return jsonify({
            'success': True,
            'message': 'Models trained successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

if __name__ == '__main__':
    port = 5001
    host = '0.0.0.0'
    
    print(f"🚀 Starting Smart Attendance AI Service on {host}:{port}")
    print("📊 Using sample data (no database required)")
    app.run(host=host, port=port, debug=True)
