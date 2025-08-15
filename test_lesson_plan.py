import requests
import json

# Test lesson plan endpoint
url = "http://localhost:8000/ml/free-ai/lesson-plans/generate"
data = {
    "subject": "Science",
    "grade": "5th Grade",
    "topic": "Photosynthesis",
    "duration": 45
}

print("Testing lesson plan endpoint...")
print(f"URL: {url}")
print(f"Data: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Success: {result.get('success', False)}")
        print(f"Message: {result.get('message', 'No message')}")
        print("\nGenerated Lesson Plan Data:")
        print(json.dumps(result.get('data', {}), indent=2))
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Error: {e}")
