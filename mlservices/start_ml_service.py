# ============================================================================
# ML SERVICE STARTUP SCRIPT
# ============================================================================
# Starts the Smart Attendance AI/ML service
# ============================================================================

import os
import sys
import subprocess
import time
from pathlib import Path

def check_dependencies():
    """Check if required Python packages are installed"""
    required_packages = [
        'flask', 'flask-cors', 'scikit-learn', 'pandas', 
        'numpy', 'psycopg2-binary', 'joblib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    if missing_packages:
        print(f"\n⚠️ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        for package in missing_packages:
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ Installed {package}")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")
                return False
    
    return True

def create_models_directory():
    """Create models directory if it doesn't exist"""
    models_dir = Path('models')
    if not models_dir.exists():
        models_dir.mkdir()
        print("✅ Created models directory")
    else:
        print("✅ Models directory exists")

def start_ml_service():
    """Start the ML service"""
    print("🚀 Starting Smart Attendance ML Service...")
    print("=" * 60)
    
    # Check dependencies
    print("📦 Checking dependencies...")
    if not check_dependencies():
        print("❌ Failed to install dependencies")
        return False
    
    # Create models directory
    print("\n📁 Setting up directories...")
    create_models_directory()
    
    # Start the service
    print("\n🌐 Starting Flask server...")
    try:
        # Import and run the service
        from attendance_ai_service import app
        
        print("✅ ML Service started successfully!")
        print("📍 Service URL: http://localhost:5001")
        print("�� Health Check: http://localhost:5001/health")
        print("\n📊 Available endpoints:")
        print("   GET  /health - Service health check")
        print("   GET  /predict/<student_id> - Predict attendance")
        print("   GET  /analyze - Analyze patterns")
        print("   GET  /risk-students - Get risk students")
        print("   POST /train - Retrain models")
        print("\n⏹️  Press Ctrl+C to stop the service")
        
        # Run the Flask app
        app.run(host='0.0.0.0', port=5001, debug=True)
        
    except Exception as e:
        print(f"❌ Failed to start ML service: {e}")
        return False

if __name__ == '__main__':
    start_ml_service()
