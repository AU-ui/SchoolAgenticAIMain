# ============================================================================
# POSTGRESQL FIX SCRIPT
# ============================================================================
# Comprehensive PostgreSQL setup and fix for Smart Attendance System
# ============================================================================

import subprocess
import sys
import os
import time

def find_postgresql_service():
    """Find the correct PostgreSQL service name"""
    print("�� Finding PostgreSQL service...")
    
    # Common PostgreSQL service names
    service_names = [
        'postgresql-x64-15',
        'postgresql-x64-14', 
        'postgresql-x64-13',
        'postgresql-x64-12',
        'postgresql-x64-11',
        'postgresql-x64-10',
        'postgresql-x64-9',
        'postgresql',
        'postgres'
    ]
    
    for service_name in service_names:
        try:
            result = subprocess.run(['sc', 'query', service_name], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0 and 'SERVICE_NAME' in result.stdout:
                print(f"✅ Found PostgreSQL service: {service_name}")
                return service_name
        except:
            continue
    
    print("❌ No PostgreSQL service found")
    return None

def check_postgresql_service(service_name):
    """Check if PostgreSQL service is running"""
    print(f"🔍 Checking {service_name} service...")
    
    try:
        result = subprocess.run(['sc', 'query', service_name], 
                              capture_output=True, text=True, shell=True)
        
        if 'RUNNING' in result.stdout:
            print(f"✅ {service_name} service is running")
            return True
        else:
            print(f"❌ {service_name} service is not running")
            return False
            
    except Exception as e:
        print(f"⚠️ Could not check service status: {e}")
        return False

def start_postgresql_service(service_name):
    """Start PostgreSQL service"""
    print(f"🚀 Starting {service_name} service...")
    
    try:
        result = subprocess.run(['net', 'start', service_name], 
                              capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print(f"✅ {service_name} service started successfully")
            return True
        else:
            print(f"❌ Failed to start service: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting service: {e}")
        return False

def try_connect_without_password():
    """Try to connect to PostgreSQL without password"""
    print("🔐 Trying to connect without password...")
    
    try:
        result = subprocess.run([
            'psql', '-U', 'postgres', '-c', "SELECT version();"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Connected without password")
            return True
        else:
            print(f"❌ Could not connect without password: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Connection timeout")
        return False
    except Exception as e:
        print(f"❌ Error connecting: {e}")
        return False

def try_connect_with_password(password):
    """Try to connect to PostgreSQL with specific password"""
    print(f"🔐 Trying to connect with password: '{password}'")
    
    try:
        # Set PGPASSWORD environment variable
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        result = subprocess.run([
            'psql', '-U', 'postgres', '-c', "SELECT version();"
        ], capture_output=True, text=True, env=env, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ Connected with password: '{password}'")
            return True
        else:
            print(f"❌ Could not connect with password '{password}': {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Connection timeout")
        return False
    except Exception as e:
        print(f"❌ Error connecting: {e}")
        return False

def reset_postgres_password():
    """Reset PostgreSQL password using different methods"""
    print("🔐 Attempting to reset PostgreSQL password...")
    
    # Method 1: Try to connect without password and set new password
    if try_connect_without_password():
        try:
            result = subprocess.run([
                'psql', '-U', 'postgres', '-c', "ALTER USER postgres PASSWORD '1234';"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ Password reset successfully")
                return True
            else:
                print(f"❌ Could not reset password: {result.stderr}")
        except Exception as e:
            print(f"❌ Error resetting password: {e}")
    
    # Method 2: Try common passwords
    common_passwords = ['', 'postgres', 'admin', 'password', '123456', '1234']
    
    for password in common_passwords:
        if try_connect_with_password(password):
            try:
                env = os.environ.copy()
                env['PGPASSWORD'] = password
                
                result = subprocess.run([
                    'psql', '-U', 'postgres', '-c', "ALTER USER postgres PASSWORD '1234';"
                ], capture_output=True, text=True, env=env, timeout=10)
                
                if result.returncode == 0:
                    print("✅ Password reset successfully")
                    return True
                else:
                    print(f"❌ Could not reset password: {result.stderr}")
            except Exception as e:
                print(f"❌ Error resetting password: {e}")
    
    print("❌ Could not reset password with any method")
    return False

def create_database():
    """Create school_management database"""
    print("🗄️ Creating school_management database...")
    
    try:
        env = os.environ.copy()
        env['PGPASSWORD'] = '1234'
        
        result = subprocess.run([
            'psql', '-U', 'postgres', '-c', "CREATE DATABASE school_management;"
        ], capture_output=True, text=True, env=env, timeout=10)
        
        if result.returncode == 0:
            print("✅ Database created successfully")
            return True
        elif "already exists" in result.stderr:
            print("✅ Database already exists")
            return True
        else:
            print(f"⚠️ Could not create database: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def test_connection():
    """Test database connection"""
    print("🧪 Testing database connection...")
    
    try:
        env = os.environ.copy()
        env['PGPASSWORD'] = '1234'
        
        result = subprocess.run([
            'psql', '-U', 'postgres', '-d', 'school_management', 
            '-c', "SELECT version();"
        ], capture_output=True, text=True, env=env, timeout=10)
        
        if result.returncode == 0:
            print("✅ Database connection successful!")
            return True
        else:
            print(f"❌ Connection failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def run_attendance_schema():
    """Run the attendance schema SQL"""
    print("📊 Setting up attendance tables...")
    
    try:
        env = os.environ.copy()
        env['PGPASSWORD'] = '1234'
        
        # Read the schema file
        schema_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'database', 'attendance_schema.sql')
        
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            result = subprocess.run([
                'psql', '-U', 'postgres', '-d', 'school_management', '-c', schema_sql
            ], capture_output=True, text=True, env=env, timeout=30)
            
            if result.returncode == 0:
                print("✅ Attendance tables created successfully")
                return True
            else:
                print(f"⚠️ Could not create tables: {result.stderr}")
                return False
        else:
            print(f"❌ Schema file not found: {schema_path}")
            return False
            
    except Exception as e:
        print(f"❌ Error setting up tables: {e}")
        return False

def main():
    print("�� PostgreSQL Fix for Smart Attendance System")
    print("=" * 60)
    
    # Step 1: Find PostgreSQL service
    service_name = find_postgresql_service()
    if not service_name:
        print("❌ PostgreSQL not installed or service not found")
        print("Please install PostgreSQL and try again")
        return
    
    # Step 2: Check if service is running
    if not check_postgresql_service(service_name):
        print(f"\n🔄 Attempting to start {service_name} service...")
        if not start_postgresql_service(service_name):
            print("❌ Could not start PostgreSQL service")
            print("Please start PostgreSQL manually and try again")
            return
    
    # Wait a moment for service to fully start
    print("⏳ Waiting for service to fully start...")
    time.sleep(3)
    
    # Step 3: Try to reset password
    print("\n🔐 Attempting to reset password...")
    if not reset_postgres_password():
        print("⚠️ Could not reset password automatically")
        print("Please manually reset PostgreSQL password to '1234'")
        print("You can do this by:")
        print("1. Opening pgAdmin")
        print("2. Right-clicking on 'Login/Group Roles' → 'postgres'")
        print("3. Properties → Definition → Set password to '1234'")
        return
    
    # Step 4: Create database
    print("\n��️ Creating database...")
    if not create_database():
        print("❌ Could not create database")
        return
    
    # Step 5: Test connection
    print("\n�� Testing connection...")
    if not test_connection():
        print("❌ Connection test failed")
        return
    
    # Step 6: Set up attendance tables
    print("\n📊 Setting up attendance tables...")
    if not run_attendance_schema():
        print("⚠️ Could not set up attendance tables")
        print("You can run the schema manually later")
    
    print("\n🎉 PostgreSQL setup complete!")
    print("You can now run the training data generator")
    print("\n📝 Next steps:")
    print("1. Run: python generate_training_data_fixed.py")
    print("2. Start ML service: python start_ml_service.py")
    print("3. Test the complete system")

if __name__ == '__main__':
    main()
