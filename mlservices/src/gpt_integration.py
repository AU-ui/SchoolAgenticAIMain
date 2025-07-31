import openai
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

class GPTIntegrationService:
    def __init__(self, api_key: str = None):
        # Initialize OpenAI (you'll need to set your API key)
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
            self.gpt_available = True
        else:
            self.gpt_available = False
            print("⚠️ OpenAI API key not found - using mock GPT responses")
    
    def generate_student_report(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed student progress report using GPT"""
        if not self.gpt_available:
            return self._mock_student_report(student_data)
        
        try:
            # Prepare student data for GPT
            prompt = self._create_student_report_prompt(student_data)
            
            # Call GPT API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an experienced teacher writing detailed, professional student progress reports."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            report_text = response.choices[0].message.content
            
            return {
                "success": True,
                "report": report_text,
                "student_name": student_data.get('name', 'Student'),
                "generated_at": datetime.now().isoformat(),
                "model": "gpt-3.5-turbo"
            }
            
        except Exception as e:
            return self._mock_student_report(student_data)
    
    def generate_lesson_plan(self, subject: str, grade: str, topic: str, duration: int) -> Dict[str, Any]:
        """Generate complete lesson plan using GPT"""
        if not self.gpt_available:
            return self._mock_lesson_plan(subject, grade, topic, duration)
        
        try:
            prompt = f"""
            Create a detailed lesson plan for:
            Subject: {subject}
            Grade: {grade}
            Topic: {topic}
            Duration: {duration} minutes
            
            Include:
            1. Learning objectives
            2. Materials needed
            3. Step-by-step activities
            4. Assessment methods
            5. Differentiation strategies
            
            Format as JSON.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert curriculum designer. Create detailed, engaging lesson plans."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            lesson_plan_text = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text
            try:
                lesson_plan = json.loads(lesson_plan_text)
            except:
                lesson_plan = {"content": lesson_plan_text}
            
            return {
                "success": True,
                "lesson_plan": lesson_plan,
                "subject": subject,
                "grade": grade,
                "topic": topic,
                "duration": duration,
                "generated_at": datetime.now().isoformat(),
                "model": "gpt-3.5-turbo"
            }
            
        except Exception as e:
            return self._mock_lesson_plan(subject, grade, topic, duration)
    
    def generate_parent_communication(self, context: str, student_data: Dict[str, Any], tone: str = "professional") -> Dict[str, Any]:
        """Generate personalized parent communication using GPT"""
        if not self.gpt_available:
            return self._mock_parent_communication(context, student_data, tone)
        
        try:
            prompt = f"""
            Write a {tone} communication to a parent about their child.
            
            Context: {context}
            Student Name: {student_data.get('name', 'Student')}
            Grade: {student_data.get('grade', 'Unknown')}
            Recent Performance: {student_data.get('recent_performance', 'Good')}
            Attendance: {student_data.get('attendance_rate', 'Good')}
            
            Make it personal, constructive, and actionable.
            Keep it under 200 words.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a caring, professional teacher communicating with parents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            communication_text = response.choices[0].message.content
            
            return {
                "success": True,
                "communication": communication_text,
                "student_name": student_data.get('name', 'Student'),
                "tone": tone,
                "generated_at": datetime.now().isoformat(),
                "model": "gpt-3.5-turbo"
            }
            
        except Exception as e:
            return self._mock_parent_communication(context, student_data, tone)
    
    def generate_assignment(self, subject: str, grade: str, topic: str, difficulty: str = "medium") -> Dict[str, Any]:
        """Generate educational assignments using GPT"""
        if not self.gpt_available:
            return self._mock_assignment(subject, grade, topic, difficulty)
        
        try:
            prompt = f"""
            Create an educational assignment for:
            Subject: {subject}
            Grade: {grade}
            Topic: {topic}
            Difficulty: {difficulty}
            
            Include:
            1. Clear instructions
            2. Multiple questions/problems
            3. Rubric for grading
            4. Estimated completion time
            
            Format as JSON.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert educator creating engaging, age-appropriate assignments."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            assignment_text = response.choices[0].message.content
            
            try:
                assignment = json.loads(assignment_text)
            except:
                assignment = {"content": assignment_text}
            
            return {
                "success": True,
                "assignment": assignment,
                "subject": subject,
                "grade": grade,
                "topic": topic,
                "difficulty": difficulty,
                "generated_at": datetime.now().isoformat(),
                "model": "gpt-3.5-turbo"
            }
            
        except Exception as e:
            return self._mock_assignment(subject, grade, topic, difficulty)
    
    def _create_student_report_prompt(self, student_data: Dict[str, Any]) -> str:
        """Create prompt for student report generation"""
        return f"""
        Write a detailed, professional student progress report for:
        
        Student: {student_data.get('name', 'Student')}
        Grade: {student_data.get('grade', 'Unknown')}
        Subject: {student_data.get('subject', 'General')}
        
        Performance Data:
        - Attendance: {student_data.get('attendance_rate', 'Good')}
        - Average Grade: {student_data.get('average_grade', 'B')}
        - Participation: {student_data.get('participation_rate', 'Good')}
        - Strengths: {student_data.get('strengths', 'Hardworking')}
        - Areas for Improvement: {student_data.get('areas_for_improvement', 'None noted')}
        
        Write 2-3 paragraphs highlighting achievements, progress, and recommendations.
        Use a positive, encouraging tone while being honest about areas for growth.
        """
    
    # Mock responses for when GPT is not available
    def _mock_student_report(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        name = student_data.get('name', 'Student')
        grade = student_data.get('average_grade', 'B')
        
        report = f"""
        {name} has shown consistent effort and engagement throughout this quarter. 
        With an average grade of {grade}, they demonstrate solid understanding of 
        the material. Their attendance has been excellent, and they actively 
        participate in class discussions.
        
        I've observed strong problem-solving skills and a willingness to help 
        classmates. To continue their growth, I recommend focusing on time 
        management and seeking clarification when needed.
        
        Overall, {name} is making excellent progress and I look forward to 
        their continued success in the coming quarter.
        """
        
        return {
            "success": True,
            "report": report.strip(),
            "student_name": name,
            "generated_at": datetime.now().isoformat(),
            "model": "mock-gpt"
        }
    
    def _mock_lesson_plan(self, subject: str, grade: str, topic: str, duration: int) -> Dict[str, Any]:
        lesson_plan = {
            "objective": f"Students will understand {topic} in {subject}",
            "materials": ["Whiteboard", "Worksheets", "Interactive tools"],
            "activities": [
                f"Introduction to {topic} (10 min)",
                f"Group discussion and examples (20 min)",
                f"Individual practice (10 min)",
                f"Assessment and review (5 min)"
            ],
            "assessment": f"Students will demonstrate understanding of {topic}",
            "differentiation": "Provide additional support for struggling students"
        }
        
        return {
            "success": True,
            "lesson_plan": lesson_plan,
            "subject": subject,
            "grade": grade,
            "topic": topic,
            "duration": duration,
            "generated_at": datetime.now().isoformat(),
            "model": "mock-gpt"
        }
    
    def _mock_parent_communication(self, context: str, student_data: Dict[str, Any], tone: str) -> Dict[str, Any]:
        name = student_data.get('name', 'Student')
        
        communication = f"""
        Dear Parent,
        
        I wanted to share some observations about {name}'s progress. {context}
        
        {name} has been showing good engagement in class and is making steady 
        progress. I appreciate your support in their educational journey.
        
        Please feel free to reach out if you have any questions.
        
        Best regards,
        Teacher
        """
        
        return {
            "success": True,
            "communication": communication.strip(),
            "student_name": name,
            "tone": tone,
            "generated_at": datetime.now().isoformat(),
            "model": "mock-gpt"
        }
    
    def _mock_assignment(self, subject: str, grade: str, topic: str, difficulty: str) -> Dict[str, Any]:
        assignment = {
            "title": f"{topic} Assignment",
            "instructions": f"Complete the following {topic} problems in {subject}",
            "questions": [
                f"Question 1: Basic {topic} problem",
                f"Question 2: Intermediate {topic} problem", 
                f"Question 3: Advanced {topic} problem"
            ],
            "rubric": {
                "Excellent": "All questions correct with clear explanations",
                "Good": "Most questions correct with some explanations",
                "Needs Improvement": "Several errors or missing explanations"
            },
            "estimated_time": "30 minutes"
        }
        
        return {
            "success": True,
            "assignment": assignment,
            "subject": subject,
            "grade": grade,
            "topic": topic,
            "difficulty": difficulty,
            "generated_at": datetime.now().isoformat(),
            "model": "mock-gpt"
        }

# Initialize GPT service
gpt_service = GPTIntegrationService() 