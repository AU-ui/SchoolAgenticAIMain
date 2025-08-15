#!/usr/bin/env python3
"""
Test script to check assignment generation
"""
import requests
import json

def test_assignment_generation():
    url = "http://localhost:8000/ml/free-ai/assignments/generate"
    payload = {
        "subject": "Mathematics",
        "grade": "Class 8",
        "topic": "Algebraic Expressions",
        "difficulty": "medium"
    }
    
    try:
        response = requests.post(url, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        
        if response.status_code == 200:
            data = response.json()
            print("\n=== ASSIGNMENT DATA ===")
            print(json.dumps(data, indent=2))
            
            if data.get('success'):
                assignment = data.get('data', {})
                print(f"\n=== KEY FIELDS ===")
                print(f"Title: {assignment.get('title')}")
                print(f"Subject: {assignment.get('subject')}")
                print(f"Grade Level: {assignment.get('grade_level')}")
                print(f"Instructions: {assignment.get('instructions')}")
                print(f"Questions count: {len(assignment.get('questions', []))}")
                print(f"Rubric count: {len(assignment.get('rubric', []))}")
                
                print(f"\n=== QUESTIONS ===")
                for i, q in enumerate(assignment.get('questions', [])):
                    print(f"Q{i+1}: {q.get('question')}")
                
                print(f"\n=== RUBRIC ===")
                for i, r in enumerate(assignment.get('rubric', [])):
                    print(f"Criteria {i+1}: {r.get('criteria')}")
            else:
                print(f"Error: {data.get('message')}")
        else:
            print(f"HTTP Error: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_assignment_generation()
