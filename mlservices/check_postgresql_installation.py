# ============================================================================
# POSTGRESQL INSTALLATION CHECKER
# ============================================================================
# Checks if PostgreSQL is installed and provides installation guidance
# ============================================================================

import subprocess
import sys
import os

def check_psql_command():
    """Check if psql command is available"""
    print("🔍 Checking if PostgreSQL is installed...")
    
    try:
        result = subprocess.run(['psql', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ PostgreSQL is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ PostgreSQL is not installed")
            return False
            
    except FileNotFoundError:
        print("❌ PostgreSQL is not installed (psql command not found)")
        return False
    except Exception as e:
        print(f"❌ Error checking PostgreSQL: {e}")
        return False

def check_postgresql_services():
    """Check for PostgreSQL services"""
    print("🔍 Checking for PostgreSQL services...")
    
    service_names = [
        'postgresql-x64-16',
        'postgresql-x64-15',
        'postgresql-x64-14',
        'postgresql-x64-13',
        'postgresql',
        'postgres'
    ]
    
    found_services = []
    
    for service_name in service_names:
        try:
            result = subprocess.run(['sc', 'query', service_name], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0 and 'SERVICE_NAME' in result.stdout:
                found_services.append(service_name)
                print(f"✅ Found service: {service_name}")
        except:
            continue
    
    if found_services:
        print(f"✅ Found {len(found_services)} PostgreSQL service(s)")
        return found_services
    else:
        print("❌ No PostgreSQL services found")
        return []

def test_connection():
    """Test PostgreSQL connection"""
    print("�� Testing PostgreSQL connection...")
    
    try:
        # Try to connect without password first
        result = subprocess.run([
            'psql', '-U', 'postgres', '-c', "SELECT version();"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ PostgreSQL connection successful!")
            return True
        else:
            print(f"❌ Connection failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False

def provide_installation_guide():
    """Provide installation guidance"""
    print("\n" + "=" * 60)
    print("�� POSTGRESQL INSTALLATION GUIDE")
    print("=" * 60)
    
    print("\n🔧 Step 1: Download PostgreSQL")
    print("1. Go to: https://www.postgresql.org/download/windows/")
    print("2. Click 'Download the installer'")
    print("3. Choose Windows x86-64 version")
    
    print("\n🚀 Step 2: Install PostgreSQL")
    print("1. Run installer as Administrator")
    print("2. Choose installation directory (default is fine)")
    print("3. Select components:")
    print("   ✅ PostgreSQL Server")
    print("   ✅ pgAdmin 4 (GUI tool)")
    print("   ✅ Command Line Tools")
    print("4. Set password for postgres user: 1234")
    print("5. Port: 5432 (default)")
    print("6. Complete installation")
    
    print("\n✅ Step 3: Verify Installation")
    print("After installation, run:")
    print("   psql --version")
    print("   psql -U postgres -c 'SELECT version();'")
    
    print("\n🎯 Step 4: Continue with Smart Attendance")
    print("Once PostgreSQL is installed, run:")
    print("   python fix_postgresql.py")
    print("   python generate_training_data_fixed.py")
    
    print("\n" + "=" * 60)

def main():
    print("🚀 PostgreSQL Installation Checker")
    print("=" * 60)
    
    # Check if PostgreSQL is installed
    psql_installed = check_psql_command()
    
    # Check for services
    services = check_postgresql_services()
    
    # Test connection if possible
    if psql_installed:
        connection_ok = test_connection()
        
        if connection_ok:
            print("\n🎉 PostgreSQL is properly installed and working!")
            print("You can now proceed with the Smart Attendance System.")
            print("\n📝 Next steps:")
            print("1. Run: python fix_postgresql.py")
            print("2. Run: python generate_training_data_fixed.py")
            print("3. Start ML service: python start_ml_service.py")
        else:
            print("\n⚠️ PostgreSQL is installed but connection failed.")
            print("This might be a password or service issue.")
            print("Try running: python fix_postgresql.py")
    else:
        print("\n❌ PostgreSQL is not installed.")
        provide_installation_guide()

if __name__ == '__main__':
    main()
