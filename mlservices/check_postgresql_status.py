# ============================================================================
# POSTGRESQL STATUS CHECKER
# ============================================================================
# Checks PostgreSQL status when pgAdmin is installed
# ============================================================================

import subprocess
import sys
import os
import glob

def find_postgresql_installation():
    """Find PostgreSQL installation directories"""
    print("🔍 Looking for PostgreSQL installation...")
    
    # Common PostgreSQL installation paths
    possible_paths = [
        r"C:\Program Files\PostgreSQL",
        r"C:\Program Files (x86)\PostgreSQL",
        r"C:\PostgreSQL",
        os.path.expanduser(r"~\AppData\Local\Programs\PostgreSQL")
    ]
    
    found_installations = []
    
    for base_path in possible_paths:
        if os.path.exists(base_path):
            print(f"✅ Found PostgreSQL directory: {base_path}")
            
            # Look for version subdirectories
            for item in os.listdir(base_path):
                version_path = os.path.join(base_path, item)
                if os.path.isdir(version_path) and item.startswith(('15', '16', '14', '13')):
                    found_installations.append(version_path)
                    print(f"   �� Version: {item}")
    
    return found_installations

def find_psql_executable():
    """Find psql executable"""
    print("🔍 Looking for psql executable...")
    
    # Common psql locations
    possible_locations = [
        r"C:\Program Files\PostgreSQL\15\bin\psql.exe",
        r"C:\Program Files\PostgreSQL\16\bin\psql.exe",
        r"C:\Program Files\PostgreSQL\14\bin\psql.exe",
        r"C:\Program Files (x86)\PostgreSQL\15\bin\psql.exe",
        r"C:\Program Files (x86)\PostgreSQL\16\bin\psql.exe",
        r"C:\Program Files (x86)\PostgreSQL\14\bin\psql.exe"
    ]
    
    for location in possible_locations:
        if os.path.exists(location):
            print(f"✅ Found psql: {location}")
            return location
    
    print("❌ psql executable not found in common locations")
    return None

def check_postgresql_services():
    """Check PostgreSQL services"""
    print("🔍 Checking PostgreSQL services...")
    
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
                
                # Check if service is running
                if 'RUNNING' in result.stdout:
                    print(f"   �� Service is running")
                else:
                    print(f"   🔴 Service is not running")
        except:
            continue
    
    return found_services

def test_psql_connection(psql_path=None):
    """Test psql connection"""
    print("🧪 Testing psql connection...")
    
    if psql_path:
        psql_cmd = [psql_path]
    else:
        psql_cmd = ['psql']
    
    try:
        # Try to connect without password first
        result = subprocess.run(psql_cmd + ['-U', 'postgres', '-c', "SELECT version();"], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ psql connection successful!")
            return True
        else:
            print(f"❌ psql connection failed: {result.stderr}")
            return False
            
    except FileNotFoundError:
        print("❌ psql command not found in PATH")
        return False
    except Exception as e:
        print(f"❌ Error testing psql: {e}")
        return False

def provide_solutions():
    """Provide solutions based on findings"""
    print("\n" + "=" * 60)
    print("🔧 SOLUTIONS")
    print("=" * 60)
    
    print("\n📋 If PostgreSQL is installed but psql not in PATH:")
    print("1. Find your PostgreSQL installation directory")
    print("2. Add the 'bin' folder to your PATH environment variable")
    print("3. Example: C:\\Program Files\\PostgreSQL\\15\\bin")
    
    print("\n📋 If PostgreSQL service is not running:")
    print("1. Open Services (services.msc)")
    print("2. Find PostgreSQL service")
    print("3. Right-click → Start")
    print("4. Set startup type to 'Automatic'")
    
    print("\n📋 If you can't connect with psql:")
    print("1. Open pgAdmin")
    print("2. Connect to your server")
    print("3. Right-click on 'Login/Group Roles' → 'postgres'")
    print("4. Properties → Definition → Set password to '1234'")
    
    print("\n�� Quick fix commands:")
    print("# Add PostgreSQL to PATH (replace with your version)")
    print("set PATH=%PATH%;C:\\Program Files\\PostgreSQL\\15\\bin")
    print("")
    print("# Start PostgreSQL service")
    print("net start postgresql-x64-15")
    print("")
    print("# Test connection")
    print("psql -U postgres -c 'SELECT version();'")

def main():
    print("🚀 PostgreSQL Status Checker")
    print("=" * 60)
    
    # Check installations
    installations = find_postgresql_installation()
    
    # Check services
    services = check_postgresql_services()
    
    # Find psql
    psql_path = find_psql_executable()
    
    # Test connection
    if psql_path:
        connection_ok = test_psql_connection(psql_path)
    else:
        connection_ok = test_psql_connection()
    
    # Provide solutions
    provide_solutions()
    
    print("\n" + "=" * 60)
    
    if installations and services and connection_ok:
        print("🎉 PostgreSQL is working! You can proceed with Smart Attendance.")
        print("\n📝 Next steps:")
        print("1. Run: python fix_postgresql.py")
        print("2. Run: python generate_training_data_fixed.py")
    else:
        print("⚠️ PostgreSQL needs some configuration.")
        print("Follow the solutions above to fix the issues.")

if __name__ == '__main__':
    main()
