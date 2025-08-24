# ============================================================================
# SQLITE TRAINING DATA GENERATOR
# ============================================================================
# Generates training data using SQLite (no PostgreSQL required)
# ============================================================================

import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker
import os

# Initialize Faker for realistic data
fake = Faker()

class SQLiteTrainingDataGenerator:
    def __init__(self):
        self.db_path = 'smart_attendance.db'
        self.setup_database()
    
    def setup_database(self):
        """Create SQLite database and tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                address TEXT,
                phone TEXT,
                email TEXT,
                principal_name TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                role TEXT NOT NULL,
                phone TEXT,
                is_active BOOLEAN DEFAULT 1,
                email_verified BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                school_id INTEGER,
                name TEXT NOT NULL,
                grade_level INTEGER,
                academic_year TEXT,
                teacher_id INTEGER,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (school_id) REFERENCES schools (id),
                FOREIGN KEY (teacher_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance_sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                class_id INTEGER NOT NULL,
                teacher_id INTEGER NOT NULL,
                session_date DATE NOT NULL,
                session_time TIME NOT NULL,
                session_type TEXT DEFAULT 'regular',
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes (id),
                FOREIGN KEY (teacher_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                student_id INTEGER NOT NULL,
                status TEXT NOT NULL,
                arrival_time TIME,
                departure_time TIME,
                notes TEXT,
                marked_by INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES attendance_sessions (session_id),
                FOREIGN KEY (student_id) REFERENCES users (id),
                FOREIGN KEY (marked_by) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance_analytics (
                analytics_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                period_type TEXT NOT NULL,
                period_start DATE NOT NULL,
                period_end DATE NOT NULL,
                total_sessions INTEGER DEFAULT 0,
                present_count INTEGER DEFAULT 0,
                absent_count INTEGER DEFAULT 0,
                late_count INTEGER DEFAULT 0,
                excused_count INTEGER DEFAULT 0,
                attendance_percentage REAL DEFAULT 0.0,
                ai_prediction TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES users (id),
                FOREIGN KEY (class_id) REFERENCES classes (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ SQLite database and tables created successfully")
    
    def generate_schools(self, num_schools=2):
        """Generate sample schools"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        schools = []
        
        for i in range(num_schools):
            school_data = {
                'name': f"{fake.company()} School",
                'address': fake.address(),
                'phone': fake.phone_number(),
                'email': fake.email(),
                'principal_name': fake.name()
            }
            
            cursor.execute("""
                INSERT INTO schools (name, address, phone, email, principal_name)
                VALUES (?, ?, ?, ?, ?)
            """, (school_data['name'], school_data['address'], 
                  school_data['phone'], school_data['email'], 
                  school_data['principal_name']))
            
            school_id = cursor.lastrowid
            schools.append(school_id)
            print(f"✅ Created school: {school_data['name']} (ID: {school_id})")
        
        conn.commit()
        conn.close()
        return schools
    
    def generate_teachers(self, num_teachers=5):
        """Generate sample teachers"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        teachers = []
        
        for i in range(num_teachers):
            teacher_data = {
                'email': fake.email(),
                'password': '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',  # 'password'
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'role': 'teacher',
                'phone': fake.phone_number()
            }
            
            cursor.execute("""
                INSERT INTO users (email, password, first_name, last_name, role, phone)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (teacher_data['email'], teacher_data['password'],
                  teacher_data['first_name'], teacher_data['last_name'],
                  teacher_data['role'], teacher_data['phone']))
            
            teacher_id = cursor.lastrowid
            teachers.append(teacher_id)
            print(f"✅ Created teacher: {teacher_data['first_name']} {teacher_data['last_name']} (ID: {teacher_id})")
        
        conn.commit()
        conn.close()
        return teachers
    
    def generate_students(self, num_students=30):
        """Generate sample students"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        students = []
        
        for i in range(num_students):
            student_data = {
                'email': fake.email(),
                'password': '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',  # 'password'
                'first_name': fake.first_name(),
                'last_name': fake.last_name(),
                'role': 'student',
                'phone': fake.phone_number()
            }
            
            cursor.execute("""
                INSERT INTO users (email, password, first_name, last_name, role, phone)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (student_data['email'], student_data['password'],
                  student_data['first_name'], student_data['last_name'],
                  student_data['role'], student_data['phone']))
            
            student_id = cursor.lastrowid
            students.append(student_id)
            print(f"✅ Created student: {student_data['first_name']} {student_data['last_name']} (ID: {student_id})")
        
        conn.commit()
        conn.close()
        return students
    
    def generate_classes(self, schools, teachers, num_classes=6):
        """Generate sample classes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        classes = []
        
        class_names = ['Mathematics', 'Science', 'English', 'History', 'Geography', 'Computer Science']
        grade_levels = [9, 10, 11, 12]
        
        for i in range(num_classes):
            class_data = {
                'school_id': random.choice(schools),
                'name': class_names[i % len(class_names)],
                'grade_level': random.choice(grade_levels),
                'academic_year': '2024-2025',
                'teacher_id': random.choice(teachers)
            }
            
            cursor.execute("""
                INSERT INTO classes (school_id, name, grade_level, academic_year, teacher_id)
                VALUES (?, ?, ?, ?, ?)
            """, (class_data['school_id'], class_data['name'],
                  class_data['grade_level'], class_data['academic_year'],
                  class_data['teacher_id']))
            
            class_id = cursor.lastrowid
            classes.append(class_id)
            print(f"✅ Created class: {class_data['name']} Grade {class_data['grade_level']} (ID: {class_id})")
        
        conn.commit()
        conn.close()
        return classes
    
    def generate_attendance_data(self, classes, students, days_back=30):
        """Generate realistic attendance data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        start_date = datetime.now() - timedelta(days=days_back)
        
        for class_id in classes:
            class_students = random.sample(students, random.randint(10, min(15, len(students))))
            
            print(f"📊 Generating attendance for class {class_id} with {len(class_students)} students...")
            
            current_date = start_date
            while current_date <= datetime.now():
                if current_date.weekday() < 5:  # Monday to Friday
                    session_time = random.choice(['08:00', '09:00', '10:00', '11:00', '14:00', '15:00'])
                    
                    cursor.execute("""
                        INSERT INTO attendance_sessions (class_id, teacher_id, session_date, session_time, session_type, status)
                        VALUES (?, (SELECT teacher_id FROM classes WHERE id = ?), ?, ?, 'regular', 'completed')
                    """, (class_id, class_id, current_date.date(), session_time))
                    
                    session_id = cursor.lastrowid
                    
                    for student_id in class_students:
                        student_type = random.choices(
                            ['good', 'average', 'struggling'],
                            weights=[0.4, 0.4, 0.2]
                        )[0]
                        
                        if student_type == 'good':
                            attendance_prob = random.uniform(0.90, 0.95)
                        elif student_type == 'average':
                            attendance_prob = random.uniform(0.75, 0.85)
                        else:  # struggling
                            attendance_prob = random.uniform(0.60, 0.75)
                        
                        if random.random() < attendance_prob:
                            status = 'present'
                            arrival_time = session_time
                        else:
                            if random.random() < 0.3:  # 30% of absences are late
                                status = 'late'
                                late_minutes = random.randint(5, 30)
                                arrival_time = (datetime.strptime(session_time, '%H:%M') + 
                                              timedelta(minutes=late_minutes)).strftime('%H:%M')
                            else:
                                status = 'absent'
                                arrival_time = None
                        
                        notes = None
                        if status == 'late':
                            notes = random.choice([
                                'Traffic delay',
                                'Overslept',
                                'Bus was late',
                                'Family emergency'
                            ])
                        elif status == 'absent':
                            if random.random() < 0.2:  # 20% of absences are excused
                                status = 'excused'
                                notes = random.choice([
                                    'Doctor appointment',
                                    'Family vacation',
                                    'Religious holiday',
                                    'Medical emergency'
                                ])
                        
                        cursor.execute("""
                            INSERT INTO attendance_records (session_id, student_id, status, arrival_time, notes, marked_by)
                            VALUES (?, ?, ?, ?, ?, (SELECT teacher_id FROM classes WHERE id = ?))
                        """, (session_id, student_id, status, arrival_time, notes, class_id))
                
                current_date += timedelta(days=1)
            
            print(f"✅ Generated {days_back} days of attendance data for class {class_id}")
        
        conn.commit()
        conn.close()
        print("🎉 All attendance data generated successfully!")
    
    def generate_all_training_data(self):
        """Generate all training data"""
        print("🚀 Starting SQLite Training Data Generation...")
        print("=" * 60)
        
        print("\n�� Generating schools...")
        schools = self.generate_schools()
        
        print("\n👨‍🏫 Generating teachers...")
        teachers = self.generate_teachers()
        
        print("\n👨‍🎓 Generating students...")
        students = self.generate_students()
        
        print("\n�� Generating classes...")
        classes = self.generate_classes(schools, teachers)
        
        print("\n📊 Generating attendance data...")
        self.generate_attendance_data(classes, students)
        
        print("\n" + "=" * 60)
        print("🎉 SQLITE TRAINING DATA GENERATION COMPLETE!")
        print("=" * 60)
        print(f"✅ Schools: {len(schools)}")
        print(f"✅ Teachers: {len(teachers)}")
        print(f"✅ Students: {len(students)}")
        print(f"✅ Classes: {len(classes)}")
        print(f"✅ Database file: {self.db_path}")
        print("\n🤖 AI models can now be trained with this data!")

if __name__ == '__main__':
    generator = SQLiteTrainingDataGenerator()
    generator.generate_all_training_data()
