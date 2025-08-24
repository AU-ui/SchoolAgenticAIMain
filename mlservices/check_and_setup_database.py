# ============================================================================
# CHECK DATABASE SCHEMA AND SETUP BASIC DATA
# ============================================================================

import psycopg2
from datetime import datetime

def check_and_setup_database():
    """Check what tables exist and setup basic data accordingly"""
    
    print("🔍 Checking database schema...")
    
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
        
        # Check what tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"�� Existing tables: {existing_tables}")
        
        # Check users table structure
        if 'users' in existing_tables:
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """)
            
            user_columns = {row[0]: row[1] for row in cursor.fetchall()}
            print(f"👤 Users table columns: {list(user_columns.keys())}")
            
            # Check if we have the right columns
            if 'tenant_id' in user_columns:
                print("✅ Users table has tenant_id - using full schema")
                setup_full_schema(cursor, conn)
            else:
                print("⚠️  Users table missing tenant_id - using simple schema")
                setup_simple_schema(cursor, conn)
        else:
            print("❌ Users table doesn't exist - need to create schema first")
            print("💡 Please run the database schema setup first")
            return False
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def setup_simple_schema(cursor, conn):
    """Setup data for simple schema (without tenants)"""
    print("\n🚀 Setting up simple schema data...")
    
    # Create a school
    print("�� Creating school...")
    cursor.execute("""
        INSERT INTO schools (name, address, phone, email)
        VALUES ('Smart School Academy', '123 Education St, City', '+1234567890', 'admin@smartschool.edu')
        ON CONFLICT (id) DO NOTHING
        RETURNING id
    """)
    
    school_result = cursor.fetchone()
    if school_result:
        school_id = school_result[0]
    else:
        cursor.execute("SELECT id FROM schools LIMIT 1")
        school_id = cursor.fetchone()[0]
    
    print(f"✅ School ID: {school_id}")
    
    # Create a teacher (without tenant_id)
    print("👨‍🏫 Creating teacher...")
    cursor.execute("""
        INSERT INTO users (email, password, first_name, last_name, role)
        VALUES ('teacher@smartschool.edu', 'hashed_password_123', 'John', 'Smith', 'teacher')
        ON CONFLICT (email) DO NOTHING
        RETURNING id
    """)
    
    teacher_result = cursor.fetchone()
    if teacher_result:
        teacher_id = teacher_result[0]
    else:
        cursor.execute("SELECT id FROM users WHERE role = 'teacher' LIMIT 1")
        teacher_id = cursor.fetchone()[0]
    
    print(f"✅ Teacher ID: {teacher_id}")
    
    # Create students
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
            INSERT INTO users (email, password, first_name, last_name, role)
            VALUES (%s, 'hashed_password_123', %s, %s, 'student')
            ON CONFLICT (email) DO NOTHING
            RETURNING id
        """, (email, first_name, last_name))
        
        result = cursor.fetchone()
        if result:
            student_ids.append(result[0])
        else:
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            student_ids.append(cursor.fetchone()[0])
    
    print(f"✅ Created {len(student_ids)} students")
    
    # Create a class
    print("📖 Creating class...")
    cursor.execute("""
        INSERT INTO classes (school_id, name, grade_level, teacher_id)
        VALUES (%s, 'Mathematics 101', 10, %s)
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
    print("\n🎉 Simple schema setup complete!")

def setup_full_schema(cursor, conn):
    """Setup data for full schema (with tenants)"""
    print("\n🚀 Setting up full schema data...")
    
    # Create a tenant first
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
    
    # Create a school
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
    
    # Create a teacher
    print("👨‍🏫 Creating teacher...")
    cursor.execute("""
        INSERT INTO users (email, password, first_name, last_name, role, tenant_id)
        VALUES ('teacher@smartschool.edu', 'hashed_password_123', 'John', 'Smith', 'teacher', %s)
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
    
    # Create students
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
            INSERT INTO users (email, password, first_name, last_name, role, tenant_id)
            VALUES (%s, 'hashed_password_123', %s, %s, 'student', %s)
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
    
    # Create a class
    print("📖 Creating class...")
    cursor.execute("""
        INSERT INTO classes (school_id, name, grade_level, teacher_id)
        VALUES (%s, 'Mathematics 101', 10, %s)
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
    print("\n🎉 Full schema setup complete!")

if __name__ == "__main__":
    check_and_setup_database()
