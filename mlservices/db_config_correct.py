# ============================================================================
# DATABASE CONFIGURATION - CORRECTED FOR BACKEND COMPATIBILITY
# ============================================================================
# Uses the same configuration as the backend
# ============================================================================

import os

# Database configuration (matching backend/src/config/database.js)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'edtech_platform',
    'user': 'postgres',
    'password': 'your_password'  # Same as backend default
}

print(f"�� Database Config: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
print(f"�� User: {DB_CONFIG['user']}")

def test_connection():
    """Test database connection"""
    import psycopg2
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected to PostgreSQL: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == '__main__':
    test_connection()
