# ============================================================================
# SIMPLE CONNECTION TEST
# ============================================================================
# Test connection with the exact same config as backend
# ============================================================================

import psycopg2

def test_connection():
    """Test database connection with different passwords"""
    
    # Try the exact same config as backend
    config = {
        'host': '127.0.0.1',
        'port': 5432,
        'database': 'edtech_platform',
        'user': 'postgres'
    }
    
    # Common passwords to try
    passwords = [
        'your_password',  # Backend default
        '',  # No password
        'postgres',
        'password',
        '1234',
        'admin',
        'root'
    ]
    
    print("🔍 Testing database connection...")
    print("=" * 40)
    
    for password in passwords:
        try:
            test_config = config.copy()
            test_config['password'] = password
            
            conn = psycopg2.connect(**test_config)
            print(f"✅ SUCCESS! Password: '{password}'")
            
            # Test a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            print(f"�� PostgreSQL Version: {version[:50]}...")
            
            cursor.close()
            conn.close()
            return password
            
        except Exception as e:
            print(f"❌ Failed with '{password}': {str(e)[:50]}...")
    
    return None

if __name__ == "__main__":
    working_password = test_connection()
    
    if working_password:
        print(f"\n🎉 FOUND WORKING PASSWORD: '{working_password}'")
        print("\n💡 Update your ML service with this password!")
    else:
        print("\n❌ No working password found")
