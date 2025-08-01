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

class PlagiarismDetectionRequest(BaseModel):
    assignment_id: int
    student_submissions: List[Dict[str, Any]]
    reference_materials: Optional[List[str]] = None

class GradingBiasRequest(BaseModel):
    grades_data: List[Dict[str, Any]]
    student_demographics: Optional[Dict[str, Any]] = None

class PerformancePredictionRequest(BaseModel):
    student_id: int
    historical_data: List[Dict[str, Any]]
    current_performance: Dict[str, Any]

class PersonalizedFeedbackRequest(BaseModel):
    student_id: int
    assignment_data: Dict[str, Any]
    performance_history: List[Dict[str, Any]]
    learning_style: Optional[str] = "mixed"

# NEW: Advanced Attendance Intelligence Models
class AttendancePatternRequest(BaseModel):
    teacher_id: int
    class_id: int
    date_range: Dict[str, str]
    include_anomalies: bool = True

class PredictiveAttendanceRequest(BaseModel):
    teacher_id: int
    class_id: int
    student_ids: List[int]
    prediction_days: int = 7

class BehavioralAnalyticsRequest(BaseModel):
    teacher_id: int
    class_id: int
    student_id: int
    analysis_period: str = "month"

class RiskAssessmentRequest(BaseModel):
    teacher_id: int
    class_id: int
    risk_threshold: float = 0.7

class TaskPrioritizationRequest(BaseModel):
    teacher_id: int
    tasks: List[Dict[str, Any]]
    available_time: int
    preferences: Dict[str, Any]

class TimeEstimationRequest(BaseModel):
    teacher_id: int
    task_details: Dict[str, Any]
    teacher_experience: str
    available_resources: List[str]

class ResourceAllocationRequest(BaseModel):
    teacher_id: int
    available_resources: Dict[str, Any]
    tasks_requirements: List[Dict[str, Any]]
    constraints: Dict[str, Any]

class WorkflowOptimizationRequest(BaseModel):
    teacher_id: int
    current_workflow: Dict[str, Any]
    optimization_goals: Dict[str, bool]
    available_automation: List[str]

class ResourceAnalyticsRequest(BaseModel):
    teacher_id: int
    resource_data: Dict[str, Any]
    usage_period: str
    include_patterns: bool = True

class ContentRecommendationsRequest(BaseModel):
    teacher_id: int
    current_subject: str
    class_level: str
    student_performance: Dict[str, Any]
    available_resources: List[str]
    preferences: Dict[str, Any]

class ResourceOptimizationRequest(BaseModel):
    teacher_id: int
    current_resources: Dict[str, Any]
    optimization_goals: Dict[str, bool]
    constraints: Dict[str, Any]

class PerformanceTrackingRequest(BaseModel):
    teacher_id: int
    tracking_period: str
    metrics: Dict[str, bool]
    comparison_baseline: str

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

@router.post("/grades/plagiarism-detection")
async def detect_plagiarism(request: PlagiarismDetectionRequest):
    """Detect plagiarism in student submissions using AI"""
    try:
        result = analytics.detect_plagiarism(
            request.assignment_id,
            request.student_submissions,
            request.reference_materials
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Plagiarism detection completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Plagiarism detection failed: {str(e)}")

@router.post("/grades/bias-detection")
async def detect_grading_bias(request: GradingBiasRequest):
    """Detect potential bias in grading patterns"""
    try:
        result = analytics.detect_grading_bias(
            request.grades_data,
            request.student_demographics
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Grading bias analysis completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bias detection failed: {str(e)}")

@router.post("/grades/performance-prediction")
async def predict_student_performance_grade(request: PerformancePredictionRequest):
    """Predict student performance for specific assignments"""
    try:
        result = analytics.predict_student_performance_grade(
            request.student_id,
            request.historical_data,
            request.current_performance
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Performance prediction completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance prediction failed: {str(e)}")

@router.post("/grades/personalized-feedback")
async def generate_personalized_feedback(request: PersonalizedFeedbackRequest):
    """Generate personalized feedback for students"""
    try:
        result = analytics.generate_personalized_feedback(
            request.student_id,
            request.assignment_data,
            request.performance_history,
            request.learning_style
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Personalized feedback generated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feedback generation failed: {str(e)}")

@router.get("/grades/analytics/{teacher_id}")
async def get_grade_analytics(teacher_id: int):
    """Get comprehensive grade analytics for a teacher"""
    try:
        result = analytics.get_grade_analytics(teacher_id)
        
        return {
            "success": True,
            "data": result,
            "message": "Grade analytics retrieved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Grade analytics failed: {str(e)}")

# NEW: Advanced Attendance Intelligence Endpoints
@router.post("/attendance/pattern-analysis")
async def analyze_attendance_patterns_advanced(request: AttendancePatternRequest):
    """Advanced attendance pattern analysis with anomaly detection"""
    try:
        result = analytics.analyze_attendance_patterns_advanced(
            request.teacher_id,
            request.class_id,
            request.date_range,
            request.include_anomalies
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Advanced attendance pattern analysis completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {str(e)}")

@router.post("/attendance/predictive")
async def predict_attendance(request: PredictiveAttendanceRequest):
    """Predict student attendance for future dates"""
    try:
        result = analytics.predict_attendance(
            request.teacher_id,
            request.class_id,
            request.student_ids,
            request.prediction_days
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Attendance prediction completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attendance prediction failed: {str(e)}")

@router.post("/attendance/behavioral-analytics")
async def analyze_behavioral_patterns(request: BehavioralAnalyticsRequest):
    """Analyze student behavioral patterns and engagement"""
    try:
        result = analytics.analyze_behavioral_patterns(
            request.teacher_id,
            request.class_id,
            request.student_id,
            request.analysis_period
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Behavioral analytics completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Behavioral analytics failed: {str(e)}")

@router.post("/attendance/risk-assessment")
async def assess_attendance_risk(request: RiskAssessmentRequest):
    """Assess risk of chronic absenteeism"""
    try:
        result = analytics.assess_attendance_risk(
            request.teacher_id,
            request.class_id,
            request.risk_threshold
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Risk assessment completed"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Risk assessment failed: {str(e)}")

@router.get("/attendance/analytics/{teacher_id}")
async def get_attendance_analytics(teacher_id: int):
    """Get comprehensive attendance analytics for a teacher"""
    try:
        analytics = await get_attendance_analytics(teacher_id)
        return {"success": True, "data": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# NEW: Smart Task Optimization Endpoints
@router.post("/tasks/prioritize")
async def prioritize_tasks(request: TaskPrioritizationRequest):
    """AI-powered task prioritization and scheduling"""
    try:
        result = await prioritize_tasks_ai(
            request.teacher_id,
            request.tasks,
            request.available_time,
            request.preferences
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/time-estimation")
async def estimate_task_time(request: TimeEstimationRequest):
    """AI-powered time estimation for tasks"""
    try:
        result = await estimate_task_time_ai(
            request.teacher_id,
            request.task_details,
            request.teacher_experience,
            request.available_resources
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/resource-allocation")
async def optimize_resource_allocation(request: ResourceAllocationRequest):
    """Optimal resource allocation and scheduling"""
    try:
        result = await optimize_resource_allocation_ai(
            request.teacher_id,
            request.available_resources,
            request.tasks_requirements,
            request.constraints
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks/workflow-optimization")
async def optimize_workflow(request: WorkflowOptimizationRequest):
    """Streamlined workflow management and automation"""
    try:
        result = await optimize_workflow_ai(
            request.teacher_id,
            request.current_workflow,
            request.optimization_goals,
            request.available_automation
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# NEW: Resource Intelligence Endpoints
@router.post("/resources/analytics")
async def analyze_resource_usage(request: ResourceAnalyticsRequest):
    """Analyze resource usage patterns and provide insights"""
    try:
        result = await analyze_resource_usage_ai(
            request.teacher_id,
            request.resource_data,
            request.usage_period,
            request.include_patterns
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resources/recommendations")
async def get_content_recommendations(request: ContentRecommendationsRequest):
    """Get AI-powered content recommendations"""
    try:
        result = await get_content_recommendations_ai(
            request.teacher_id,
            request.current_subject,
            request.class_level,
            request.student_performance,
            request.available_resources,
            request.preferences
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resources/optimize")
async def optimize_resources(request: ResourceOptimizationRequest):
    """Optimize resource allocation and management"""
    try:
        result = await optimize_resources_ai(
            request.teacher_id,
            request.current_resources,
            request.optimization_goals,
            request.constraints
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/resources/performance")
async def track_resource_performance(request: PerformanceTrackingRequest):
    """Track resource performance and effectiveness"""
    try:
        result = await track_resource_performance_ai(
            request.teacher_id,
            request.tracking_period,
            request.metrics,
            request.comparison_baseline
        )
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 