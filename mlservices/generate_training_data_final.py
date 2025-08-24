# ============================================================================
# TRAINING DATA GENERATOR - FINAL VERSION
# ============================================================================
# Uses the same database configuration as the backend
# ============================================================================

import psycopg2
import random
from datetime import datetime, timedelta
import os

# Database configuration (matching backend)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'edtech_platform',
    'user': 'postgres',
    'password': 'your_password'  # Same as backend
}

def create_training_data():
    """Create comprehensive training data"""
    print("🚀 Creating training data for Smart Attendance System...")
    
    try:
        # Connect to your actual database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"✅ Connected to database: {DB_CONFIG['database']}")
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('users', 'schools', 'classes', 'attendance_sessions', 'attendance_records')
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"�� Existing tables: {existing_tables}")
        
        # Create schools if not exists
        if 'schools' not in existing_tables:
            print("🏫 Creating schools table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schools (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    address TEXT,
                    phone VARCHAR(50),
                    email VARCHAR(255),
                    principal_name VARCHAR(255),
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert sample schools
            schools_data = [
                ('Tech High School', '123 Education St, Tech City', '555-0101', 'admin@techhigh.edu', 'Dr. Smith'),
                ('Innovation Academy', '456 Learning Ave, Innovation Town', '555-0202', 'admin@innovation.edu', 'Dr. Johnson'),
                ('Future Prep School', '789 Knowledge Blvd, Future City', '555-0303', 'admin@futureprep.edu', 'Dr. Williams')
            ]
            
            cursor.executemany("""
                INSERT INTO schools (name, address, phone, email, principal_name)
                VALUES (%s, %s, %s, %s, %s)
            """, schools_data)
            
            print("✅ Schools created successfully")
        
        # Create users if not exists
        if 'users' not in existing_tables:
            print("👥 Creating users table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    first_name VARCHAR(100) NOT NULL,
                    last_name VARCHAR(100) NOT NULL,
                    role VARCHAR(50) NOT NULL CHECK (role IN ('superadmin', 'admin', 'administrator', 'teacher', 'parent', 'student')),
                    profile_picture_url TEXT,
                    phone VARCHAR(50),
                    is_active BOOLEAN DEFAULT true,
                    email_verified BOOLEAN DEFAULT false,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert sample users
            users_data = [
                # Teachers
                ('teacher1@school.edu', 'password123', 'John', 'Doe', 'teacher'),
                ('teacher2@school.edu', 'password123', 'Jane', 'Smith', 'teacher'),
                ('teacher3@school.edu', 'password123', 'Mike', 'Johnson', 'teacher'),
                
                # Students
                ('student1@school.edu', 'password123', 'Alice', 'Brown', 'student'),
                ('student2@school.edu', 'password123', 'Bob', 'Wilson', 'student'),
                ('student3@school.edu', 'password123', 'Charlie', 'Davis', 'student'),
                ('student4@school.edu', 'password123', 'Diana', 'Miller', 'student'),
                ('student5@school.edu', 'password123', 'Eve', 'Garcia', 'student'),
                
                # Admin
                ('admin@school.edu', 'password123', 'Admin', 'User', 'admin')
            ]
            
            cursor.executemany("""
                INSERT INTO users (email, password, first_name, last_name, role)
                VALUES (%s, %s, %s, %s, %s)
            """, users_data)
            
            print("✅ Users created successfully")
        
        # Create classes if not exists
        if 'classes' not in existing_tables:
            print("📚 Creating classes table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS classes (
                    id SERIAL PRIMARY KEY,
                    school_id INTEGER REFERENCES schools(id) ON DELETE CASCADE,
                    name VARCHAR(100) NOT NULL,
                    grade_level INTEGER,
                    academic_year VARCHAR(20),
                    teacher_id INTEGER REFERENCES users(id),
                    is_active BOOLEAN DEFAULT true,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Get school and teacher IDs
            cursor.execute("SELECT id FROM schools LIMIT 1")
            school_id = cursor.fetchone()[0]
            
            cursor.execute("SELECT id FROM users WHERE role = 'teacher' LIMIT 3")
            teacher_ids = [row[0] for row in cursor.fetchall()]
            
            # Insert sample classes
            classes_data = [
                (school_id, 'Mathematics 101', 10, '2024-2025', teacher_ids[0]),
                (school_id, 'Science Lab', 11, '2024-2025', teacher_ids[1]),
                (school_id, 'English Literature', 12, '2024-2025', teacher_ids[2])
            ]
            
            cursor.executemany("""
                INSERT INTO classes (school_id, name, grade_level, academic_year, teacher_id)
                VALUES (%s, %s, %s, %s, %s)
            """, classes_data)
            
            print("✅ Classes created successfully")
        
        # Create attendance tables if not exists
        if 'attendance_sessions' not in existing_tables:
            print("📅 Creating attendance tables...")
            
            # Create attendance_sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance_sessions (
                    session_id SERIAL PRIMARY KEY,
                    class_id INTEGER NOT NULL,
                    teacher_id INTEGER NOT NULL,
                    session_date DATE NOT NULL,
                    session_time TIME NOT NULL,
                    session_type VARCHAR(50) DEFAULT 'regular',
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    CONSTRAINT fk_attendance_sessions_class FOREIGN KEY (class_id) REFERENCES classes(id),
                    CONSTRAINT fk_attendance_sessions_teacher FOREIGN KEY (teacher_id) REFERENCES users(id),
                    CONSTRAINT unique_session UNIQUE (class_id, session_date, session_time)
                )
            """)
            
            # Create attendance_records table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance_records (
                    record_id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    student_id INTEGER NOT NULL,
                    status VARCHAR(20) NOT NULL CHECK (status IN ('present', 'absent', 'late', 'excused')),
                    arrival_time TIME,
                    departure_time TIME,
                    notes TEXT,
                    marked_by INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    CONSTRAINT fk_attendance_records_session FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id),
                    CONSTRAINT fk_attendance_records_student FOREIGN KEY (student_id) REFERENCES users(id),
                    CONSTRAINT fk_attendance_records_marked_by FOREIGN KEY (marked_by) REFERENCES users(id),
                    CONSTRAINT unique_attendance_record UNIQUE (session_id, student_id)
                )
            """)
            
            print("✅ Attendance tables created successfully")
        
        # Generate attendance data
        print("📊 Generating attendance records...")
        
        # Get class and student IDs
        cursor.execute("SELECT id FROM classes LIMIT 3")
        class_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id FROM users WHERE role = 'student' LIMIT 5")
        student_ids = [row[0] for row in cursor.fetchall()]
        
        cursor.execute("SELECT id FROM users WHERE role = 'teacher' LIMIT 1")
        teacher_id = cursor.fetchone()[0]
        
        # Generate 30 days of attendance data
        start_date = datetime.now() - timedelta(days=30)
        
        for day in range(30):
            current_date = start_date + timedelta(days=day)
            
            for class_id in class_ids:
                # Create attendance session
                session_time = '09:00:00'
                cursor.execute("""
                    INSERT INTO attendance_sessions 
                    (class_id, teacher_id, session_date, session_time, session_type, status)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING session_id
                """, (class_id, teacher_id, current_date.date(), session_time, 'regular', 'completed'))
                
                session_id = cursor.fetchone()[0]
                
                # Generate attendance records for each student
                for student_id in student_ids:
                    # Random attendance status with realistic patterns
                    status_choices = ['present', 'absent', 'late']
                    weights = [0.85, 0.10, 0.05]  # 85% present, 10% absent, 5% late
                    status = random.choices(status_choices, weights=weights)[0]
                    
                    arrival_time = None
                    if status == 'late':
                        arrival_time = '09:15:00'
                    elif status == 'present':
                        arrival_time = '08:55:00'
                    
                    cursor.execute("""
                        INSERT INTO attendance_records 
                        (session_id, student_id, status, arrival_time, marked_by)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (session_id, student_id, status, arrival_time, teacher_id))
        
        conn.commit()
        print("✅ Training data generated successfully!")
        print(f"�� Generated: 30 days × {len(class_ids)} classes × {len(student_ids)} students = {30 * len(class_ids) * len(student_ids)} attendance records")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating training data: {e}")
        return False

if __name__ == '__main__':
    create_training_data()
