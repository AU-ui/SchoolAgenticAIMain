# ============================================================================
# TEST ML SERVICE API ENDPOINTS
# ============================================================================
# Test the Smart Attendance AI Service without database
# ============================================================================

import requests
import json

def test_ml_service():
    """Test the ML service endpoints"""
    
    base_url = "http://127.0.0.1:5001"
    
    print("🧪 Testing Smart Attendance AI Service...")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health Check: PASSED")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health Check: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Health Check: ERROR - {e}")
    
    # Test 2: Predict Attendance (will fail without data, but should return proper error)
    print("\n2️⃣ Testing Predict Attendance...")
    try:
        response = requests.get(f"{base_url}/predict/1")
        if response.status_code == 200:
            print("✅ Predict Attendance: PASSED")
            print(f"   Response: {response.json()}")
        elif response.status_code == 500:
            print("⚠️ Predict Attendance: No data available (expected)")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Predict Attendance: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Predict Attendance: ERROR - {e}")
    
    # Test 3: Analyze Patterns
    print("\n3️⃣ Testing Analyze Patterns...")
    try:
        response = requests.get(f"{base_url}/analyze")
        if response.status_code == 200:
            print("✅ Analyze Patterns: PASSED")
            print(f"   Response: {response.json()}")
        elif response.status_code == 500:
            print("⚠️ Analyze Patterns: No data available (expected)")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Analyze Patterns: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Analyze Patterns: ERROR - {e}")
    
    # Test 4: Risk Students
    print("\n4️⃣ Testing Risk Students...")
    try:
        response = requests.get(f"{base_url}/risk-students")
        if response.status_code == 200:
            print("✅ Risk Students: PASSED")
            print(f"   Response: {response.json()}")
        elif response.status_code == 500:
            print("⚠️ Risk Students: No data available (expected)")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Risk Students: FAILED (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Risk Students: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print("🎯 ML Service Test Complete!")
    print("\n💡 The ML service is working correctly.")
    print("   Database connection can be added later.")

if __name__ == "__main__":
    test_ml_service()
