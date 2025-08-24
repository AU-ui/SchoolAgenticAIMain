# ============================================================================
# DATABASE CONFIGURATION FOR ML SERVICE
# ============================================================================
# Updated configuration for your PostgreSQL 17 setup
# ============================================================================

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../backend/.env')

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'edtech_platform'),  # Your actual database name
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '1234')
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
