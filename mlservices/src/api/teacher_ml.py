from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from ..models.teacher_analytics import TeacherAnalytics

router = APIRouter(prefix="/ml/teacher", tags=["Teacher ML Services"])
analytics = TeacherAnalytics()

class AttendanceData(BaseModel):
    student_id: int
    status: str
    timestamp: str
    class_id: int

class StudentData(BaseModel):
    student_id: int
    attendance_rate: float
    assignment_completion_rate: float
    average_grade: float
    days_since_last_assignment: int
    total_assignments: int
    final_grade: Optional[float] = None

class ClassScheduleData(BaseModel):
    id: int
    subject: str
    duration: int
    priority: str

class TeacherPreferences(BaseModel):
    preferred_subjects: List[str] = []
    preferred_times: List[str] = []
    max_classes_per_day: int = 6

class ReportRequest(BaseModel):
    report_type: str
    data: List[Dict[str, Any]]
    template_id: Optional[int] = None

class QuestionGenerationRequest(BaseModel):
    class_id: int
    subject_id: int
    syllabus_id: int
    teacher_id: int
    config: Dict[str, Any]

class QuestionData(BaseModel):
    question: str
    type: str  # mcq, written
    marks: int
    difficulty: str
    topic: str
    options: Optional[List[str]] = None
    solution: Optional[str] = None
    explanation: Optional[str] = None
    board_specific: bool = True

@router.post("/attendance/analyze")
async def analyze_attendance_patterns(attendance_data: List[AttendanceData]):
    """Analyze attendance patterns and provide insights"""
    try:
        # Convert to format expected by analytics
        data = [item.dict() for item in attendance_data]
        patterns = analytics.analyze_attendance_patterns(data)
        
        return {
            "success": True,
            "data": patterns,
            "message": "Attendance analysis completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/performance/predict")
async def predict_student_performance(student_data: List[StudentData]):
    """Predict student performance based on historical data"""
    try:
        data = [item.dict() for item in student_data]
        predictions = analytics.predict_student_performance(data)
        
        return {
            "success": True,
            "data": predictions,
            "message": "Performance prediction completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.post("/timetable/optimize")
async def optimize_timetable(
    class_data: List[ClassScheduleData],
    teacher_preferences: TeacherPreferences
):
    """Optimize class timetable based on constraints"""
    try:
        classes = [item.dict() for item in class_data]
        preferences = teacher_preferences.dict()
        
        optimized_schedule = analytics.optimize_timetable(classes, preferences)
        
        return {
            "success": True,
            "data": optimized_schedule,
            "message": "Timetable optimization completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@router.post("/reports/generate")
async def generate_ai_report(request: ReportRequest):
    """Generate AI-powered reports"""
    try:
        report = analytics.generate_ai_report(
            request.report_type,
            request.data,
            request.template_id
        )
        
        return {
            "success": True,
            "data": report,
            "message": "Report generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.post("/generate-questions")
async def generate_ai_questions(request: QuestionGenerationRequest):
    """Generate AI-powered questions with solutions"""
    try:
        # Extract configuration
        config = request.config
        question_type = config.get('questionType', 'mixed')
        difficulty = config.get('difficulty', 'medium')
        topic_focus = config.get('topicFocus', '')
        question_count = config.get('questionCount', 10)
        include_solutions = config.get('includeSolutions', True)
        include_explanations = config.get('includeExplanations', True)
        board_specific = config.get('boardSpecific', True)
        
        # Generate questions based on syllabus and configuration
        questions = analytics.generate_questions(
            class_id=request.class_id,
            subject_id=request.subject_id,
            syllabus_id=request.syllabus_id,
            question_type=question_type,
            difficulty=difficulty,
            topic_focus=topic_focus,
            question_count=question_count,
            include_solutions=include_solutions,
            include_explanations=include_explanations,
            board_specific=board_specific
        )
        
        return {
            "success": True,
            "data": {
                "questions": questions,
                "total_questions": len(questions),
                "config_used": config
            },
            "message": f"Generated {len(questions)} questions successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")

@router.post("/syllabus/analyze")
async def analyze_syllabus_content(syllabus_id: int, teacher_id: int):
    """Analyze syllabus content and provide insights"""
    try:
        analysis = analytics.analyze_syllabus_content(syllabus_id, teacher_id)
        
        return {
            "success": True,
            "data": analysis,
            "message": "Syllabus analysis completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Syllabus analysis failed: {str(e)}")

@router.post("/syllabus/customize")
async def customize_syllabus_content(
    syllabus_id: int,
    teacher_id: int,
    customizations: Dict[str, Any]
):
    """Customize syllabus content with AI assistance"""
    try:
        customized_syllabus = analytics.customize_syllabus_content(
            syllabus_id, teacher_id, customizations
        )
        
        return {
            "success": True,
            "data": customized_syllabus,
            "message": "Syllabus customized successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Syllabus customization failed: {str(e)}")

@router.post("/topics/explain")
async def explain_topic_with_examples(
    topic: str,
    class_level: str,
    subject: str,
    board: str = "CBSE"
):
    """Generate topic explanations with visual examples"""
    try:
        explanation = analytics.explain_topic_with_examples(
            topic, class_level, subject, board
        )
        
        return {
            "success": True,
            "data": explanation,
            "message": "Topic explanation generated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topic explanation failed: {str(e)}")

@router.get("/insights/{teacher_id}")
async def get_teacher_insights(teacher_id: int):
    """Get comprehensive teacher insights"""
    try:
        insights = analytics.get_teacher_insights(teacher_id)
        
        return {
            "success": True,
            "data": insights,
            "message": "Teacher insights retrieved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@router.post("/assignments/generate")
async def generate_smart_assignment(
    class_id: int,
    subject_id: int,
    topic: str,
    difficulty: str = "medium",
    question_count: int = 10
):
    """Generate smart assignments with AI"""
    try:
        assignment = analytics.generate_smart_assignment(
            class_id, subject_id, topic, difficulty, question_count
        )
        
        return {
            "success": True,
            "data": assignment,
            "message": "Smart assignment generated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assignment generation failed: {str(e)}")

@router.post("/pdf/generate")
async def generate_pdf_with_solutions(
    question_paper_id: int,
    include_solutions: bool = True,
    teacher_only: bool = True
):
    """Generate PDF with or without solutions"""
    try:
        pdf_data = analytics.generate_pdf_with_solutions(
            question_paper_id, include_solutions, teacher_only
        )
        
        return {
            "success": True,
            "data": pdf_data,
            "message": "PDF generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

@router.post("/email/send-assignment")
async def send_assignment_via_email(
    assignment_id: int,
    student_ids: List[int],
    teacher_id: int
):
    """Send assignment via email with PDF attachment"""
    try:
        email_result = analytics.send_assignment_via_email(
            assignment_id, student_ids, teacher_id
        )
        
        return {
            "success": True,
            "data": email_result,
            "message": "Assignment sent via email"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email sending failed: {str(e)}")

@router.post("/board-content")
async def fetch_board_content(
    board: str,
    class_level: str,
    teacher_id: int
):
    """Fetch board-specific content from CBSE/ICSE"""
    try:
        board_content = analytics.fetch_board_content(
            board, class_level, teacher_id
        )
        
        return {
            "success": True,
            "data": board_content,
            "message": f"Board content fetched for {board} {class_level}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Board content fetch failed: {str(e)}")

@router.post("/syllabus/visual-edit")
async def save_visual_syllabus_edit(
    syllabus_id: int,
    visual_data: Dict[str, Any],
    teacher_id: int
):
    """Save visual syllabus editor changes"""
    try:
        saved_data = analytics.save_visual_syllabus_edit(
            syllabus_id, visual_data, teacher_id
        )
        
        return {
            "success": True,
            "data": saved_data,
            "message": "Visual syllabus saved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visual syllabus save failed: {str(e)}")

@router.post("/question-papers/{paper_id}/generate-professional-pdf")
async def generate_professional_pdf(
    paper_id: int,
    include_solutions: bool = True,
    teacher_only_solutions: bool = True,
    include_diagrams: bool = True,
    include_equations: bool = True,
    professional_formatting: bool = True,
    watermark: str = "Teacher Copy",
    header_footer: bool = True
):
    """Generate professional PDF with advanced formatting"""
    try:
        pdf_data = analytics.generate_professional_pdf(
            paper_id, include_solutions, teacher_only_solutions,
            include_diagrams, include_equations, professional_formatting,
            watermark, header_footer
        )
        
        return {
            "success": True,
            "data": pdf_data,
            "message": "Professional PDF generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Professional PDF generation failed: {str(e)}")

@router.post("/question-papers/{paper_id}/generate-student-pdf")
async def generate_student_pdf(
    paper_id: int,
    include_instructions: bool = True,
    include_rubric: bool = True,
    student_friendly_format: bool = True,
    no_solutions: bool = True
):
    """Generate student-friendly PDF without solutions"""
    try:
        pdf_data = analytics.generate_student_pdf(
            paper_id, include_instructions, include_rubric,
            student_friendly_format, no_solutions
        )
        
        return {
            "success": True,
            "data": pdf_data,
            "message": "Student PDF generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Student PDF generation failed: {str(e)}")

@router.post("/question-papers/{paper_id}/generate-interactive-pdf")
async def generate_interactive_pdf(
    paper_id: int,
    include_hyperlinks: bool = True,
    include_bookmarks: bool = True,
    include_forms: bool = False,
    include_annotations: bool = True
):
    """Generate interactive PDF with hyperlinks and bookmarks"""
    try:
        pdf_data = analytics.generate_interactive_pdf(
            paper_id, include_hyperlinks, include_bookmarks,
            include_forms, include_annotations
        )
        
        return {
            "success": True,
            "data": pdf_data,
            "message": "Interactive PDF generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interactive PDF generation failed: {str(e)}") 