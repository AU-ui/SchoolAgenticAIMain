"""
CBSE/ICSE Board Integration API Endpoints
Provides board-specific syllabus and paper generation
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from src.cbse_icse_syllabus import CBSEICSESyllabus

router = APIRouter(prefix="/ml/board", tags=["CBSE/ICSE Board Integration"])

# Initialize the syllabus system
syllabus_system = CBSEICSESyllabus()

class SyllabusRequest(BaseModel):
    board: str  # "CBSE" or "ICSE"
    subject: str
    class_level: str  # "Class 5", "Class 6", etc.

class QuestionPaperRequest(BaseModel):
    board: str
    subject: str
    class_level: str
    exam_type: str = "Unit Test"
    duration: int = 60
    selected_topics: List[str] = []

class LessonPlanRequest(BaseModel):
    board: str
    subject: str
    class_level: str
    topic: str

class AssignmentRequest(BaseModel):
    board: str
    subject: str
    class_level: str
    topic: str
    difficulty: str = "medium"
    question_count: int = 10

@router.get("/syllabus")
async def get_available_syllabus():
    """Get available syllabus options"""
    return {
        "success": True,
        "data": {
            "boards": ["CBSE", "ICSE"],
            "subjects": ["Mathematics", "Science", "English", "Social Studies"],
            "classes": ["Class 5", "Class 6", "Class 7", "Class 8"],
            "description": "CBSE and ICSE board syllabus integration"
        }
    }

@router.post("/syllabus/get")
async def get_syllabus(request: SyllabusRequest):
    """Get syllabus for specific board, subject and class"""
    try:
        syllabus = syllabus_system.get_syllabus(
            request.board, 
            request.subject, 
            request.class_level
        )
        
        if not syllabus:
            raise HTTPException(status_code=404, detail="Syllabus not found")
        
        return {
            "success": True,
            "data": {
                "board": request.board,
                "subject": request.subject,
                "class": request.class_level,
                "syllabus": syllabus
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/question-paper/generate")
async def generate_question_paper(request: QuestionPaperRequest):
    """Generate CBSE/ICSE question paper"""
    try:
        paper = syllabus_system.generate_question_paper(
            request.board,
            request.subject,
            request.class_level,
            request.exam_type,
            request.duration,
            request.selected_topics
        )
        
        if "error" in paper:
            raise HTTPException(status_code=404, detail=paper["error"])
        
        return {
            "success": True,
            "data": {
                "question_paper": paper,
                "message": f"{request.board} {request.subject} question paper generated successfully"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lesson-plan/generate")
async def generate_lesson_plan(request: LessonPlanRequest):
    """Generate board-specific lesson plan"""
    try:
        lesson_plan = syllabus_system.get_lesson_plan_template(
            request.board,
            request.subject,
            request.class_level,
            request.topic
        )
        
        if "error" in lesson_plan:
            raise HTTPException(status_code=404, detail=lesson_plan["error"])
        
        return {
            "success": True,
            "data": {
                "lesson_plan": lesson_plan,
                "message": f"{request.board} {request.subject} lesson plan generated successfully"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/assignment/generate")
async def generate_assignment(request: AssignmentRequest):
    """Generate board-specific assignment"""
    try:
        # Get syllabus for the topic
        syllabus = syllabus_system.get_syllabus(
            request.board,
            request.subject,
            request.class_level
        )
        
        if not syllabus:
            raise HTTPException(status_code=404, detail="Syllabus not found")
        
        # Generate questions for the assignment
        questions = []
        for i in range(request.question_count):
            question_type = "Short Answer" if i < request.question_count // 2 else "Long Answer"
            question = syllabus_system._generate_question(
                request.subject,
                question_type,
                syllabus,
                request.class_level
            )
            questions.append({
                "question_number": i + 1,
                "question": question,
                "type": question_type,
                "marks": 2 if question_type == "Short Answer" else 5
            })
        
        assignment = {
            "board": request.board,
            "subject": request.subject,
            "class": request.class_level,
            "topic": request.topic,
            "difficulty": request.difficulty,
            "total_questions": request.question_count,
            "total_marks": sum(q["marks"] for q in questions),
            "questions": questions,
            "instructions": [
                "Answer all questions",
                "Show your working clearly",
                "Use appropriate units where necessary"
            ]
        }
        
        return {
            "success": True,
            "data": {
                "assignment": assignment,
                "message": f"{request.board} {request.subject} assignment generated successfully"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/subjects/{board}")
async def get_subjects_for_board(board: str):
    """Get available subjects for a specific board"""
    try:
        if board.upper() == "CBSE":
            subjects = list(syllabus_system.cbse_syllabus.keys())
        elif board.upper() == "ICSE":
            subjects = list(syllabus_system.icse_syllabus.keys())
        else:
            raise HTTPException(status_code=400, detail="Invalid board")
        
        return {
            "success": True,
            "data": {
                "board": board,
                "subjects": subjects
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/topics/{board}/{subject}/{class_level}")
async def get_topics_for_subject(board: str, subject: str, class_level: str):
    """Get available topics for a specific subject and class"""
    try:
        syllabus = syllabus_system.get_syllabus(board, subject, class_level)
        
        if not syllabus:
            raise HTTPException(status_code=404, detail="Syllabus not found")
        
        topics = []
        for unit, unit_topics in syllabus.get("topics", {}).items():
            topics.extend(unit_topics)
        
        return {
            "success": True,
            "data": {
                "board": board,
                "subject": subject,
                "class": class_level,
                "units": syllabus.get("units", []),
                "topics": topics,
                "unit_topics": syllabus.get("topics", {})
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sample-papers")
async def get_sample_papers():
    """Get sample question papers for different boards and classes"""
    sample_papers = []
    
    # Generate sample papers for different combinations
    combinations = [
        ("CBSE", "Mathematics", "Class 8"),
        ("CBSE", "Science", "Class 7"),
        ("CBSE", "English", "Class 6"),
        ("ICSE", "Mathematics", "Class 8"),
        ("ICSE", "Science", "Class 7")
    ]
    
    for board, subject, class_level in combinations:
        try:
            paper = syllabus_system.generate_question_paper(
                board, subject, class_level, "Sample Paper", 60
            )
            if "error" not in paper:
                sample_papers.append({
                    "board": board,
                    "subject": subject,
                    "class": class_level,
                    "total_marks": paper["total_marks"],
                    "duration": paper["duration"],
                    "sections_count": len(paper["sections"])
                })
        except:
            continue
    
    return {
        "success": True,
        "data": {
            "sample_papers": sample_papers,
            "description": "Sample question papers for CBSE and ICSE boards"
        }
    } 