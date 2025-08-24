# ============================================================================
# DATABASE CONNECTION TEST
# ============================================================================
# Tests database connection before generating training data
# ============================================================================

import psycopg2
import os
from pathlib import Path

def test_database_connection():
    """Test database connection with different configurations"""
    
    # Try different password configurations
    configs = [
        {
            'host': 'localhost',
            'database': 'school_management',
            'user': 'postgres',
            'password': '1234',
            'port': 5432
        },
        {
            'host': 'localhost',
            'database': 'school_management',
            'user': 'postgres',
            'password': 'password',
            'port': 5432
        },
        {
            'host': 'localhost',
            'database': 'school_management',
            'user': 'postgres',
            'password': '',
            'port': 5432
        }
    ]
    
    print("🔍 Testing database connections...")
    print("=" * 50)
    
    for i, config in enumerate(configs, 1):
        print(f"\n📊 Test {i}: Trying password '{config['password']}'")
        
        try:
            conn = psycopg2.connect(**config)
            cursor = conn.cursor()
            
            # Test basic query
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            
            print(f"✅ Connection successful!")
            print(f"   Database: {config['database']}")
            print(f"   User: {config['user']}")
            print(f"   PostgreSQL version: {version[0]}")
            
            # Test if attendance tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'attendance%'
                ORDER BY table_name;
            """)
            
            tables = cursor.fetchall()
            if tables:
                print(f"   ✅ Attendance tables found: {[t[0] for t in tables]}")
            else:
                print(f"   ⚠️ No attendance tables found")
            
            cursor.close()
            conn.close()
            
            # Return the working config
            return config
            
        except Exception as e:
            print(f"   ❌ Connection failed: {e}")
    
    print("\n❌ All connection attempts failed!")
    return None

def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(
            host='localhost',
            database='postgres',
            user='postgres',
            password='1234',
            port=5432
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if school_management database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'school_management'")
        exists = cursor.fetchone()
        
        if not exists:
            print("📊 Creating school_management database...")
            cursor.execute("CREATE DATABASE school_management")
            print("✅ Database created successfully!")
        else:
            print("✅ Database already exists!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

if __name__ == '__main__':
    print("🚀 Database Connection Test")
    print("=" * 50)
    
    # First try to create database if it doesn't exist
    create_database_if_not_exists()
    
    # Test connection
    working_config = test_database_connection()
    
    if working_config:
        print(f"\n🎉 Database connection successful!")
        print(f"Use this configuration:")
        print(f"   DB_HOST={working_config['host']}")
        print(f"   DB_NAME={working_config['database']}")
        print(f"   DB_USER={working_config['user']}")
        print(f"   DB_PASSWORD={working_config['password']}")
        print(f"   DB_PORT={working_config['port']}")
    else:
        print(f"\n❌ No working database configuration found!")
        print("Please check your PostgreSQL installation and credentials.")
