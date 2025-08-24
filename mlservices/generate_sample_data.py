# ============================================================================
# GENERATE SAMPLE ATTENDANCE DATA FOR ML TRAINING
# ============================================================================

import psycopg2
import random
from datetime import datetime, timedelta

def generate_sample_data():
    """Generate sample attendance data for ML training"""
    
    print("🚀 Generating sample attendance data...")
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='edtech_platform',
            user='postgres',
            password='4321'
        )
        
        cursor = conn.cursor()
        
        # Check if we have basic data
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
        student_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM classes")
        class_count = cursor.fetchone()[0]
        
        print(f"📊 Found {student_count} students and {class_count} classes")
        
        if student_count == 0 or class_count == 0:
            print("⚠️  Need to create basic users and classes first")
            return
        
        # Generate 30 days of attendance data
        start_date = datetime.now() - timedelta(days=30)
        
        for day in range(30):
            current_date = start_date + timedelta(days=day)
            
            # Skip weekends
            if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                continue
                
            # Create attendance session
            cursor.execute("""
                INSERT INTO attendance_sessions 
                (class_id, teacher_id, session_date, session_time, session_type, status)
                VALUES (1, 1, %s, '09:00:00', 'regular', 'completed')
                RETURNING session_id
            """, (current_date.date(),))
            
            session_id = cursor.fetchone()[0]
            
            # Generate attendance records for students
            for student_id in range(1, min(student_count + 1, 6)):  # Up to 5 students
                # Weighted random: 85% present, 10% absent, 5% late
                status = random.choices(['present', 'absent', 'late'], weights=[0.85, 0.10, 0.05])[0]
                
                cursor.execute("""
                    INSERT INTO attendance_records 
                    (session_id, student_id, status, marked_by)
                    VALUES (%s, %s, %s, 1)
                """, (session_id, student_id, status))
        
        conn.commit()
        print("✅ Generated 30 days of sample attendance data!")
        print("📈 Data includes present/absent/late patterns for ML training")
        
    except Exception as e:
        print(f"❌ Error generating data: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    generate_sample_data()
