# ============================================================================
# DATABASE CONFIGURATION - SIMPLIFIED VERSION
# ============================================================================
# Direct configuration for your PostgreSQL 17 setup
# ============================================================================

import os

# Direct database configuration (no dotenv dependency)
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'edtech_platform',  # Your actual database name
    'user': 'postgres',
    'password': '1234'
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
