# ============================================================================
# SETUP BASIC DATA (USERS, SCHOOLS, CLASSES) FOR ATTENDANCE SYSTEM - FIXED
# ============================================================================

import psycopg2
from datetime import datetime

def setup_basic_data():
    """Create basic users, schools, and classes for the attendance system"""
    
    print("🚀 Setting up basic data for Smart Attendance System...")
    
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
        
        # 1. Create a tenant first
        print("�� Creating tenant...")
        cursor.execute("""
            INSERT INTO tenants (name, domain, address, phone, email)
            VALUES ('Smart School Academy', 'smartschool.edu', '123 Education St, City', '+1234567890', 'admin@smartschool.edu')
            ON CONFLICT (id) DO NOTHING
            RETURNING id
        """)
        
        tenant_result = cursor.fetchone()
        if tenant_result:
            tenant_id = tenant_result[0]
        else:
            cursor.execute("SELECT id FROM tenants LIMIT 1")
            tenant_id = cursor.fetchone()[0]
        
        print(f"✅ Tenant ID: {tenant_id}")
        
        # 2. Create a school
        print("�� Creating school...")
        cursor.execute("""
            INSERT INTO schools (tenant_id, name, address, phone, email)
            VALUES (%s, 'Smart School Academy', '123 Education St, City', '+1234567890', 'admin@smartschool.edu')
            ON CONFLICT (id) DO NOTHING
            RETURNING id
        """, (tenant_id,))
        
        school_result = cursor.fetchone()
        if school_result:
            school_id = school_result[0]
        else:
            cursor.execute("SELECT id FROM schools LIMIT 1")
            school_id = cursor.fetchone()[0]
        
        print(f"✅ School ID: {school_id}")
        
        # 3. Create a teacher
        print("👨‍🏫 Creating teacher...")
        cursor.execute("""
            INSERT INTO users (email, password, first_name, last_name, role, tenant_id, created_at)
            VALUES ('teacher@smartschool.edu', 'hashed_password_123', 'John', 'Smith', 'teacher', %s, NOW())
            ON CONFLICT (email) DO NOTHING
            RETURNING id
        """, (tenant_id,))
        
        teacher_result = cursor.fetchone()
        if teacher_result:
            teacher_id = teacher_result[0]
        else:
            cursor.execute("SELECT id FROM users WHERE role = 'teacher' LIMIT 1")
            teacher_id = cursor.fetchone()[0]
        
        print(f"✅ Teacher ID: {teacher_id}")
        
        # 4. Create students
        print("👨‍🎓 Creating students...")
        students = [
            ('alice@student.edu', 'Alice', 'Johnson'),
            ('bob@student.edu', 'Bob', 'Williams'),
            ('charlie@student.edu', 'Charlie', 'Brown'),
            ('diana@student.edu', 'Diana', 'Davis'),
            ('edward@student.edu', 'Edward', 'Miller')
        ]
        
        student_ids = []
        for email, first_name, last_name in students:
            cursor.execute("""
                INSERT INTO users (email, password, first_name, last_name, role, tenant_id, created_at)
                VALUES (%s, 'hashed_password_123', %s, %s, 'student', %s, NOW())
                ON CONFLICT (email) DO NOTHING
                RETURNING id
            """, (email, first_name, last_name, tenant_id))
            
            result = cursor.fetchone()
            if result:
                student_ids.append(result[0])
            else:
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                student_ids.append(cursor.fetchone()[0])
        
        print(f"✅ Created {len(student_ids)} students")
        
        # 5. Create a class
        print("📖 Creating class...")
        cursor.execute("""
            INSERT INTO classes (school_id, name, grade_level, teacher_id, created_at)
            VALUES (%s, 'Mathematics 101', 10, %s, NOW())
            ON CONFLICT (id) DO NOTHING
            RETURNING id
        """, (school_id, teacher_id))
        
        class_result = cursor.fetchone()
        if class_result:
            class_id = class_result[0]
        else:
            cursor.execute("SELECT id FROM classes LIMIT 1")
            class_id = cursor.fetchone()[0]
        
        print(f"✅ Class ID: {class_id}")
        
        conn.commit()
        
        print("\n🎉 Basic data setup complete!")
        print(f"�� Summary:")
        print(f"   - Tenant: Smart School Academy (ID: {tenant_id})")
        print(f"   - School: Smart School Academy (ID: {school_id})")
        print(f"   - Teacher: John Smith (ID: {teacher_id})")
        print(f"   - Students: {len(student_ids)} students created")
        print(f"   - Class: Mathematics 101 (ID: {class_id})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error setting up data: {e}")
        if 'conn' in locals():
            conn.rollback()
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    setup_basic_data()
