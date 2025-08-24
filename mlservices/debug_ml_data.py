# ============================================================================
# DEBUG ML SERVICE DATA ACCESS
# ============================================================================

import psycopg2
import pandas as pd

def debug_ml_data():
    """Debug why ML service can't find attendance data"""
    
    print("🔍 Debugging ML service data access...")
    
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
        
        # Check attendance tables
        print("\n📊 Checking attendance tables...")
        
        cursor.execute("SELECT COUNT(*) FROM attendance_sessions")
        session_count = cursor.fetchone()[0]
        print(f"✅ Attendance sessions: {session_count}")
        
        cursor.execute("SELECT COUNT(*) FROM attendance_records")
        record_count = cursor.fetchone()[0]
        print(f"✅ Attendance records: {record_count}")
        
        # Check sample data
        print("\n📋 Sample attendance sessions:")
        cursor.execute("""
            SELECT session_id, class_id, teacher_id, session_date, session_time, session_type, status
            FROM attendance_sessions 
            ORDER BY session_date DESC 
            LIMIT 5
        """)
        
        sessions = cursor.fetchall()
        for session in sessions:
            print(f"   Session {session[0]}: Class {session[1]}, Teacher {session[2]}, Date {session[3]}")
        
        print("\n📋 Sample attendance records:")
        cursor.execute("""
            SELECT ar.session_id, ar.student_id, ar.status, ar.marked_by, ats.session_date
            FROM attendance_records ar
            JOIN attendance_sessions ats ON ar.session_id = ats.session_id
            ORDER BY ats.session_date DESC 
            LIMIT 5
        """)
        
        records = cursor.fetchall()
        for record in records:
            print(f"   Record: Session {record[0]}, Student {record[1]}, Status {record[2]}, Date {record[4]}")
        
        # Test the exact query the ML service uses
        print("\n�� Testing ML service query...")
        cursor.execute("""
            SELECT 
                ar.student_id,
                ar.status,
                ar.created_at,
                ats.session_date,
                ats.session_time,
                ats.session_type,
                c.name as class_name,
                EXTRACT(DOW FROM ats.session_date) as day_of_week,
                EXTRACT(MONTH FROM ats.session_date) as month,
                EXTRACT(YEAR FROM ats.session_date) as year
            FROM attendance_records ar
            JOIN attendance_sessions ats ON ar.session_id = ats.session_id
            JOIN classes c ON ats.class_id = c.id
            WHERE ats.session_date >= CURRENT_DATE - INTERVAL '90 days'
            ORDER BY ats.session_date DESC
            LIMIT 10
        """)
        
        ml_data = cursor.fetchall()
        print(f"✅ ML service query returned {len(ml_data)} records")
        
        if ml_data:
            print("�� Sample ML data:")
            for row in ml_data[:3]:
                print(f"   Student {row[0]}: {row[1]} on {row[3]}, Class: {row[6]}")
        else:
            print("❌ No data found for ML service")
        
    except Exception as e:
        print(f"❌ Error debugging: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    debug_ml_data()
