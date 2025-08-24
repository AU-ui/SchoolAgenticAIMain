# ============================================================================
# POSTGRESQL SETUP SCRIPT
# ============================================================================
# Helps set up PostgreSQL for Smart Attendance System
# ============================================================================

import subprocess
import sys
import os

def check_postgresql_service():
    """Check if PostgreSQL service is running"""
    print("🔍 Checking PostgreSQL service...")
    
    try:
        # Check if PostgreSQL service is running
        result = subprocess.run(['sc', 'query', 'postgresql-x64-15'], 
                              capture_output=True, text=True, shell=True)
        
        if 'RUNNING' in result.stdout:
            print("✅ PostgreSQL service is running")
            return True
        else:
            print("❌ PostgreSQL service is not running")
            return False
            
    except Exception as e:
        print(f"⚠️ Could not check service status: {e}")
        return False

def start_postgresql_service():
    """Start PostgreSQL service"""
    print("🚀 Starting PostgreSQL service...")
    
    try:
        result = subprocess.run(['net', 'start', 'postgresql-x64-15'], 
                              capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            print("✅ PostgreSQL service started successfully")
            return True
        else:
            print(f"❌ Failed to start service: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting service: {e}")
        return False

def reset_postgres_password():
    """Reset PostgreSQL password"""
    print("🔐 Resetting PostgreSQL password...")
    
    try:
        # Try to connect and reset password
        result = subprocess.run([
            'psql', '-U', 'postgres', '-c', "ALTER USER postgres PASSWORD '1234';"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Password reset successfully")
            return True
        else:
            print(f"⚠️ Could not reset password: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        return False

def create_database():
    """Create school_management database"""
    print("🗄️ Creating school_management database...")
    
    try:
        result = subprocess.run([
            'psql', '-U', 'postgres', '-c', "CREATE DATABASE school_management;"
        ], capture_output=True, text=True)
        
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
        result = subprocess.run([
            'psql', '-U', 'postgres', '-d', 'school_management', 
            '-c', "SELECT version();"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database connection successful!")
            return True
        else:
            print(f"❌ Connection failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def main():
    print("🚀 PostgreSQL Setup for Smart Attendance System")
    print("=" * 60)
    
    # Step 1: Check if service is running
    if not check_postgresql_service():
        print("\n🔄 Attempting to start PostgreSQL service...")
        if not start_postgresql_service():
            print("❌ Could not start PostgreSQL service")
            print("Please start PostgreSQL manually and try again")
            return
    
    # Step 2: Try to reset password
    print("\n🔐 Attempting to reset password...")
    reset_postgres_password()
    
    # Step 3: Create database
    print("\n��️ Creating database...")
    create_database()
    
    # Step 4: Test connection
    print("\n�� Testing connection...")
    if test_connection():
        print("\n🎉 PostgreSQL setup complete!")
        print("You can now run the training data generator")
    else:
        print("\n❌ Setup incomplete")
        print("Please check PostgreSQL installation and try again")

if __name__ == '__main__':
    main()
