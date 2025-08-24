# ============================================================================
# FIND BACKEND PASSWORD
# ============================================================================
# Tests the same passwords that the backend might be using
# ============================================================================

import psycopg2

def test_password(password):
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='edtech_platform',
            user='postgres',
            password=password
        )
        print(f"✅ SUCCESS! Password works: '{password}'")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Failed: '{password}' - {str(e)[:50]}...")
        return False

# Test passwords in order of likelihood
passwords_to_test = [
    'your_password',  # Backend default
    '',  # No password
    'postgres',
    'password',
    '1234',
    'admin',
    'root',
    'edtech',
    'platform'
]

print("🔍 Testing passwords that might work with your backend...")
print("=" * 60)

for password in passwords_to_test:
    if test_password(password):
        print(f"\n🎉 FOUND WORKING PASSWORD: '{password}'")
        print("Use this password in your ML service!")
        break
else:
    print("\n❌ None of the tested passwords worked")
    print("\n💡 Try these steps:")
    print("1. Check if there's a .env file in the backend folder")
    print("2. Look at pgAdmin connection properties")
    print("3. Try connecting with psql directly")
