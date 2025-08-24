# ============================================================================
# DEBUG CONNECTION DIFFERENCE
# ============================================================================
# Compare backend and ML service connection methods
# ============================================================================

import psycopg2
import subprocess
import os
import sys

def check_backend_connection():
    """Check how the backend is connecting"""
    print("🔍 Checking Backend Connection Method...")
    print("=" * 50)
    
    try:
        # Try to connect to the backend API to see if it's working
        import requests
        response = requests.get("http://localhost:5000/health")
        if response.status_code == 200:
            print("✅ Backend is responding on port 5000")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Backend not responding properly: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach backend: {e}")

def check_postgresql_config():
    """Check PostgreSQL configuration"""
    print("\n🔍 Checking PostgreSQL Configuration...")
    print("=" * 50)
    
    # Check if PostgreSQL is listening
    try:
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        if '5432' in result.stdout:
            print("✅ PostgreSQL is listening on port 5432")
            # Show the specific line
            for line in result.stdout.split('\n'):
                if '5432' in line:
                    print(f"   {line.strip()}")
        else:
            print("❌ PostgreSQL not found on port 5432")
    except Exception as e:
        print(f"❌ Cannot check netstat: {e}")

def try_different_connection_methods():
    """Try different connection methods"""
    print("\n🔍 Trying Different Connection Methods...")
    print("=" * 50)
    
    # Method 1: Try with different connection strings
    connection_strings = [
        "postgresql://postgres:your_password@127.0.0.1:5432/edtech_platform",
        "postgresql://postgres:your_password@localhost:5432/edtech_platform",
        "postgresql://postgres@127.0.0.1:5432/edtech_platform",
        "postgresql://postgres@localhost:5432/edtech_platform"
    ]
    
    for i, conn_str in enumerate(connection_strings, 1):
        try:
            print(f"Testing method {i}: {conn_str}")
            conn = psycopg2.connect(conn_str)
            print(f"✅ SUCCESS with method {i}")
            conn.close()
            return conn_str
        except Exception as e:
            print(f"❌ Failed method {i}: {str(e)[:50]}...")
    
    return None

def check_environment_differences():
    """Check environment differences"""
    print("\n🔍 Checking Environment Differences...")
    print("=" * 50)
    
    # Check Python environment
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check environment variables
    env_vars = ['DB_PASSWORD', 'POSTGRES_PASSWORD', 'PGPASSWORD', 'PATH']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"{var}: {value[:20]}..." if len(value) > 20 else f"{var}: {value}")
        else:
            print(f"{var}: Not set")

def try_backend_style_connection():
    """Try to mimic the backend connection style"""
    print("\n🔍 Trying Backend-Style Connection...")
    print("=" * 50)
    
    # Try the exact same config as backend
    config = {
        'host': '127.0.0.1',
        'port': 5432,
        'database': 'edtech_platform',
        'user': 'postgres',
        'password': 'your_password',
        'sslmode': 'disable',  # Backend might be using this
        'connect_timeout': 10
    }
    
    try:
        print("Trying backend-style config...")
        conn = psycopg2.connect(**config)
        print("✅ SUCCESS with backend-style config!")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Failed with backend-style config: {e}")
        return False

def main():
    print("🔧 Debugging Connection Difference")
    print("=" * 60)
    
    # Check backend connection
    check_backend_connection()
    
    # Check PostgreSQL config
    check_postgresql_config()
    
    # Check environment differences
    check_environment_differences()
    
    # Try different connection methods
    working_method = try_different_connection_methods()
    
    # Try backend-style connection
    backend_style_works = try_backend_style_connection()
    
    print("\n" + "=" * 60)
    print("🎯 Summary:")
    
    if working_method:
        print(f"✅ Found working connection method: {working_method}")
    elif backend_style_works:
        print("✅ Backend-style connection works!")
    else:
        print("❌ No connection method works")
        print("\n💡 Possible reasons:")
        print("1. Backend is using a different user/authentication method")
        print("2. Backend has a .env file with different credentials")
        print("3. Backend is using connection pooling")
        print("4. PostgreSQL is configured differently for different clients")

if __name__ == "__main__":
    main()
