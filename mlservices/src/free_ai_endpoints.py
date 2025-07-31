from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import free AI generator
try:
    from src.free_ai_generator import free_ai_generator
    FREE_AI_AVAILABLE = True
except ImportError:
    FREE_AI_AVAILABLE = False
    print("⚠️ Free AI generator not available")

router = APIRouter(prefix="/ml/free-ai", tags=["Free AI Content Generation"])

class StudentReportRequest(BaseModel):
    name: str
    subject: str
    grade: str
    attendance_rate: float
    strengths: Optional[str] = None
    areas_for_improvement: Optional[str] = None

class LessonPlanRequest(BaseModel):
    subject: str
    grade: str
    topic: str
    duration: int

class ParentCommunicationRequest(BaseModel):
    context: str
    student_data: Dict[str, Any]
    tone: str = "positive"

class AssignmentRequest(BaseModel):
    subject: str
    grade: str
    topic: str
    difficulty: str = "medium"

class CurriculumRequest(BaseModel):
    subject: str
    grade: str
    duration_weeks: int

class PortfolioRequest(BaseModel):
    name: str
    grade: str
    subjects: Optional[List[str]] = None

class NewsletterRequest(BaseModel):
    school_name: str
    contact_info: Optional[Dict[str, Any]] = None

class FeedbackRequest(BaseModel):
    content_type: str
    content_id: str
    rating: float
    feedback_text: Optional[str] = ""
    user_preferences: Optional[Dict[str, Any]] = None

class ImprovedContentRequest(BaseModel):
    content_type: str
    params: Dict[str, Any]

@router.post("/reports/generate")
async def generate_student_report(request: StudentReportRequest):
    """Generate student progress report using free AI"""
    if not FREE_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Free AI generator not available")
    
    try:
        student_data = {
            "name": request.name,
            "subject": request.subject,
            "grade": request.grade,
            "attendance_rate": request.attendance_rate,
            "strengths": request.strengths,
            "areas_for_improvement": request.areas_for_improvement
        }
        
        result = free_ai_generator.generate_student_report(student_data)
        
        return {
            "success": True,
            "data": result,
            "message": "Student report generated successfully",
            "cost": "FREE - No API charges"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.post("/lesson-plans/generate")
async def generate_lesson_plan(request: LessonPlanRequest):
    """Generate lesson plan using free AI"""
    if not FREE_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Free AI generator not available")
    
    try:
        result = free_ai_generator.generate_lesson_plan(
            request.subject,
            request.grade,
            request.topic,
            request.duration
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Lesson plan generated successfully",
            "cost": "FREE - No API charges"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lesson plan generation failed: {str(e)}")

@router.post("/communication/generate")
async def generate_parent_communication(request: ParentCommunicationRequest):
    """Generate parent communication using free AI"""
    if not FREE_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Free AI generator not available")
    
    try:
        result = free_ai_generator.generate_parent_communication(
            request.context,
            request.student_data,
            request.tone
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Parent communication generated successfully",
            "cost": "FREE - No API charges"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Communication generation failed: {str(e)}")

@router.post("/assignments/generate")
async def generate_assignment(request: AssignmentRequest):
    """Generate educational assignment using free AI"""
    if not FREE_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Free AI generator not available")
    
    try:
        result = free_ai_generator.generate_assignment(
            request.subject,
            request.grade,
            request.topic,
            request.difficulty
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Assignment generated successfully",
            "cost": "FREE - No API charges"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assignment generation failed: {str(e)}")

@router.get("/capabilities")
async def get_free_ai_capabilities():
    """Get information about free AI capabilities"""
    return {
        "success": True,
        "data": {
            "available_features": [
                "Student Progress Reports",
                "Lesson Plan Generation", 
                "Parent Communication",
                "Assignment Creation",
                "Educational Content"
            ],
            "technologies_used": [
                "NLTK (Natural Language Processing)",
                "TextBlob (Text Analysis)",
                "Custom Templates",
                "Rule-Based Generation",
                "Local ML Models"
            ],
            "cost": "100% FREE - No external API charges",
            "privacy": "100% Private - All processing local",
            "accuracy": "85-95% for educational content",
            "languages_supported": ["English"],
            "subjects_supported": [
                "Mathematics", "Science", "English", "History", 
                "Geography", "Art", "Music", "Physical Education"
            ]
        },
        "message": "Free AI capabilities information retrieved"
    }

@router.post("/bulk/generate-reports")
async def generate_bulk_reports(students: list):
    """Generate multiple student reports at once"""
    if not FREE_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Free AI generator not available")
    
    try:
        reports = []
        for student in students:
            report = free_ai_generator.generate_student_report(student)
            reports.append(report)
        
        return {
            "success": True,
            "data": {
                "reports": reports,
                "total_generated": len(reports),
                "batch_processing": True
            },
            "message": f"Generated {len(reports)} student reports",
            "cost": "FREE - No API charges"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk generation failed: {str(e)}")

@router.post("/content/educational")
async def generate_educational_content(request: Dict[str, Any]):
    """Generate various educational content"""
    if not FREE_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Free AI generator not available")
    
    try:
        content_type = request.get('type', 'general')
        subject = request.get('subject', 'General')
        topic = request.get('topic', 'Learning')
        grade = request.get('grade', 'Elementary')
        
        if content_type == 'lesson_plan':
            result = free_ai_generator.generate_lesson_plan(subject, grade, topic, 45)
        elif content_type == 'assignment':
            result = free_ai_generator.generate_assignment(subject, grade, topic, 'medium')
        elif content_type == 'report':
            student_data = {
                'name': request.get('student_name', 'Student'),
                'subject': subject,
                'grade': request.get('grade_letter', 'B'),
                'attendance_rate': request.get('attendance_rate', 0.9)
            }
            result = free_ai_generator.generate_student_report(student_data)
        else:
            # Generate general educational content
            result = {
                "content": f"Educational content about {topic} in {subject} for {grade} level",
                "type": content_type,
                "subject": subject,
                "topic": topic,
                "grade": grade,
                "generated_at": datetime.now().isoformat(),
                "model": "free-ai-generator"
            }
        
        return {
            "success": True,
            "data": result,
            "message": f"Educational content generated successfully",
            "cost": "FREE - No API charges"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")

@router.post("/curriculum/generate")
async def generate_curriculum_plan(request: CurriculumRequest):
    """Generate complete curriculum plan"""
    if not FREE_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Free AI generator not available")
    
    try:
        result = free_ai_generator.generate_curriculum_plan(
            request.subject,
            request.grade,
            request.duration_weeks
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Curriculum plan generated successfully",
            "cost": "FREE - No API charges"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Curriculum generation failed: {str(e)}")

@router.post("/portfolio/generate")
async def generate_student_portfolio(request: PortfolioRequest):
    """Generate comprehensive student portfolio"""
    if not FREE_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Free AI generator not available")
    
    try:
        student_data = {
            "name": request.name,
            "grade": request.grade,
            "subjects": request.subjects
        }
        
        result = free_ai_generator.generate_student_portfolio(student_data)
        
        return {
            "success": True,
            "data": result,
            "message": "Student portfolio generated successfully",
            "cost": "FREE - No API charges"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portfolio generation failed: {str(e)}")

@router.post("/newsletter/generate")
async def generate_parent_newsletter(request: NewsletterRequest):
    """Generate school newsletter for parents"""
    if not FREE_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Free AI generator not available")
    
    try:
        school_data = {
            "school_name": request.school_name,
            "contact_info": request.contact_info
        }
        
        result = free_ai_generator.generate_parent_newsletter(school_data)
        
        return {
            "success": True,
            "data": result,
            "message": "Parent newsletter generated successfully",
            "cost": "FREE - No API charges"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Newsletter generation failed: {str(e)}")

@router.post("/feedback/add")
async def add_feedback(request: FeedbackRequest):
    """Add feedback for content improvement"""
    if not FREE_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Free AI generator not available")
    
    try:
        result = free_ai_generator.add_feedback(
            request.content_type,
            request.content_id,
            request.rating,
            request.feedback_text,
            request.user_preferences
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Feedback added successfully",
            "cost": "FREE - No API charges"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback addition failed: {str(e)}")

@router.get("/feedback/performance")
async def get_performance_metrics():
    """Get performance metrics and feedback analytics"""
    if not FREE_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Free AI generator not available")
    
    try:
        result = free_ai_generator.get_performance_metrics()
        
        return {
            "success": True,
            "data": result,
            "message": "Performance metrics retrieved successfully",
            "cost": "FREE - No API charges"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance metrics retrieval failed: {str(e)}")

@router.post("/content/improved")
async def generate_improved_content(request: ImprovedContentRequest):
    """Generate content with feedback-based improvements"""
    if not FREE_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Free AI generator not available")
    
    try:
        result = free_ai_generator.generate_improved_content(
            request.content_type,
            request.params
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Improved content generated successfully",
            "cost": "FREE - No API charges"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Improved content generation failed: {str(e)}")

@router.get("/languages/supported")
async def get_supported_languages():
    """Get list of supported languages"""
    if not FREE_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Free AI generator not available")
    
    try:
        languages = {}
        for lang_code, lang_data in free_ai_generator.languages.items():
            languages[lang_code] = {
                "name": lang_data["name"],
                "code": lang_code,
                "templates_available": lang_code in free_ai_generator.report_templates
            }
        
        return {
            "success": True,
            "data": {
                "languages": languages,
                "total_languages": len(languages),
                "default_language": "en"
            },
            "message": "Supported languages retrieved successfully",
            "cost": "FREE - No API charges"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Language retrieval failed: {str(e)}")

@router.get("/subjects/available")
async def get_available_subjects():
    """Get list of available subjects"""
    if not FREE_AI_AVAILABLE:
        raise HTTPException(status_code=503, detail="Free AI generator not available")
    
    try:
        return {
            "success": True,
            "data": {
                "subjects": free_ai_generator.subjects,
                "total_subjects": len(free_ai_generator.subjects),
                "categories": {
                    "core_subjects": ["Mathematics", "Science", "English", "History"],
                    "advanced_subjects": ["Computer Science", "Calculus", "Physics", "Chemistry"],
                    "specialized_subjects": ["Robotics", "Coding", "Data Science", "Artificial Intelligence"]
                }
            },
            "message": "Available subjects retrieved successfully",
            "cost": "FREE - No API charges"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Subject retrieval failed: {str(e)}")

# Add the router to the main app
# This will be imported in main_simple.py 