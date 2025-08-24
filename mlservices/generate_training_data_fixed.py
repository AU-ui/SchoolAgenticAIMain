# ============================================================================
# FIXED TRAINING DATA GENERATOR
# ============================================================================
# Generates training data with proper database connection
# ============================================================================

import psycopg2
import random
from datetime import datetime, timedelta
import numpy as np
from faker import Faker
import sys
import os

# Add the parent directory to the path to import the test module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialize Faker for realistic data
fake = Faker()

class FixedTrainingDataGenerator:
    def __init__(self):
        # Try to get working database config
        try:
            from test_db_connection import test_database_connection
            self.db_config = test_database_connection()
            if not self.db_config:
                raise Exception("No working database configuration found")
        except ImportError:
            # Fallback configuration
            self.db_config = {
                'host': 'localhost',
                'database': 'school_management',
                'user': 'postgres',
                'password': '1234',
                'port': 5432
            }
        
    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            return None
    
    def generate_schools(self, num_schools=2):
        """Generate sample schools"""
        conn = self.connect_db()
        if not conn:
            return []
        
        try:
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
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (school_data['name'], school_data['address'], 
                      school_data['phone'], school_data['email'], 
                      school_data['principal_name']))
                
                school_id = cursor.fetchone()[0]
                schools.append(school_id)
                print(f"✅ Created school: {school_data['name']} (ID: {school_id})")
            
            conn.commit()
            return schools
            
        except Exception as e:
            print(f"Error generating schools: {e}")
            conn.rollback()
            return []
        finally:
            conn.close()
    
    def generate_teachers(self, num_teachers=5):
        """Generate sample teachers"""
        conn = self.connect_db()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            teachers = []
            
            for i in range(num_teachers):
                teacher_data = {
                    'email': fake.email(),
                    'password': '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',  # 'password'
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'role': 'teacher',
                    'phone': fake.phone_number(),
                    'email_verified': True
                }
                
                cursor.execute("""
                    INSERT INTO users (email, password, first_name, last_name, role, phone, email_verified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (teacher_data['email'], teacher_data['password'],
                      teacher_data['first_name'], teacher_data['last_name'],
                      teacher_data['role'], teacher_data['phone'],
                      teacher_data['email_verified']))
                
                teacher_id = cursor.fetchone()[0]
                teachers.append(teacher_id)
                print(f"✅ Created teacher: {teacher_data['first_name']} {teacher_data['last_name']} (ID: {teacher_id})")
            
            conn.commit()
            return teachers
            
        except Exception as e:
            print(f"Error generating teachers: {e}")
            conn.rollback()
            return []
        finally:
            conn.close()
    
    def generate_students(self, num_students=30):
        """Generate sample students"""
        conn = self.connect_db()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            students = []
            
            for i in range(num_students):
                student_data = {
                    'email': fake.email(),
                    'password': '$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',  # 'password'
                    'first_name': fake.first_name(),
                    'last_name': fake.last_name(),
                    'role': 'student',
                    'phone': fake.phone_number(),
                    'email_verified': True
                }
                
                cursor.execute("""
                    INSERT INTO users (email, password, first_name, last_name, role, phone, email_verified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (student_data['email'], student_data['password'],
                      student_data['first_name'], student_data['last_name'],
                      student_data['role'], student_data['phone'],
                      student_data['email_verified']))
                
                student_id = cursor.fetchone()[0]
                students.append(student_id)
                print(f"✅ Created student: {student_data['first_name']} {student_data['last_name']} (ID: {student_id})")
            
            conn.commit()
            return students
            
        except Exception as e:
            print(f"Error generating students: {e}")
            conn.rollback()
            return []
        finally:
            conn.close()
    
    def generate_classes(self, schools, teachers, num_classes=6):
        """Generate sample classes"""
        conn = self.connect_db()
        if not conn:
            return []
        
        try:
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
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (class_data['school_id'], class_data['name'],
                      class_data['grade_level'], class_data['academic_year'],
                      class_data['teacher_id']))
                
                class_id = cursor.fetchone()[0]
                classes.append(class_id)
                print(f"✅ Created class: {class_data['name']} Grade {class_data['grade_level']} (ID: {class_id})")
            
            conn.commit()
            return classes
            
        except Exception as e:
            print(f"Error generating classes: {e}")
            conn.rollback()
            return []
        finally:
            conn.close()
    
    def generate_attendance_data(self, classes, students, days_back=30):  # Reduced to 30 days for faster generation
        """Generate realistic attendance data"""
        conn = self.connect_db()
        if not conn:
            return
        
        try:
            cursor = conn.cursor()
            
            # Generate attendance for the last 30 days (reduced for faster generation)
            start_date = datetime.now() - timedelta(days=days_back)
            
            for class_id in classes:
                # Get students for this class (randomly assign 10-15 students per class)
                class_students = random.sample(students, random.randint(10, min(15, len(students))))
                
                print(f"📊 Generating attendance for class {class_id} with {len(class_students)} students...")
                
                current_date = start_date
                while current_date <= datetime.now():
                    # Skip weekends
                    if current_date.weekday() < 5:  # Monday to Friday
                        # Create attendance session
                        session_time = random.choice(['08:00', '09:00', '10:00', '11:00', '14:00', '15:00'])
                        
                        cursor.execute("""
                            INSERT INTO attendance_sessions (class_id, teacher_id, session_date, session_time, session_type, status)
                            VALUES (%s, (SELECT teacher_id FROM classes WHERE id = %s), %s, %s, 'regular', 'completed')
                            RETURNING session_id
                        """, (class_id, class_id, current_date.date(), session_time))
                        
                        session_id = cursor.fetchone()[0]
                        
                        # Generate attendance records for each student
                        for student_id in class_students:
                            # Realistic attendance patterns
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
                            
                            # Determine attendance status
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
                            
                            # Add some notes for late/absent students
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
                                VALUES (%s, %s, %s, %s, %s, (SELECT teacher_id FROM classes WHERE id = %s))
                            """, (session_id, student_id, status, arrival_time, notes, class_id))
                    
                    current_date += timedelta(days=1)
                
                print(f"✅ Generated {days_back} days of attendance data for class {class_id}")
            
            conn.commit()
            print("🎉 All attendance data generated successfully!")
            
        except Exception as e:
            print(f"Error generating attendance data: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def generate_all_training_data(self):
        """Generate all training data"""
        print("🚀 Starting Fixed Training Data Generation...")
        print("=" * 60)
        print(f"📊 Using database: {self.db_config['database']}")
        print(f"👤 User: {self.db_config['user']}")
        print(f"�� Password: {self.db_config['password']}")
        print("=" * 60)
        
        # Generate basic entities
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
        print("🎉 FIXED TRAINING DATA GENERATION COMPLETE!")
        print("=" * 60)
        print(f"✅ Schools: {len(schools)}")
        print(f"✅ Teachers: {len(teachers)}")
        print(f"✅ Students: {len(students)}")
        print(f"✅ Classes: {len(classes)}")
        print(f"✅ Attendance Records: ~{len(students) * len(classes) * 30} records")
        print("\n🤖 AI models can now be trained with this data!")

if __name__ == '__main__':
    generator = FixedTrainingDataGenerator()
    generator.generate_all_training_data()
