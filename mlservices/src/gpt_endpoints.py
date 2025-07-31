from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import GPT service
try:
    from src.gpt_integration import gpt_service
    GPT_AVAILABLE = True
except ImportError:
    GPT_AVAILABLE = False
    print("⚠️ GPT integration not available")

router = APIRouter(prefix="/ml/gpt", tags=["GPT Integration"])

class StudentReportRequest(BaseModel):
    student_data: Dict[str, Any]

class LessonPlanRequest(BaseModel):
    subject: str
    grade: str
    topic: str
    duration: int

class ParentCommunicationRequest(BaseModel):
    context: str
    student_data: Dict[str, Any]
    tone: str = "professional"

class AssignmentRequest(BaseModel):
    subject: str
    grade: str
    topic: str
    difficulty: str = "medium"

@router.post("/reports/generate")
async def generate_student_report(request: StudentReportRequest):
    """Generate detailed student progress report using GPT"""
    if not GPT_AVAILABLE:
        raise HTTPException(status_code=503, detail="GPT integration not available")
    
    try:
        result = gpt_service.generate_student_report(request.student_data)
        
        return {
            "success": True,
            "data": result,
            "message": "Student report generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")

@router.post("/lesson-plans/generate")
async def generate_lesson_plan(request: LessonPlanRequest):
    """Generate complete lesson plan using GPT"""
    if not GPT_AVAILABLE:
        raise HTTPException(status_code=503, detail="GPT integration not available")
    
    try:
        result = gpt_service.generate_lesson_plan(
            request.subject,
            request.grade,
            request.topic,
            request.duration
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Lesson plan generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lesson plan generation failed: {str(e)}")

@router.post("/communication/generate")
async def generate_parent_communication(request: ParentCommunicationRequest):
    """Generate personalized parent communication using GPT"""
    if not GPT_AVAILABLE:
        raise HTTPException(status_code=503, detail="GPT integration not available")
    
    try:
        result = gpt_service.generate_parent_communication(
            request.context,
            request.student_data,
            request.tone
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Parent communication generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Communication generation failed: {str(e)}")

@router.post("/assignments/generate")
async def generate_assignment(request: AssignmentRequest):
    """Generate educational assignments using GPT"""
    if not GPT_AVAILABLE:
        raise HTTPException(status_code=503, detail="GPT integration not available")
    
    try:
        result = gpt_service.generate_assignment(
            request.subject,
            request.grade,
            request.topic,
            request.difficulty
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Assignment generated successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Assignment generation failed: {str(e)}")

@router.get("/status")
async def get_gpt_status():
    """Check GPT integration status"""
    return {
        "success": True,
        "data": {
            "gpt_available": GPT_AVAILABLE,
            "model": "gpt-3.5-turbo" if GPT_AVAILABLE else "mock-gpt",
            "features": [
                "Student Report Generation",
                "Lesson Plan Creation", 
                "Parent Communication",
                "Assignment Generation"
            ],
            "timestamp": datetime.now().isoformat()
        },
        "message": "GPT integration status retrieved"
    }

# Example usage endpoints for testing
@router.post("/examples/student-report")
async def example_student_report():
    """Example student report generation"""
    example_data = {
        "name": "Sarah Johnson",
        "grade": "5th Grade",
        "subject": "Mathematics",
        "attendance_rate": "95%",
        "average_grade": "A-",
        "participation_rate": "Excellent",
        "strengths": "Problem-solving, teamwork, creativity",
        "areas_for_improvement": "Time management, asking for help"
    }
    
    if GPT_AVAILABLE:
        result = gpt_service.generate_student_report(example_data)
    else:
        result = gpt_service._mock_student_report(example_data)
    
    return {
        "success": True,
        "data": result,
        "message": "Example student report generated"
    }

@router.post("/examples/lesson-plan")
async def example_lesson_plan():
    """Example lesson plan generation"""
    if GPT_AVAILABLE:
        result = gpt_service.generate_lesson_plan(
            "Science",
            "4th Grade", 
            "Ecosystems",
            45
        )
    else:
        result = gpt_service._mock_lesson_plan(
            "Science",
            "4th Grade",
            "Ecosystems", 
            45
        )
    
    return {
        "success": True,
        "data": result,
        "message": "Example lesson plan generated"
    }

@router.post("/examples/parent-communication")
async def example_parent_communication():
    """Example parent communication generation"""
    example_context = "Alex has been showing great improvement in math but needs support with homework completion"
    example_student_data = {
        "name": "Alex Chen",
        "grade": "6th Grade",
        "recent_performance": "Improving in math",
        "attendance_rate": "Good"
    }
    
    if GPT_AVAILABLE:
        result = gpt_service.generate_parent_communication(
            example_context,
            example_student_data,
            "encouraging"
        )
    else:
        result = gpt_service._mock_parent_communication(
            example_context,
            example_student_data,
            "encouraging"
        )
    
    return {
        "success": True,
        "data": result,
        "message": "Example parent communication generated"
    }

@router.post("/examples/assignment")
async def example_assignment():
    """Example assignment generation"""
    if GPT_AVAILABLE:
        result = gpt_service.generate_assignment(
            "English",
            "7th Grade",
            "Essay Writing",
            "medium"
        )
    else:
        result = gpt_service._mock_assignment(
            "English",
            "7th Grade", 
            "Essay Writing",
            "medium"
        )
    
    return {
        "success": True,
        "data": result,
        "message": "Example assignment generated"
    } 