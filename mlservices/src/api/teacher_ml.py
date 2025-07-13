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

@router.get("/insights/{teacher_id}")
async def get_teacher_insights(teacher_id: int):
    """Get personalized insights for a teacher"""
    try:
        # Mock insights - in real implementation, fetch from database
        insights = {
            "attendance_trends": {
                "overall_rate": 85.5,
                "trend": "improving",
                "best_day": "Tuesday",
                "worst_day": "Friday"
            },
            "performance_metrics": {
                "average_grade": 78.2,
                "completion_rate": 92.1,
                "student_satisfaction": 4.2
            },
            "recommendations": [
                "Consider more interactive activities on Fridays",
                "Implement peer review sessions for better engagement",
                "Schedule difficult topics for Tuesday mornings"
            ]
        }
        
        return {
            "success": True,
            "data": insights,
            "message": "Insights retrieved successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve insights: {str(e)}") 