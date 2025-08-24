# ============================================================================
# TEST BACKEND CONNECTION METHOD
# ============================================================================
# Uses the same connection method as the backend
# ============================================================================

import psycopg2
import os

def test_backend_style_connection():
    """Test connection using backend-style configuration"""
    
    # Try the exact same config as backend
    configs_to_try = [
        {
            'host': 'localhost',
            'port': 5432,
            'database': 'edtech_platform',
            'user': 'postgres',
            'password': 'your_password'  # Backend default
        },
        {
            'host': 'localhost',
            'port': 5432,
            'database': 'edtech_platform',
            'user': 'postgres',
            'password': ''  # No password
        },
        {
            'host': 'localhost',
            'port': 5432,
            'database': 'edtech_platform',
            'user': 'postgres',
            'password': 'postgres'  # Common default
        }
    ]
    
    print("🔍 Testing backend-style connections...")
    print("=" * 50)
    
    for i, config in enumerate(configs_to_try, 1):
        try:
            print(f"Testing config {i}: {config['user']}@{config['host']}:{config['port']}/{config['database']}")
            conn = psycopg2.connect(**config)
            print(f"✅ SUCCESS with password: '{config['password']}'")
            conn.close()
            return config
        except Exception as e:
            print(f"❌ Failed: {str(e)[:50]}...")
    
    return None

def check_environment_variables():
    """Check if there are any environment variables set"""
    print("\n🔍 Checking environment variables...")
    
    env_vars = ['DB_PASSWORD', 'POSTGRES_PASSWORD', 'PGPASSWORD']
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"Found {var}: {value[:3]}***" if len(value) > 3 else f"Found {var}: {value}")
        else:
            print(f"Not found: {var}")

def main():
    print("�� Backend Connection Test")
    print("=" * 30)
    
    # Check environment variables
    check_environment_variables()
    
    # Test backend-style connections
    working_config = test_backend_style_connection()
    
    if working_config:
        print(f"\n🎉 FOUND WORKING CONFIG!")
        print(f"Host: {working_config['host']}")
        print(f"Port: {working_config['port']}")
        print(f"Database: {working_config['database']}")
        print(f"User: {working_config['user']}")
        print(f"Password: '{working_config['password']}'")
        
        print("\n💡 Use this configuration in your ML service!")
    else:
        print("\n❌ No working configuration found")
        print("\n💡 Please check pgAdmin connection properties for the correct password")

if __name__ == "__main__":
    main()
