# ============================================================================
# DEBUG BACKEND CONNECTION
# ============================================================================
# Let's see what the backend is actually doing
# ============================================================================

import psycopg2
import subprocess
import os
import sys

def check_backend_process():
    """Check if backend is running and what it's doing"""
    print("🔍 Checking backend process...")
    
    try:
        # Check if backend is running on port 5000
        result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
        if '5000' in result.stdout:
            print("✅ Backend is running on port 5000")
        else:
            print("❌ Backend not found on port 5000")
    except:
        print("⚠️ Could not check backend process")

def try_different_connection_methods():
    """Try different connection methods"""
    print("\n🔍 Trying different connection methods...")
    
    # Method 1: Try with different hosts
    hosts_to_try = ['localhost', '127.0.0.1', '::1']
    
    for host in hosts_to_try:
        try:
            print(f"Testing host: {host}")
            conn = psycopg2.connect(
                host=host,
                port=5432,
                database='edtech_platform',
                user='postgres',
                password='your_password'
            )
            print(f"✅ SUCCESS with host: {host}")
            conn.close()
            return {'host': host, 'password': 'your_password'}
        except Exception as e:
            print(f"❌ Failed with {host}: {str(e)[:50]}...")
    
    return None

def check_postgresql_installation():
    """Check PostgreSQL installation details"""
    print("\n🔍 Checking PostgreSQL installation...")
    
    try:
        # Try to find PostgreSQL installation
        result = subprocess.run(['psql', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL found: {result.stdout.strip()}")
        else:
            print("❌ PostgreSQL not found in PATH")
    except:
        print("❌ Could not check PostgreSQL installation")

def try_connection_without_password():
    """Try connection without password (trust authentication)"""
    print("\n🔍 Trying connection without password...")
    
    try:
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            database='edtech_platform',
            user='postgres'
            # No password
        )
        print("✅ SUCCESS! No password needed (trust authentication)")
        conn.close()
        return {'password': ''}
    except Exception as e:
        print(f"❌ Failed without password: {str(e)[:50]}...")
        return None

def main():
    print("�� Backend Connection Debug")
    print("=" * 30)
    
    # Check backend process
    check_backend_process()
    
    # Check PostgreSQL installation
    check_postgresql_installation()
    
    # Try connection without password first
    result = try_connection_without_password()
    if result:
        print(f"\n🎉 FOUND WORKING CONFIG!")
        print(f"Password: '{result['password']}' (empty)")
        return
    
    # Try different hosts
    result = try_different_connection_methods()
    if result:
        print(f"\n🎉 FOUND WORKING CONFIG!")
        print(f"Host: {result['host']}")
        print(f"Password: '{result['password']}'")
        return
    
    print("\n❌ No working configuration found")
    print("\n💡 Let's try a different approach...")
    print("1. Check if PostgreSQL is using trust authentication")
    print("2. Check if there's a different user")
    print("3. Check if the backend is using a different connection method")

if __name__ == "__main__":
    main()
