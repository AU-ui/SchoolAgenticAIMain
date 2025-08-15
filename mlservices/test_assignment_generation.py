#!/usr/bin/env python3

from src.free_ai_generator import free_ai_generator

def test_assignment_generation():
    print("🧪 Testing ML Model Assignment Generation...")
    print("=" * 50)
    
    # Test 1: 1857 Revolt Assignment
    print("\n📚 Test 1: History - 1857 Revolt")
    result = free_ai_generator.generate_assignment('History', '8th Grade', '1857 revolt', 'medium')
    
    if result.get('success'):
        print("✅ Success: Assignment generated successfully!")
        assignment = result.get('assignment', {})
        print(f"📝 Title: {assignment.get('title')}")
        print(f"📊 Total Points: {assignment.get('total_points')}")
        print(f"⏱️ Estimated Time: {assignment.get('estimated_time')}")
        
        print("\n❓ Questions Generated:")
        questions = assignment.get('questions', [])
        for i, q in enumerate(questions, 1):
            print(f"  {i}. {q.get('question')} ({q.get('points')} points)")
        
        # Check if questions are specific to 1857 revolt
        specific_keywords = ['1857', 'revolt', 'sepoy', 'british', 'colonial', 'india']
        specific_count = sum(1 for q in questions if any(keyword in q.get('question', '').lower() for keyword in specific_keywords))
        print(f"\n🎯 Specificity Check: {specific_count}/{len(questions)} questions contain 1857 revolt keywords")
        
    else:
        print("❌ Failed: Assignment generation failed")
    
    # Test 2: Different topic
    print("\n" + "=" * 50)
    print("\n📚 Test 2: Mathematics - Algebra")
    result2 = free_ai_generator.generate_assignment('Mathematics', '9th Grade', 'Algebra', 'medium')
    
    if result2.get('success'):
        print("✅ Success: Math assignment generated successfully!")
        assignment2 = result2.get('assignment', {})
        print(f"📝 Title: {assignment2.get('title')}")
        
        print("\n❓ Math Questions Generated:")
        questions2 = assignment2.get('questions', [])
        for i, q in enumerate(questions2, 1):
            print(f"  {i}. {q.get('question')} ({q.get('points')} points)")
    
    print("\n" + "=" * 50)
    print("🎉 ML Model Configuration Test Complete!")

if __name__ == "__main__":
    test_assignment_generation()
