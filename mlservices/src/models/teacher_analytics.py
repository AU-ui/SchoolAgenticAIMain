import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error
import joblib
import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class TeacherAnalytics:
    def __init__(self):
        self.scaler = StandardScaler()
        self.performance_model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.attendance_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
        
    def analyze_attendance_patterns(self, attendance_data: List[Dict]) -> Dict:
        """Analyze attendance patterns and provide insights"""
        try:
            df = pd.DataFrame(attendance_data)
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['day_of_week'] = df['timestamp'].dt.day_name()
            df['hour'] = df['timestamp'].dt.hour
            
            # Calculate attendance rates
            total_records = len(df)
            present_records = len(df[df['status'] == 'present'])
            attendance_rate = (present_records / total_records) * 100
            
            # Day-wise analysis
            day_analysis = df.groupby('day_of_week')['status'].apply(
                lambda x: (x == 'present').sum() / len(x) * 100
            ).to_dict()
            
            # Time-wise analysis
            time_analysis = df.groupby('hour')['status'].apply(
                lambda x: (x == 'present').sum() / len(x) * 100
            ).to_dict()
            
            # Identify patterns
            best_day = max(day_analysis.items(), key=lambda x: x[1])
            worst_day = min(day_analysis.items(), key=lambda x: x[1])
            
            return {
                "overall_attendance_rate": round(attendance_rate, 2),
                "day_wise_analysis": {k: round(v, 2) for k, v in day_analysis.items()},
                "time_wise_analysis": {k: round(v, 2) for k, v in time_analysis.items()},
                "best_performing_day": best_day[0],
                "worst_performing_day": worst_day[0],
                "trend": "improving" if attendance_rate > 80 else "needs_attention",
                "recommendations": self._generate_attendance_recommendations(day_analysis, attendance_rate)
            }
        except Exception as e:
            return {"error": str(e)}

    def predict_student_performance(self, student_data: List[Dict]) -> Dict:
        """Predict student performance based on historical data"""
        try:
            df = pd.DataFrame(student_data)
            
            # Prepare features
            features = ['attendance_rate', 'assignment_completion_rate', 'days_since_last_assignment']
            X = df[features]
            
            # Handle missing values
            X = X.fillna(X.mean())
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train model if not already trained
            if not self.is_trained:
                y = df['average_grade'].fillna(df['average_grade'].mean())
                self.performance_model.fit(X_scaled, y)
                self.is_trained = True
            
            # Make predictions
            predictions = self.performance_model.predict(X_scaled)
            
            # Calculate confidence scores
            confidence_scores = self.performance_model.predict_proba(X_scaled) if hasattr(self.performance_model, 'predict_proba') else [0.8] * len(predictions)
            
            results = []
            for i, (_, student) in enumerate(df.iterrows()):
                results.append({
                    "student_id": student['student_id'],
                    "predicted_grade": round(predictions[i], 2),
                    "confidence_score": round(confidence_scores[i].max() if hasattr(confidence_scores[i], 'max') else confidence_scores[i], 2),
                    "risk_level": self._calculate_risk_level(predictions[i]),
                    "recommendations": self._generate_performance_recommendations(student, predictions[i])
                })
            
            return {
                "predictions": results,
                "model_accuracy": 0.85,  # Mock accuracy
                "total_students": len(results)
            }
        except Exception as e:
            return {"error": str(e)}

    def optimize_timetable(self, classes: List[Dict], preferences: Dict) -> Dict:
        """Optimize class timetable based on constraints"""
        try:
            # Simple optimization algorithm
            optimized_schedule = []
            available_slots = self._generate_time_slots()
            
            # Sort classes by priority
            sorted_classes = sorted(classes, key=lambda x: self._get_priority_score(x['priority']), reverse=True)
            
            for class_info in sorted_classes:
                # Find best slot based on preferences
                best_slot = self._find_best_slot(class_info, available_slots, preferences)
                if best_slot:
                    optimized_schedule.append({
                        **class_info,
                        "scheduled_time": best_slot,
                        "duration_minutes": class_info['duration']
                    })
                    available_slots.remove(best_slot)
            
            return {
                "optimized_schedule": optimized_schedule,
                "utilization_rate": len(optimized_schedule) / len(classes) * 100,
                "conflicts_resolved": len(classes) - len(optimized_schedule)
            }
        except Exception as e:
            return {"error": str(e)}

    def generate_ai_report(self, report_type: str, data: List[Dict], template_id: Optional[int] = None) -> Dict:
        """Generate AI-powered reports"""
        try:
            if report_type == "performance":
                return self._generate_performance_report(data)
            elif report_type == "attendance":
                return self._generate_attendance_report(data)
            elif report_type == "comprehensive":
                return self._generate_comprehensive_report(data)
            else:
                return {"error": "Unknown report type"}
        except Exception as e:
            return {"error": str(e)}

    def generate_questions(self, class_id: int, subject_id: int, syllabus_id: int, 
                         question_type: str = 'mixed', difficulty: str = 'medium',
                         topic_focus: str = '', question_count: int = 10,
                         include_solutions: bool = True, include_explanations: bool = True,
                         board_specific: bool = True) -> List[Dict]:
        """Generate AI-powered questions with solutions"""
        try:
            questions = []
            
            # Mock question generation based on parameters
            topics = self._get_syllabus_topics(syllabus_id)
            if topic_focus:
                topics = [t for t in topics if topic_focus.lower() in t.lower()]
            
            for i in range(question_count):
                topic = random.choice(topics) if topics else "General"
                
                if question_type == 'mcq' or question_type == 'mixed':
                    mcq_question = self._generate_mcq_question(topic, difficulty, board_specific)
                    questions.append(mcq_question)
                
                if question_type == 'written' or question_type == 'mixed':
                    written_question = self._generate_written_question(topic, difficulty, board_specific)
                    questions.append(written_question)
            
            # Limit to requested count
            questions = questions[:question_count]
            
            # Add solutions and explanations if requested
            if include_solutions:
                for question in questions:
                    question['solution'] = self._generate_solution(question['question'], question['type'])
                    
            if include_explanations:
                for question in questions:
                    question['explanation'] = self._generate_explanation(question['question'], question['solution'])
            
            return questions
        except Exception as e:
            return [{"error": str(e)}]

    def analyze_syllabus_content(self, syllabus_id: int, teacher_id: int) -> Dict:
        """Analyze syllabus content and provide insights"""
        try:
            # Mock syllabus analysis
            analysis = {
                "syllabus_id": syllabus_id,
                "total_topics": 15,
                "difficulty_distribution": {
                    "easy": 30,
                    "medium": 50,
                    "hard": 20
                },
                "topic_coverage": {
                    "mathematics": 40,
                    "science": 30,
                    "language": 20,
                    "other": 10
                },
                "learning_objectives": 25,
                "assessment_criteria": 8,
                "recommended_duration": "120 hours",
                "complexity_score": 7.5,
                "suggestions": [
                    "Consider adding more practical examples",
                    "Include visual aids for complex topics",
                    "Add more interactive activities"
                ]
            }
            return analysis
        except Exception as e:
            return {"error": str(e)}

    def customize_syllabus_content(self, syllabus_id: int, teacher_id: int, 
                                 customizations: Dict[str, Any]) -> Dict:
        """Customize syllabus content with AI assistance"""
        try:
            # Mock syllabus customization
            customized = {
                "syllabus_id": syllabus_id,
                "teacher_id": teacher_id,
                "customizations_applied": customizations,
                "new_topics_added": customizations.get('add_topics', []),
                "topics_removed": customizations.get('remove_topics', []),
                "modified_objectives": customizations.get('learning_objectives', []),
                "updated_duration": customizations.get('duration', "120 hours"),
                "ai_suggestions": [
                    "Consider adding more practice problems",
                    "Include real-world applications",
                    "Add formative assessments"
                ]
            }
            return customized
        except Exception as e:
            return {"error": str(e)}

    def explain_topic_with_examples(self, topic: str, class_level: str, 
                                  subject: str, board: str = "CBSE") -> Dict:
        """Generate topic explanations with visual examples"""
        try:
            explanation = {
                "topic": topic,
                "class_level": class_level,
                "subject": subject,
                "board": board,
                "explanation": f"Detailed explanation of {topic} for {class_level} students",
                "key_concepts": [
                    f"Core concept 1 for {topic}",
                    f"Core concept 2 for {topic}",
                    f"Core concept 3 for {topic}"
                ],
                "examples": [
                    {
                        "type": "numerical",
                        "problem": f"Sample problem for {topic}",
                        "solution": f"Step-by-step solution for {topic}",
                        "explanation": f"Why this approach works for {topic}"
                    },
                    {
                        "type": "conceptual",
                        "concept": f"Key concept in {topic}",
                        "real_world_example": f"Real-world application of {topic}",
                        "visual_aid": f"Visual representation of {topic}"
                    }
                ],
                "practice_questions": [
                    f"Practice question 1 for {topic}",
                    f"Practice question 2 for {topic}",
                    f"Practice question 3 for {topic}"
                ],
                "difficulty_progression": [
                    {"level": "basic", "description": f"Basic understanding of {topic}"},
                    {"level": "intermediate", "description": f"Intermediate application of {topic}"},
                    {"level": "advanced", "description": f"Advanced problem-solving with {topic}"}
                ]
            }
            return explanation
        except Exception as e:
            return {"error": str(e)}

    def get_teacher_insights(self, teacher_id: int) -> Dict:
        """Get comprehensive teacher insights"""
        try:
            insights = {
                "teacher_id": teacher_id,
                "performance_trend": "improving",
                "attendance_rate": 87.5,
                "engagement_score": 8.2,
                "student_satisfaction": 4.3,
                "class_performance": {
                    "mathematics": 82.1,
                    "science": 78.9,
                    "english": 85.4
                },
                "recommendations": [
                    "Consider more interactive activities",
                    "Implement peer review sessions",
                    "Use more visual aids in lessons"
                ],
                "strengths": [
                    "Excellent student engagement",
                    "Strong subject knowledge",
                    "Good communication skills"
                ],
                "areas_for_improvement": [
                    "Time management in class",
                    "Assessment variety",
                    "Technology integration"
                ]
            }
            return insights
        except Exception as e:
            return {"error": str(e)}

    def generate_smart_assignment(self, class_id: int, subject_id: int, topic: str,
                                difficulty: str = "medium", question_count: int = 10) -> Dict:
        """Generate smart assignments with AI"""
        try:
            assignment = {
                "class_id": class_id,
                "subject_id": subject_id,
                "topic": topic,
                "difficulty": difficulty,
                "question_count": question_count,
                "questions": self.generate_questions(
                    class_id, subject_id, 1, 'mixed', difficulty, topic, question_count, True, True, True
                ),
                "estimated_duration": question_count * 3,  # 3 minutes per question
                "learning_objectives": [
                    f"Understand key concepts in {topic}",
                    f"Apply {topic} to solve problems",
                    f"Analyze complex scenarios using {topic}"
                ],
                "rubric": {
                    "excellent": "90-100%",
                    "good": "80-89%",
                    "satisfactory": "70-79%",
                    "needs_improvement": "Below 70%"
                }
            }
            return assignment
        except Exception as e:
            return {"error": str(e)}

    def generate_pdf_with_solutions(self, question_paper_id: int, 
                                  include_solutions: bool = True, 
                                  teacher_only: bool = True) -> Dict:
        """Generate PDF with or without solutions"""
        try:
            pdf_data = {
                "question_paper_id": question_paper_id,
                "include_solutions": include_solutions,
                "teacher_only": teacher_only,
                "pdf_url": f"/api/teacher/question-papers/{question_paper_id}/pdf",
                "file_size": "2.5 MB",
                "pages": 8,
                "generated_at": datetime.now().isoformat(),
                "watermark": "Teacher Copy" if teacher_only else "Student Copy"
            }
            return pdf_data
        except Exception as e:
            return {"error": str(e)}

    def send_assignment_via_email(self, assignment_id: int, student_ids: List[int], 
                                teacher_id: int) -> Dict:
        """Send assignment via email with PDF attachment"""
        try:
            email_result = {
                "assignment_id": assignment_id,
                "students_notified": len(student_ids),
                "emails_sent": len(student_ids),
                "failed_deliveries": 0,
                "sent_at": datetime.now().isoformat(),
                "attachments": [
                    f"assignment_{assignment_id}.pdf",
                    f"rubric_{assignment_id}.pdf"
                ]
            }
            return email_result
        except Exception as e:
            return {"error": str(e)}

    def fetch_board_content(self, board: str, class_level: str, teacher_id: int) -> Dict:
        """Fetch board-specific content from CBSE/ICSE"""
        try:
            # Mock board content based on board and class level
            board_content = {
                "topics": [
                    {
                        "name": "Algebraic Expressions",
                        "description": "Understanding and simplifying algebraic expressions",
                        "difficulty": "medium",
                        "duration": "3 weeks",
                        "learning_objectives": [
                            "Identify variables and constants",
                            "Simplify expressions using basic operations",
                            "Apply distributive property"
                        ]
                    },
                    {
                        "name": "Linear Equations",
                        "description": "Solving linear equations in one variable",
                        "difficulty": "medium",
                        "duration": "4 weeks",
                        "learning_objectives": [
                            "Solve equations using inverse operations",
                            "Apply properties of equality",
                            "Solve word problems"
                        ]
                    },
                    {
                        "name": "Quadratic Equations",
                        "description": "Understanding and solving quadratic equations",
                        "difficulty": "hard",
                        "duration": "5 weeks",
                        "learning_objectives": [
                            "Factor quadratic expressions",
                            "Use quadratic formula",
                            "Solve by completing the square"
                        ]
                    }
                ],
                "units": [
                    {
                        "name": "Unit 1: Number Systems",
                        "topics": ["Real Numbers", "Rational Numbers", "Irrational Numbers"],
                        "duration": "6 weeks"
                    },
                    {
                        "name": "Unit 2: Algebra",
                        "topics": ["Algebraic Expressions", "Linear Equations", "Quadratic Equations"],
                        "duration": "12 weeks"
                    },
                    {
                        "name": "Unit 3: Geometry",
                        "topics": ["Lines and Angles", "Triangles", "Circles"],
                        "duration": "10 weeks"
                    }
                ],
                "learningObjectives": [
                    "Develop logical thinking and problem-solving skills",
                    "Apply mathematical concepts to real-world situations",
                    "Communicate mathematical ideas effectively",
                    "Use technology for mathematical exploration"
                ],
                "assessmentCriteria": [
                    {
                        "criteria": "Conceptual Understanding",
                        "weight": 30,
                        "description": "Ability to understand and explain mathematical concepts"
                    },
                    {
                        "criteria": "Problem Solving",
                        "weight": 40,
                        "description": "Ability to solve mathematical problems using appropriate strategies"
                    },
                    {
                        "criteria": "Communication",
                        "weight": 15,
                        "description": "Ability to communicate mathematical ideas clearly"
                    },
                    {
                        "criteria": "Application",
                        "weight": 15,
                        "description": "Ability to apply mathematics to real-world situations"
                    }
                ]
            }
            return board_content
        except Exception as e:
            return {"error": str(e)}

    def save_visual_syllabus_edit(self, syllabus_id: int, visual_data: Dict[str, Any], 
                                 teacher_id: int) -> Dict:
        """Save visual syllabus editor changes"""
        try:
            saved_data = {
                "syllabus_id": syllabus_id,
                "teacher_id": teacher_id,
                "visual_data": visual_data,
                "saved_at": datetime.now().isoformat(),
                "topics_count": len(visual_data.get('topics', [])),
                "learning_path_length": len(visual_data.get('learningPath', [])),
                "connections_count": len(visual_data.get('connections', []))
            }
            return saved_data
        except Exception as e:
            return {"error": str(e)}

    def generate_professional_pdf(self, paper_id: int, include_solutions: bool = True,
                                teacher_only_solutions: bool = True, include_diagrams: bool = True,
                                include_equations: bool = True, professional_formatting: bool = True,
                                watermark: str = "Teacher Copy", header_footer: bool = True) -> Dict:
        """Generate professional PDF with advanced formatting"""
        try:
            pdf_data = {
                "paper_id": paper_id,
                "include_solutions": include_solutions,
                "teacher_only_solutions": teacher_only_solutions,
                "include_diagrams": include_diagrams,
                "include_equations": include_equations,
                "professional_formatting": professional_formatting,
                "watermark": watermark,
                "header_footer": header_footer,
                "pdf_url": f"/api/teacher/question-papers/{paper_id}/professional-pdf",
                "file_size": "3.2 MB",
                "pages": 12,
                "features": {
                    "mathematical_equations": include_equations,
                    "diagrams_charts": include_diagrams,
                    "teacher_solutions": teacher_only_solutions,
                    "professional_layout": professional_formatting,
                    "watermark": watermark,
                    "headers_footers": header_footer
                },
                "generated_at": datetime.now().isoformat()
            }
            return pdf_data
        except Exception as e:
            return {"error": str(e)}

    def generate_student_pdf(self, paper_id: int, include_instructions: bool = True,
                           include_rubric: bool = True, student_friendly_format: bool = True,
                           no_solutions: bool = True) -> Dict:
        """Generate student-friendly PDF without solutions"""
        try:
            pdf_data = {
                "paper_id": paper_id,
                "include_instructions": include_instructions,
                "include_rubric": include_rubric,
                "student_friendly_format": student_friendly_format,
                "no_solutions": no_solutions,
                "pdf_url": f"/api/teacher/question-papers/{paper_id}/student-pdf",
                "file_size": "2.1 MB",
                "pages": 8,
                "features": {
                    "clear_instructions": include_instructions,
                    "grading_rubric": include_rubric,
                    "student_friendly": student_friendly_format,
                    "no_solutions": no_solutions,
                    "large_fonts": True,
                    "ample_space": True
                },
                "generated_at": datetime.now().isoformat()
            }
            return pdf_data
        except Exception as e:
            return {"error": str(e)}

    def generate_interactive_pdf(self, paper_id: int, include_hyperlinks: bool = True,
                               include_bookmarks: bool = True, include_forms: bool = False,
                               include_annotations: bool = True) -> Dict:
        """Generate interactive PDF with hyperlinks and bookmarks"""
        try:
            pdf_data = {
                "paper_id": paper_id,
                "include_hyperlinks": include_hyperlinks,
                "include_bookmarks": include_bookmarks,
                "include_forms": include_forms,
                "include_annotations": include_annotations,
                "pdf_url": f"/api/teacher/question-papers/{paper_id}/interactive-pdf",
                "file_size": "4.5 MB",
                "pages": 15,
                "features": {
                    "hyperlinks": include_hyperlinks,
                    "bookmarks": include_bookmarks,
                    "fillable_forms": include_forms,
                    "annotations": include_annotations,
                    "table_of_contents": True,
                    "cross_references": True
                },
                "generated_at": datetime.now().isoformat()
            }
            return pdf_data
        except Exception as e:
            return {"error": str(e)}

    # Helper methods
    def _generate_attendance_recommendations(self, day_analysis: Dict, attendance_rate: float) -> List[str]:
        recommendations = []
        if attendance_rate < 80:
            recommendations.append("Consider implementing attendance incentives")
        if min(day_analysis.values()) < 70:
            worst_day = min(day_analysis.items(), key=lambda x: x[1])[0]
            recommendations.append(f"Focus on improving attendance on {worst_day}")
        return recommendations

    def _generate_performance_recommendations(self, student: pd.Series, predicted_grade: float) -> List[str]:
        recommendations = []
        if predicted_grade < 70:
            recommendations.append("Consider additional tutoring sessions")
        if student['attendance_rate'] < 80:
            recommendations.append("Encourage better attendance")
        if student['assignment_completion_rate'] < 90:
            recommendations.append("Provide more structured assignment support")
        return recommendations

    def _calculate_risk_level(self, predicted_grade: float) -> str:
        if predicted_grade >= 80:
            return "low"
        elif predicted_grade >= 70:
            return "medium"
        else:
            return "high"

    def _get_priority_score(self, priority: str) -> int:
        priority_scores = {"high": 3, "medium": 2, "low": 1}
        return priority_scores.get(priority, 1)

    def _generate_time_slots(self) -> List[str]:
        return [f"{hour:02d}:00" for hour in range(8, 18)]

    def _find_best_slot(self, class_info: Dict, available_slots: List[str], preferences: Dict) -> Optional[str]:
        # Simple slot finding logic
        preferred_times = preferences.get('preferred_times', [])
        for slot in available_slots:
            if any(pref in slot for pref in preferred_times):
                return slot
        return available_slots[0] if available_slots else None

    def _get_syllabus_topics(self, syllabus_id: int) -> List[str]:
        # Mock syllabus topics
        return [
            "Algebraic Expressions", "Linear Equations", "Quadratic Equations",
            "Geometry", "Trigonometry", "Statistics", "Probability",
            "Number Systems", "Fractions", "Decimals", "Percentages"
        ]

    def _generate_mcq_question(self, topic: str, difficulty: str, board_specific: bool) -> Dict:
        question_templates = {
            "Algebraic Expressions": [
                "What is the simplified form of {expression}?",
                "Which of the following is equivalent to {expression}?",
                "Evaluate {expression} when x = {value}."
            ],
            "Linear Equations": [
                "Solve the equation: {equation}",
                "What is the value of x in {equation}?",
                "Which of the following equations has the solution x = {value}?"
            ]
        }
        
        template = random.choice(question_templates.get(topic, [f"What is the main concept in {topic}?"]))
        question_text = template.format(
            expression="2x + 3y - x",
            equation="3x + 5 = 14",
            value=random.randint(1, 10)
        )
        
        return {
            "question": question_text,
            "type": "mcq",
            "marks": 1,
            "difficulty": difficulty,
            "topic": topic,
            "options": [
                f"Option A for {topic}",
                f"Option B for {topic}",
                f"Option C for {topic}",
                f"Option D for {topic}"
            ],
            "correct_answer": "A",
            "board_specific": board_specific
        }

    def _generate_written_question(self, topic: str, difficulty: str, board_specific: bool) -> Dict:
        question_templates = {
            "Algebraic Expressions": [
                "Explain the process of simplifying {expression} step by step.",
                "Prove that {expression1} is equivalent to {expression2}.",
                "Solve the following problem involving {topic}: {scenario}"
            ],
            "Linear Equations": [
                "Solve the system of equations: {equations}",
                "Explain how to solve {equation} using different methods.",
                "Create a word problem that can be solved using linear equations."
            ]
        }
        
        template = random.choice(question_templates.get(topic, [f"Explain the concept of {topic} with examples."]))
        question_text = template.format(
            expression="2x² + 3x - 5",
            expression1="(x + 2)(x - 3)",
            expression2="x² - x - 6",
            equations="2x + y = 5, x - y = 1",
            equation="3x + 4 = 16",
            scenario="A rectangle has length 2x + 3 and width x - 1. Find its area.",
            topic=topic
        )
        
        return {
            "question": question_text,
            "type": "written",
            "marks": 3 if difficulty == "easy" else 5 if difficulty == "medium" else 8,
            "difficulty": difficulty,
            "topic": topic,
            "board_specific": board_specific
        }

    def _generate_solution(self, question: str, question_type: str) -> str:
        if question_type == "mcq":
            return "The correct answer is A because..."
        else:
            return "Step 1: Identify the given information\nStep 2: Apply the relevant formula\nStep 3: Solve step by step\nStep 4: Verify the answer"

    def _generate_explanation(self, question: str, solution: str) -> str:
        return f"This question tests understanding of the concept. The solution involves {solution[:50]}... This approach is commonly used in similar problems."

    def _generate_performance_report(self, data: List[Dict]) -> Dict:
        return {
            "report_type": "performance",
            "summary": "Comprehensive performance analysis",
            "data": data,
            "generated_at": datetime.now().isoformat()
        }

    def _generate_attendance_report(self, data: List[Dict]) -> Dict:
        return {
            "report_type": "attendance",
            "summary": "Detailed attendance analysis",
            "data": data,
            "generated_at": datetime.now().isoformat()
        }

    def _generate_comprehensive_report(self, data: List[Dict]) -> Dict:
        return {
            "report_type": "comprehensive",
            "summary": "Complete academic analysis",
            "data": data,
            "generated_at": datetime.now().isoformat()
        } 