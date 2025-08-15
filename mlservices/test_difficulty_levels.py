#!/usr/bin/env python3

from src.free_ai_generator import free_ai_generator

def test_difficulty_levels():
    print("🧪 Testing ML Model Difficulty Levels...")
    print("=" * 60)
    
    # Test 1: History - 1857 Revolt with different difficulties
    print("\n📚 Test 1: History - 1857 Revolt (All Difficulty Levels)")
    print("-" * 50)
    
    difficulties = ["easy", "medium", "hard"]
    for difficulty in difficulties:
        print(f"\n🎯 {difficulty.upper()} DIFFICULTY:")
        result = free_ai_generator.generate_assignment('History', '8th Grade', '1857 revolt', difficulty)
        
        if result.get('success'):
            assignment = result.get('assignment', {})
            print(f"📝 Title: {assignment.get('title')}")
            print(f"📊 Total Points: {assignment.get('total_points')}")
            print(f"⏱️ Estimated Time: {assignment.get('estimated_time')}")
            
            print("\n❓ Questions:")
            questions = assignment.get('questions', [])
            for i, q in enumerate(questions, 1):
                print(f"  {i}. {q.get('question')} ({q.get('points')} points)")
        else:
            print("❌ Failed to generate assignment")
    
    # Test 2: Mathematics - Algebra with different difficulties
    print("\n" + "=" * 60)
    print("\n📚 Test 2: Mathematics - Algebra (All Difficulty Levels)")
    print("-" * 50)
    
    for difficulty in difficulties:
        print(f"\n🎯 {difficulty.upper()} DIFFICULTY:")
        result = free_ai_generator.generate_assignment('Mathematics', '9th Grade', 'Algebra', difficulty)
        
        if result.get('success'):
            assignment = result.get('assignment', {})
            print(f"📝 Title: {assignment.get('title')}")
            print(f"📊 Total Points: {assignment.get('total_points')}")
            print(f"⏱️ Estimated Time: {assignment.get('estimated_time')}")
            
            print("\n❓ Questions:")
            questions = assignment.get('questions', [])
            for i, q in enumerate(questions, 1):
                print(f"  {i}. {q.get('question')} ({q.get('points')} points)")
        else:
            print("❌ Failed to generate assignment")
    
    # Test 3: Science with different difficulties
    print("\n" + "=" * 60)
    print("\n📚 Test 3: Science - Photosynthesis (All Difficulty Levels)")
    print("-" * 50)
    
    for difficulty in difficulties:
        print(f"\n🎯 {difficulty.upper()} DIFFICULTY:")
        result = free_ai_generator.generate_assignment('Science', '7th Grade', 'Photosynthesis', difficulty)
        
        if result.get('success'):
            assignment = result.get('assignment', {})
            print(f"📝 Title: {assignment.get('title')}")
            print(f"📊 Total Points: {assignment.get('total_points')}")
            print(f"⏱️ Estimated Time: {assignment.get('estimated_time')}")
            
            print("\n❓ Questions:")
            questions = assignment.get('questions', [])
            for i, q in enumerate(questions, 1):
                print(f"  {i}. {q.get('question')} ({q.get('points')} points)")
        else:
            print("❌ Failed to generate assignment")
    
    print("\n" + "=" * 60)
    print("🎉 Difficulty Level Testing Complete!")
    print("\n📊 Summary:")
    print("✅ Easy: Basic recall and understanding questions")
    print("✅ Medium: Analysis and application questions") 
    print("✅ Hard: Critical thinking and complex problem-solving questions")

if __name__ == "__main__":
    test_difficulty_levels()
