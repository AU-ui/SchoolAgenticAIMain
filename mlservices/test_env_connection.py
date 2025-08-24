# ============================================================================
# SIMPLE ENV CONNECTION TEST
# ============================================================================

import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

print("🔍 Testing .env file loading...")

# Check if .env file exists
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    print(f"✅ .env file found at: {env_path}")
else:
    print(f"❌ .env file not found at: {env_path}")

# Print environment variables
print("\n📋 Environment variables:")
print(f"DB_HOST: {os.getenv('DB_HOST', 'NOT SET')}")
print(f"DB_PORT: {os.getenv('DB_PORT', 'NOT SET')}")
print(f"DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}")
print(f"DB_USER: {os.getenv('DB_USER', 'NOT SET')}")
print(f"DB_PASSWORD: {os.getenv('DB_PASSWORD', 'NOT SET')}")

# Test database connection
print("\n🧪 Testing database connection...")

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432)),
        database=os.getenv('DB_NAME', 'edtech_platform'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', '1234')
    )
    
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    cursor.close()
    conn.close()
    
    print(f"✅ Database connection successful!")
    print(f"�� PostgreSQL version: {version[0]}")
    
except Exception as e:
    print(f"❌ Database connection failed: {e}")
