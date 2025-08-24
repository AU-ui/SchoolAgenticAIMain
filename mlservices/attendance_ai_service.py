# ============================================================================
# SMART ATTENDANCE AI/ML SERVICE
# ============================================================================
# AI-powered attendance prediction and analysis
# Features: Pattern recognition, risk assessment, predictive analytics
# ============================================================================

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import json
from datetime import datetime, timedelta
import psycopg2
from psycopg2.extras import RealDictCursor
import warnings
warnings.filterwarnings('ignore')

class AttendanceAIService:
    def __init__(self, db_config=None):
        """
        Initialize the AI service with database connection
        """
        self.db_config = db_config or {
            'host': 'localhost',
            'database': 'school_management',
            'user': 'postgres',
            'password': '1234',
            'port': 5432
        }
        
        # Initialize models
        self.attendance_predictor = None
        self.risk_detector = None
        self.scaler = StandardScaler()
        
        # Load pre-trained models if they exist
        self.load_models()
    
    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def load_models(self):
        """Load pre-trained models from disk"""
        try:
            self.attendance_predictor = joblib.load('models/attendance_predictor.pkl')
            self.risk_detector = joblib.load('models/risk_detector.pkl')
            self.scaler = joblib.load('models/scaler.pkl')
            print("✅ Models loaded successfully")
        except FileNotFoundError:
            print("⚠️ No pre-trained models found. Will train new models.")
            self.train_models()
    
    def save_models(self):
        """Save trained models to disk"""
        try:
            joblib.dump(self.attendance_predictor, 'models/attendance_predictor.pkl')
            joblib.dump(self.risk_detector, 'models/risk_detector.pkl')
            joblib.dump(self.scaler, 'models/scaler.pkl')
            print("✅ Models saved successfully")
        except Exception as e:
            print(f"❌ Error saving models: {e}")
    
    def get_attendance_data(self, student_id=None, class_id=None, days=90):
        """
        Fetch attendance data from database
        """
        conn = self.connect_db()
        if not conn:
            return pd.DataFrame()
        
        try:
            query = """
                SELECT 
                    ar.student_id,
                    ar.status,
                    ar.created_at,
                    as.session_date,
                    as.session_time,
                    as.session_type,
                    c.name as class_name,
                    EXTRACT(DOW FROM as.session_date) as day_of_week,
                    EXTRACT(MONTH FROM as.session_date) as month,
                    EXTRACT(YEAR FROM as.session_date) as year
                FROM attendance_records ar
                JOIN attendance_sessions as ON ar.session_id = as.session_id
                JOIN classes c ON as.class_id = c.id
                WHERE as.session_date >= CURRENT_DATE - INTERVAL '%s days'
            """
            
            params = [days]
            
            if student_id:
                query += " AND ar.student_id = %s"
                params.append(student_id)
            
            if class_id:
                query += " AND as.class_id = %s"
                params.append(class_id)
            
            query += " ORDER BY as.session_date, as.session_time"
            
            df = pd.read_sql_query(query, conn, params=params)
            return df
            
        except Exception as e:
            print(f"❌ Error fetching attendance data: {e}")
            return pd.DataFrame()
        finally:
            conn.close()
    
    def prepare_features(self, df):
        """
        Prepare features for ML models
        """
        if df.empty:
            return pd.DataFrame()
        
        # Convert status to numeric
        status_map = {'present': 1, 'absent': 0, 'late': 0.5, 'excused': 0.8}
        df['status_numeric'] = df['status'].map(status_map)
        
        # Create time-based features
        df['hour'] = pd.to_datetime(df['session_time']).dt.hour
        df['is_morning'] = (df['hour'] < 12).astype(int)
        df['is_afternoon'] = ((df['hour'] >= 12) & (df['hour'] < 17)).astype(int)
        df['is_evening'] = (df['hour'] >= 17).astype(int)
        
        # Create day-of-week features
        df['is_monday'] = (df['day_of_week'] == 1).astype(int)
        df['is_friday'] = (df['day_of_week'] == 5).astype(int)
        df['is_weekend'] = (df['day_of_week'].isin([6, 0])).astype(int)
        
        # Create session type features
        df['is_regular'] = (df['session_type'] == 'regular').astype(int)
        df['is_exam'] = (df['session_type'] == 'exam').astype(int)
        
        # Create rolling averages
        df = df.sort_values(['student_id', 'session_date', 'session_time'])
        df['attendance_7d'] = df.groupby('student_id')['status_numeric'].rolling(7, min_periods=1).mean().reset_index(0, drop=True)
        df['attendance_30d'] = df.groupby('student_id')['status_numeric'].rolling(30, min_periods=1).mean().reset_index(0, drop=True)
        
        # Create lag features
        df['status_lag1'] = df.groupby('student_id')['status_numeric'].shift(1)
        df['status_lag2'] = df.groupby('student_id')['status_numeric'].shift(2)
        df['status_lag3'] = df.groupby('student_id')['status_numeric'].shift(3)
        
        # Fill NaN values
        df = df.fillna(0)
        
        return df
    
    def train_models(self):
        """
        Train the ML models
        """
        print("�� Training ML models...")
        
        # Get training data
        df = self.get_attendance_data(days=365)  # Use 1 year of data
        if df.empty:
            print("❌ No training data available")
            return
        
        # Prepare features
        df = self.prepare_features(df)
        if df.empty:
            print("❌ Error preparing features")
            return
        
        # Select features for training
        feature_columns = [
            'day_of_week', 'month', 'year', 'hour',
            'is_morning', 'is_afternoon', 'is_evening',
            'is_monday', 'is_friday', 'is_weekend',
            'is_regular', 'is_exam',
            'attendance_7d', 'attendance_30d',
            'status_lag1', 'status_lag2', 'status_lag3'
        ]
        
        X = df[feature_columns]
        y = df['status_numeric']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train attendance predictor
        self.attendance_predictor = RandomForestClassifier(n_estimators=100, random_state=42)
        self.attendance_predictor.fit(X_train_scaled, y_train)
        
        # Train risk detector (anomaly detection)
        self.risk_detector = IsolationForest(contamination=0.1, random_state=42)
        self.risk_detector.fit(X_train_scaled)
        
        # Evaluate models
        y_pred = self.attendance_predictor.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Models trained successfully")
        print(f"�� Attendance Predictor Accuracy: {accuracy:.2%}")
        
        # Save models
        self.save_models()
    
    def predict_attendance(self, student_id, days_ahead=7):
        """
        Predict attendance for a student
        """
        if self.attendance_predictor is None:
            print("❌ Model not trained")
            return None
        
        # Get recent attendance data
        df = self.get_attendance_data(student_id=student_id, days=30)
        if df.empty:
            return None
        
        # Prepare features
        df = self.prepare_features(df)
        if df.empty:
            return None
        
        # Get latest features
        latest_features = df.iloc[-1:][[
            'day_of_week', 'month', 'year', 'hour',
            'is_morning', 'is_afternoon', 'is_evening',
            'is_monday', 'is_friday', 'is_weekend',
            'is_regular', 'is_exam',
            'attendance_7d', 'attendance_30d',
            'status_lag1', 'status_lag2', 'status_lag3'
        ]]
        
        # Scale features
        latest_features_scaled = self.scaler.transform(latest_features)
        
        # Make prediction
        prediction = self.attendance_predictor.predict(latest_features_scaled)[0]
        probability = self.attendance_predictor.predict_proba(latest_features_scaled)[0]
        
        # Calculate risk score
        risk_score = self.risk_detector.decision_function(latest_features_scaled)[0]
        
        return {
            'predicted_attendance': float(prediction),
            'attendance_probability': float(probability[1] if len(probability) > 1 else probability[0]),
            'risk_score': float(risk_score),
            'risk_level': 'high' if risk_score < -0.5 else 'medium' if risk_score < 0 else 'low',
            'confidence': float(max(probability))
        }
    
    def analyze_patterns(self, student_id=None, class_id=None):
        """
        Analyze attendance patterns
        """
        df = self.get_attendance_data(student_id=student_id, class_id=class_id, days=90)
        if df.empty:
            return None
        
        # Basic statistics
        total_sessions = len(df)
        present_count = len(df[df['status'] == 'present'])
        absent_count = len(df[df['status'] == 'absent'])
        late_count = len(df[df['status'] == 'late'])
        excused_count = len(df[df['status'] == 'excused'])
        
        attendance_rate = present_count / total_sessions if total_sessions > 0 else 0
        
        # Day-of-week analysis
        day_analysis = df.groupby('day_of_week')['status'].apply(
            lambda x: (x == 'present').sum() / len(x) * 100
        ).to_dict()
        
        # Time-of-day analysis
        df['hour'] = pd.to_datetime(df['session_time']).dt.hour
        time_analysis = df.groupby('hour')['status'].apply(
            lambda x: (x == 'present').sum() / len(x) * 100
        ).to_dict()
        
        # Trend analysis (last 30 days vs previous 30 days)
        df['session_date'] = pd.to_datetime(df['session_date'])
        recent_30 = df[df['session_date'] >= datetime.now() - timedelta(days=30)]
        previous_30 = df[(df['session_date'] >= datetime.now() - timedelta(days=60)) & 
                        (df['session_date'] < datetime.now() - timedelta(days=30))]
        
        recent_rate = len(recent_30[recent_30['status'] == 'present']) / len(recent_30) if len(recent_30) > 0 else 0
        previous_rate = len(previous_30[previous_30['status'] == 'present']) / len(previous_30) if len(previous_30) > 0 else 0
        
        trend = 'improving' if recent_rate > previous_rate else 'declining' if recent_rate < previous_rate else 'stable'
        
        return {
            'total_sessions': total_sessions,
            'present_count': present_count,
            'absent_count': absent_count,
            'late_count': late_count,
            'excused_count': excused_count,
            'attendance_rate': attendance_rate,
            'day_analysis': day_analysis,
            'time_analysis': time_analysis,
            'trend': trend,
            'recent_rate': recent_rate,
            'previous_rate': previous_rate
        }
    
    def get_risk_students(self, class_id=None, threshold=0.7):
        """
        Identify students at risk of poor attendance
        """
        conn = self.connect_db()
        if not conn:
            return []
        
        try:
            # Get all students in the class
            query = """
                SELECT DISTINCT u.id, u.first_name, u.last_name, u.email
                FROM users u
                JOIN students s ON u.id = s.user_id
                WHERE u.role = 'student'
            """
            
            if class_id:
                query += " AND s.class_id = %s"
                params = [class_id]
            else:
                params = []
            
            students_df = pd.read_sql_query(query, conn, params=params)
            
            risk_students = []
            
            for _, student in students_df.iterrows():
                prediction = self.predict_attendance(student['id'])
                if prediction and prediction['attendance_probability'] < threshold:
                    risk_students.append({
                        'student_id': student['id'],
                        'name': f"{student['first_name']} {student['last_name']}",
                        'email': student['email'],
                        'risk_score': prediction['risk_score'],
                        'attendance_probability': prediction['attendance_probability'],
                        'risk_level': prediction['risk_level']
                    })
            
            # Sort by risk score
            risk_students.sort(key=lambda x: x['risk_score'])
            
            return risk_students
            
        except Exception as e:
            print(f"❌ Error getting risk students: {e}")
            return []
        finally:
            conn.close()

# ============================================================================
# FLASK API ENDPOINTS
# ============================================================================

from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize AI service
ai_service = AttendanceAIService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'attendance_ai_service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/predict/<int:student_id>', methods=['GET'])
def predict_attendance(student_id):
    """Predict attendance for a student"""
    try:
        days_ahead = request.args.get('days_ahead', 7, type=int)
        prediction = ai_service.predict_attendance(student_id, days_ahead)
        
        if prediction:
            return jsonify({
                'success': True,
                'data': prediction
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No data available for prediction'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/analyze', methods=['GET'])
def analyze_patterns():
    """Analyze attendance patterns"""
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
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@app.route('/risk-students', methods=['GET'])
def get_risk_students():
    """Get students at risk"""
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
    """Retrain the ML models"""
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
    print("🚀 Starting Attendance AI Service...")
    print("📊 Available endpoints:")
    print("  - GET  /health")
    print("  - GET  /predict/<student_id>")
    print("  - GET  /analyze")
    print("  - GET  /risk-students")
    print("  - POST /train")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
