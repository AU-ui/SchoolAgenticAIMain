import requests
import json

def test_assignment():
    url = "http://localhost:8000/ml/free-ai/assignments/generate"
    data = {
        "subject": "English",
        "grade": "8th Grade",
        "topic": "Essay Writing",
        "difficulty": "medium"
    }
    
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Questions: {result['data']['questions']}")
    print(f"Questions type: {type(result['data']['questions'])}")

if __name__ == "__main__":
    test_assignment()
