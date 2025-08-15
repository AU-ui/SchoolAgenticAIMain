#!/usr/bin/env python3
"""
Test script for board-specific assignment generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.free_ai_generator import FreeAIContentGenerator

def test_board_specific_assignments():
    """Test board-specific assignment generation"""
    
    generator = FreeAIContentGenerator()
    
    # Test cases
    test_cases = [
        {
            "board": "CBSE",
            "subject": "Mathematics", 
            "grade": "12th Grade",
            "topic": "3D Plane Equation",
            "difficulty": "medium"
        },
        {
            "board": "ICSE",
            "subject": "Mathematics",
            "grade": "12th Grade", 
            "topic": "3D Plane Equation",
            "difficulty": "hard"
        },
        {
            "board": "CBSE",
            "subject": "Mathematics",
            "grade": "12th Grade",
            "topic": "Vector Algebra", 
            "difficulty": "easy"
        }
    ]
    
    print("🧪 Testing Board-Specific Assignment Generation")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['board']} - {test_case['subject']} - {test_case['topic']}")
        print("-" * 50)
        
        try:
            result = generator.generate_assignment(
                board=test_case['board'],
                subject=test_case['subject'],
                grade=test_case['grade'],
                topic=test_case['topic'],
                difficulty=test_case['difficulty']
            )
            
            if result.get('success'):
                assignment = result.get('assignment', {})
                
                print(f"✅ Title: {assignment.get('title', 'N/A')}")
                print(f"📋 Board: {assignment.get('board', 'N/A')}")
                print(f"📚 Subject: {assignment.get('subject', 'N/A')}")
                print(f"🎓 Grade: {assignment.get('grade_level', 'N/A')}")
                print(f"🎯 Difficulty: {assignment.get('difficulty', 'N/A')}")
                print(f"📝 Instructions: {assignment.get('instructions', 'N/A')}")
                print(f"📊 Total Points: {assignment.get('total_points', 'N/A')}")
                
                print(f"\n❓ Questions ({len(assignment.get('questions', []))}):")
                for j, question in enumerate(assignment.get('questions', []), 1):
                    print(f"  {j}. {question.get('question', 'N/A')} ({question.get('points', 0)} points)")
                
                print(f"\n🎯 Learning Objectives:")
                for objective in assignment.get('learning_objectives', []):
                    print(f"  • {objective}")
                    
            else:
                print(f"❌ Generation failed: {result.get('message', 'Unknown error')}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("✅ Board-specific assignment generation test completed!")

if __name__ == "__main__":
    test_board_specific_assignments()
