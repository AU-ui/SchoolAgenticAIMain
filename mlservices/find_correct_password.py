# ============================================================================
# PASSWORD FINDER FOR POSTGRESQL
# ============================================================================
# Tests common passwords to find the correct one
# ============================================================================

import psycopg2

# Common passwords to try
passwords_to_try = [
    '1234',
    'password',
    'postgres',
    'admin',
    'root',
    'your_password',
    '',  # empty password
    '123456',
    'qwerty',
    'postgresql'
]

# Database configuration
DB_CONFIG_BASE = {
    'host': 'localhost',
    'port': 5432,
    'database': 'edtech_platform',
    'user': 'postgres'
}

def test_password(password):
    """Test a specific password"""
    try:
        config = DB_CONFIG_BASE.copy()
        config['password'] = password
        
        conn = psycopg2.connect(**config)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        
        print(f"✅ SUCCESS! Password is: '{password}'")
        print(f"✅ Connected to PostgreSQL: {version[0]}")
        return password
        
    except Exception as e:
        print(f"❌ Failed with password '{password}': {str(e)[:50]}...")
        return None

def main():
    print("🔍 Finding correct PostgreSQL password...")
    print("=" * 50)
    
    for password in passwords_to_try:
        result = test_password(password)
        if result:
            return result
    
    print("❌ None of the common passwords worked.")
    print("💡 You may need to check your PostgreSQL installation.")
    return None

if __name__ == '__main__':
    main()
