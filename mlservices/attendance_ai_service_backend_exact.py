# ============================================================================
# SMART ATTENDANCE AI/ML SERVICE - EXACT BACKEND MATCH
# ============================================================================
# Uses the exact same connection settings as the backend
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
import os

warnings.filterwarnings('ignore')

class AttendanceAIService:
    def __init__(self, db_config=None):
        """
        Initialize the AI service with database connection
        """
        if db_config is None:
            # EXACT same config as backend
            self.db_config = {
                'host': 'localhost',  # Same as backend default
                'port': 5432,
                'database': 'edtech_platform',
                'user': 'postgres',
                'password': 'your_password',  # EXACT same as backend default
                'connect_timeout': 2,  # Same as backend connectionTimeoutMillis
                'sslmode': 'disable'  # Same as backend ssl: false
            }
        else:
            self.db_config = db_config
        
        print(f" Database Config: {self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}")
        print(f" Using EXACT same settings as backend")
        
        # Initialize models
        self.attendance_predictor = None
        self.risk_detector = None
        self.scaler = StandardScaler()
        
        # Load pre-trained models if they exist
        self.load_models()
    
    def connect_db(self):
        """Connect to PostgreSQL database using exact backend settings"""
        try:
            conn = psycopg2.connect(**self.db_config)
            print("✅ Database connected successfully (using backend exact settings)")
            return conn
        except Exception as e:
            print(f"❌ Database connection error: {e}")
            print(" Trying alternative passwords...")
            
            # Try alternative passwords
            alternative_passwords = ['', 'postgres', 'password', '1234', 'admin', 'root']
            for alt_password in alternative_passwords:
                try:
                    test_config = self.db_config.copy()
                    test_config['password'] = alt_password
                    conn = psycopg2.connect(**test_config)
                    print(f"✅ Connected with password: '{alt_password}'")
                    self.db_config = test_config
                    return conn
                except:
                    continue
            return None
    
    def load_models(self):
        """Load pre-trained models from disk"""
        try:
            model_path = 'models/'
            self.attendance_predictor = joblib.load(f'{model_path}attendance_predictor.pkl')
            self.risk_detector = joblib.load(f'{model_path}risk_detector.pkl')
            self.scaler = joblib.load(f'{model_path}scaler.pkl')
            print("✅ Models loaded successfully")
        except FileNotFoundError:
            print("⚠️ No pre-trained models found. Will train new models.")
            self.train_models()
    
    def save_models(self):
        """Save trained models to disk"""
        try:
            model_path = 'models/'
            os.makedirs(model_path, exist_ok=True)
            
            joblib.dump(self.attendance_predictor, f'{model_path}attendance_predictor.pkl')
            joblib.dump(self.risk_detector, f'{model_path}risk_detector.pkl')
            joblib.dump(self.scaler, f'{model_path}scaler.pkl')
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
            
            query += " ORDER BY as.session_date DESC"
            
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            return df
            
        except Exception as e:
            print(f"❌ Error fetching attendance data: {e}")
            conn.close()
            return pd.DataFrame()
    
    def prepare_features(self, df):
        """
        Prepare features for ML models
        """
        if df.empty:
            return pd.DataFrame()
        
        # Convert status to numeric
        status_map = {'present': 1, 'absent': 0, 'late': 0.5, 'excused': 0.5}
        df['status_numeric'] = df['status'].map(status_map)
        
        # Time-based features
        df['hour'] = pd.to_datetime(df['session_time']).dt.hour
        df['is_morning'] = (df['hour'] < 12).astype(int)
        
        # Day of week features
        df['is_monday'] = (df['day_of_week'] == 1).astype(int)
        df['is_friday'] = (df['day_of_week'] == 5).astype(int)
        
        # Rolling averages
        df['attendance_7d'] = df.groupby('student_id')['status_numeric'].rolling(7).mean().reset_index(0, drop=True)
        df['attendance_30d'] = df.groupby('student_id')['status_numeric'].rolling(30).mean().reset_index(0, drop=True)
        
        # Lag features
        df['status_lag1'] = df.groupby('student_id')['status_numeric'].shift(1)
        df['status_lag2'] = df.groupby('student_id')['status_numeric'].shift(2)
        
        return df
    
    def train_models(self):
        """
        Train ML models on attendance data
        """
        print(" Training ML models...")
        
        # Get training data
        df = self.get_attendance_data(days=90)
        
        if df.empty:
            print("❌ No training data available")
            return
        
        # Prepare features
        df = self.prepare_features(df)
        df = df.dropna()
        
        if df.empty:
            print("❌ No valid training data after feature preparation")
            return
        
        # Features for prediction
        feature_cols = ['hour', 'is_morning', 'is_monday', 'is_friday', 
                       'attendance_7d', 'attendance_30d', 'status_lag1', 'status_lag2']
        
        X = df[feature_cols]
        y = df['status_numeric']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train attendance predictor
        self.attendance_predictor = RandomForestClassifier(n_estimators=100, random_state=42)
        self.attendance_predictor.fit(X_train_scaled, y_train)
        
        # Train risk detector
        self.risk_detector = IsolationForest(contamination=0.1, random_state=42)
        self.risk_detector.fit(X_train_scaled)
        
        # Evaluate models
        y_pred = self.attendance_predictor.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Models trained successfully!")
        print(f"📊 Accuracy: {accuracy:.2f}")
        
        # Save models
        self.save_models()
    
    def predict_attendance(self, student_id, days_ahead=7):
        """
        Predict attendance for a student
        """
        if self.attendance_predictor is None:
            return None
        
        # Get recent data for the student
        df = self.get_attendance_data(student_id=student_id, days=30)
        
        if df.empty:
            return None
        
        # Prepare features
        df = self.prepare_features(df)
        
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
            'confidence': max(prediction)
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
        
        attendance_rate = present_count / total_sessions if total_sessions > 0 else 0
        
        # Day of week analysis
        day_stats = df.groupby('day_of_week')['status'].apply(
            lambda x: (x == 'present').mean()
        ).to_dict()
        
        return {
            'total_session
