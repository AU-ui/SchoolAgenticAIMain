import random
import json
from datetime import datetime
from typing import Dict, List, Any

class SimpleFreeAIGenerator:
    def __init__(self):
        self.student_names = [
            "Alex", "Sarah", "Michael", "Emma", "David", "Sophia", "James", "Olivia",
            "William", "Ava", "Benjamin", "Isabella", "Lucas", "Mia", "Henry", "Charlotte"
        ]
        
        self.subjects = [
            "Mathematics", "Science", "English", "History", "Geography", "Art", "Music"
        ]
        
        self.positive_adjectives = [
            "excellent", "outstanding", "remarkable", "impressive", "dedicated", "enthusiastic",
            "hardworking", "motivated", "creative", "thoughtful", "organized", "reliable"
        ]
        
        self.improvement_areas = [
            "time management", "organization skills", "class participation", "homework completion",
            "study habits", "attention to detail", "critical thinking", "communication skills"
        ]
        
        self.achievements = [
            "shows great improvement", "demonstrates strong understanding", "excels in group work",
            "displays excellent problem-solving skills", "shows creativity in assignments",
            "maintains consistent effort", "participates actively in discussions"
        ]
        
        self.recommendations = [
            "Continue practicing regularly", "Focus on completing assignments on time",
            "Participate more in class discussions", "Review material before tests",
            "Ask questions when clarification is needed", "Work on organization skills",
            "Practice time management", "Engage in additional reading"
        ]

    def generate_student_report(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a student progress report"""
        name = student_data.get('name', random.choice(self.student_names))
        subject = student_data.get('subject', random.choice(self.subjects))
        grade = student_data.get('grade', 'B+')
        attendance_rate = student_data.get('attendance_rate', 0.9)
        
        # Calculate attendance percentage
        attendance_percentage = int(attendance_rate * 100)
        
        # Generate report content
        strengths = random.sample(self.positive_adjectives, 3)
        areas_for_improvement = random.sample(self.improvement_areas, 2)
        achievements = random.sample(self.achievements, 3)
        recommendations = random.sample(self.recommendations, 3)
        
        report = {
            "student_name": name,
            "subject": subject,
            "grade": grade,
            "attendance_percentage": attendance_percentage,
            "report_date": datetime.now().strftime("%B %d, %Y"),
            "teacher_comments": {
                "strengths": strengths,
                "areas_for_improvement": areas_for_improvement,
                "achievements": achievements,
                "recommendations": recommendations
            },
            "academic_performance": {
                "overall_grade": grade,
                "class_participation": f"{random.randint(75, 95)}%",
                "homework_completion": f"{random.randint(80, 100)}%",
                "test_average": f"{random.randint(75, 95)}%"
            },
            "next_steps": [
                "Continue current study habits",
                "Focus on identified improvement areas",
                "Maintain regular attendance",
                "Seek additional help when needed"
            ],
            "generated_at": datetime.now().isoformat(),
            "model": "simple-free-ai-generator"
        }
        
        return report

    def generate_lesson_plan(self, subject: str, grade: str, topic: str, duration: int) -> Dict[str, Any]:
        """Generate a lesson plan"""
        # Create lesson structure with timing
        lesson_structure = [
            {
                "time": "5 minutes",
                "activity": "Introduction and Warm-up",
                "description": f"Introduce the topic of {topic} and engage students with a brief discussion"
            },
            {
                "time": "15 minutes",
                "activity": "Direct Instruction",
                "description": f"Present key concepts of {topic} using visual aids and examples"
            },
            {
                "time": "15 minutes",
                "activity": "Guided Practice",
                "description": f"Students work through examples and problems related to {topic}"
            },
            {
                "time": "10 minutes",
                "activity": "Assessment and Closure",
                "description": f"Review key points and assess student understanding"
            }
        ]
        
        materials = [
            "Whiteboard and markers",
            "Textbook and supplementary materials",
            "Worksheets and practice problems",
            "Digital resources and videos"
        ]
        
        differentiation_strategies = [
            "Provide additional support for struggling students",
            "Offer extension activities for advanced learners",
            "Use visual aids and hands-on materials"
        ]
        
        lesson_plan = {
            "title": f"{topic} Lesson Plan",
            "subject": subject,
            "grade": grade,
            "topic": topic,
            "duration": duration,
            "objective": f"Students will understand the fundamental concepts of {topic} and be able to apply this knowledge to solve problems and analyze different contexts.",
            "materials": materials,
            "lesson_structure": lesson_structure,
            "differentiation_strategies": differentiation_strategies,
            "assessment": "Students will be assessed through class participation, worksheet completion, group discussion, and individual practice activities.",
            "homework_assignment": {
                "title": f"{topic} Practice Assignment",
                "description": f"Complete practice problems related to {topic} and prepare for next class discussion",
                "estimated_time": "20-30 minutes",
                "due_date": "Next class period"
            },
            "generated_at": datetime.now().isoformat(),
            "model": "simple-free-ai-generator"
        }
        
        return lesson_plan

    def generate_assignment(self, subject: str, grade: str, topic: str, difficulty: str = "medium") -> Dict[str, Any]:
        """Generate an educational assignment"""
        num_questions = 3 if difficulty == "easy" else 4 if difficulty == "medium" else 5
        
        questions = [
            f"Explain the concept of {topic} in your own words.",
            f"Provide three examples of {topic} in real-world situations.",
            f"Compare and contrast different approaches to {topic}.",
            f"Create a problem related to {topic} and solve it.",
            f"Analyze the importance of {topic} in {subject}."
        ]
        
        rubric = {
            "Excellent": "Complete understanding with detailed explanations",
            "Good": "Solid understanding with adequate explanations",
            "Satisfactory": "Basic understanding with some explanations",
            "Needs Improvement": "Limited understanding or missing explanations"
        }
        
        assignment = {
            "subject": subject,
            "grade": grade,
            "topic": topic,
            "difficulty": difficulty,
            "due_date": "Next class period",
            "estimated_time": f"{num_questions * 10} minutes",
            "questions": questions[:num_questions],
            "rubric": rubric,
            "instructions": f"Complete all questions related to {topic}. Show your work and provide detailed explanations.",
            "learning_objectives": [
                f"Demonstrate understanding of {topic}",
                f"Apply {topic} concepts to new situations",
                f"Communicate understanding clearly"
            ],
            "generated_at": datetime.now().isoformat(),
            "model": "simple-free-ai-generator"
        }
        
        return assignment

    def generate_curriculum_plan(self, subject: str, grade: str, duration_weeks: int) -> Dict[str, Any]:
        """Generate a curriculum plan"""
        units = []
        for week in range(1, duration_weeks + 1):
            units.append({
                "week": week,
                "topic": f"Unit {week}: Advanced {subject} Concepts",
                "objectives": [
                    f"Master fundamental {subject} principles",
                    f"Apply {subject} knowledge to complex problems",
                    f"Develop critical thinking skills"
                ],
                "activities": [
                    "Lecture and discussion",
                    "Hands-on practice",
                    "Group projects",
                    "Individual assessments"
                ]
            })
        
        curriculum = {
            "subject": subject,
            "grade": grade,
            "duration_weeks": duration_weeks,
            "units": units,
            "assessment_strategy": {
                "formative": "Weekly quizzes and class participation",
                "summative": "Unit tests and final project",
                "ongoing": "Homework assignments and classwork"
            },
            "resources": [
                "Textbook and supplementary materials",
                "Digital learning platforms",
                "Hands-on materials and manipulatives",
                "Assessment tools and rubrics"
            ],
            "generated_at": datetime.now().isoformat(),
            "model": "simple-free-ai-generator"
        }
        
        return curriculum

    def generate_student_portfolio(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a student portfolio"""
        name = student_data.get('name', random.choice(self.student_names))
        grade = student_data.get('grade', 'B+')
        subjects = student_data.get('subjects', self.subjects[:4])
        
        portfolio = {
            "student_name": name,
            "grade_level": grade,
            "academic_year": "2024-2025",
            "subjects": subjects,
            "achievements": [
                "Outstanding academic performance",
                "Active participation in class discussions",
                "Excellent problem-solving skills",
                "Strong leadership qualities"
            ],
            "projects": [
                {
                    "title": f"Research Project in {subjects[0]}",
                    "description": f"Comprehensive study of advanced {subjects[0]} concepts",
                    "grade": "A",
                    "completion_date": "December 2024"
                },
                {
                    "title": f"Creative Assignment in {subjects[1]}",
                    "description": f"Innovative approach to {subjects[1]} learning",
                    "grade": "A-",
                    "completion_date": "November 2024"
                }
            ],
            "skills_developed": [
                "Critical thinking and analysis",
                "Effective communication",
                "Collaborative teamwork",
                "Independent research"
            ],
            "goals_for_next_semester": [
                "Maintain high academic standards",
                "Take on leadership roles in group projects",
                "Explore advanced topics in favorite subjects",
                "Develop additional technical skills"
            ],
            "teacher_recommendations": random.sample(self.recommendations, 3),
            "generated_at": datetime.now().isoformat(),
            "model": "simple-free-ai-generator"
        }
        
        return portfolio

    def generate_parent_newsletter(self, school_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a parent newsletter"""
        school_name = school_data.get('school_name', 'Excellence Academy')
        contact_info = school_data.get('contact_info', {
            'phone': '(555) 123-4567',
            'email': 'info@excellenceacademy.edu'
        })
        
        newsletter = {
            "school_name": school_name,
            "newsletter_date": datetime.now().strftime("%B %Y"),
            "principal_message": f"Welcome to another exciting month at {school_name}! We are proud of our students' continued growth and achievements.",
            "upcoming_events": [
                {"date": "December 15", "event": "Winter Concert"},
                {"date": "December 20", "event": "Holiday Break Begins"},
                {"date": "January 8", "event": "Classes Resume"},
                {"date": "January 15", "event": "Parent-Teacher Conferences"}
            ],
            "academic_highlights": [
                "Students achieved 95% attendance rate this month",
                "Science fair projects showcased innovative thinking",
                "Math competition winners announced",
                "Reading program participation increased by 20%"
            ],
            "parent_tips": [
                "Establish a consistent homework routine",
                "Encourage daily reading at home",
                "Stay in regular communication with teachers",
                "Support your child's extracurricular activities"
            ],
            "important_dates": [
                {"date": "December 15", "description": "Report cards distributed"},
                {"date": "December 20", "description": "Early dismissal for holiday break"},
                {"date": "January 8", "description": "New semester begins"}
            ],
            "contact_information": contact_info,
            "generated_at": datetime.now().isoformat(),
            "model": "simple-free-ai-generator"
        }
        
        return newsletter

# Initialize the simple free AI generator
simple_free_ai_generator = SimpleFreeAIGenerator()
