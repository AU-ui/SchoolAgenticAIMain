import numpy as np
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import json

class NaturalLanguageGeneration:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize text generation models
        self.text_generator = pipeline("text-generation", model="gpt2")
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
        # Load templates
        self.email_templates = self._load_email_templates()
        self.feedback_templates = self._load_feedback_templates()
        self.report_templates = self._load_report_templates()
    
    def generate_personalized_email(self, recipient_data: Dict[str, Any], 
                                  email_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized emails for different purposes"""
        
        try:
            # Get base template
            template = self.email_templates.get(email_type, self.email_templates['general'])
            
            # Personalize content
            personalized_content = self._personalize_email_content(template, recipient_data, context)
            
            # Generate subject line
            subject_line = self._generate_subject_line(email_type, context)
            
            # Add signature
            signature = self._generate_signature(recipient_data)
            
            return {
                "success": True,
                "subject": subject_line,
                "content": personalized_content,
                "signature": signature,
                "email_type": email_type,
                "recipient": recipient_data.get('name', 'Recipient'),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating email: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_student_feedback(self, student_data: Dict[str, Any], 
                                performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized student feedback"""
        
        try:
            # Analyze performance
            performance_analysis = self._analyze_performance(performance_data)
            
            # Select appropriate template
            template = self._select_feedback_template(performance_analysis)
            
            # Generate personalized feedback
            feedback_content = self._generate_feedback_content(template, student_data, performance_analysis)
            
            # Add specific recommendations
            recommendations = self._generate_feedback_recommendations(performance_analysis)
            
            return {
                "success": True,
                "feedback_content": feedback_content,
                "recommendations": recommendations,
                "performance_summary": performance_analysis['summary'],
                "student_name": student_data.get('name', 'Student'),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating student feedback: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_parent_communication(self, parent_data: Dict[str, Any], 
                                   communication_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate parent communication templates"""
        
        try:
            # Get communication template
            template = self._get_parent_communication_template(communication_type)
            
            # Personalize content
            personalized_content = self._personalize_parent_communication(template, parent_data, context)
            
            # Add cultural considerations
            culturally_adjusted_content = self._apply_cultural_considerations(
                personalized_content, parent_data.get('language_preference', 'english')
            )
            
            return {
                "success": True,
                "content": culturally_adjusted_content,
                "communication_type": communication_type,
                "parent_name": parent_data.get('name', 'Parent'),
                "language": parent_data.get('language_preference', 'english'),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating parent communication: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def generate_automated_report(self, data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        """Generate automated reports with NLG"""
        
        try:
            # Get report template
            template = self.report_templates.get(report_type, self.report_templates['general'])
            
            # Generate report content
            report_content = self._generate_report_content(template, data)
            
            # Add insights
            insights = self._generate_report_insights(data)
            
            # Add recommendations
            recommendations = self._generate_report_recommendations(data)
            
            return {
                "success": True,
                "report_content": report_content,
                "insights": insights,
                "recommendations": recommendations,
                "report_type": report_type,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error generating report: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _load_email_templates(self) -> Dict[str, str]:
        """Load email templates"""
        
        return {
            "attendance_alert": """
            Dear {parent_name},
            
            I wanted to inform you that {student_name} was absent from class today ({date}).
            If this absence was planned, please let us know. If not, we hope {student_name} is feeling well.
            
            Please ensure {student_name} completes any missed assignments.
            
            Best regards,
            {teacher_name}
            """,
            
            "performance_update": """
            Dear {parent_name},
            
            I'm pleased to share that {student_name} has shown excellent progress in {subject}.
            Recent assessments indicate strong understanding of the material.
            
            Key achievements:
            {achievements}
            
            Areas for continued growth:
            {growth_areas}
            
            Best regards,
            {teacher_name}
            """,
            
            "general": """
            Dear {recipient_name},
            
            {message_content}
            
            Best regards,
            {sender_name}
            """
        }
    
    def _load_feedback_templates(self) -> Dict[str, str]:
        """Load feedback templates"""
        
        return {
            "excellent": """
            {student_name}, your work demonstrates exceptional understanding and effort.
            Your {achievement} shows your dedication to learning.
            Continue to challenge yourself and explore new concepts.
            """,
            
            "good": """
            {student_name}, you're making solid progress in {subject}.
            Your {strength} is particularly strong.
            To continue improving, focus on {improvement_area}.
            """,
            
            "needs_improvement": """
            {student_name}, I see you're working on {subject}.
            While you've made some progress, there's room for growth in {area_of_concern}.
            I recommend {specific_recommendation} to help you succeed.
            """
        }
    
    def _load_report_templates(self) -> Dict[str, str]:
        """Load report templates"""
        
        return {
            "attendance": """
            Attendance Report for {class_name}
            
            Summary:
            - Total Students: {total_students}
            - Present: {present_count}
            - Absent: {absent_count}
            - Attendance Rate: {attendance_rate}%
            
            Key Insights:
            {insights}
            
            Recommendations:
            {recommendations}
            """,
            
            "performance": """
            Performance Report for {student_name}
            
            Summary:
            - Average Grade: {average_grade}
            - Total Assignments: {total_assignments}
            - Improvement Trend: {trend}
            
            Key Insights:
            {insights}
            
            Recommendations:
            {recommendations}
            """,
            
            "general": """
            {report_title}
            
            {content}
            
            Generated on: {timestamp}
            """
        }
    
    def _personalize_email_content(self, template: str, recipient_data: Dict[str, Any], 
                                 context: Dict[str, Any]) -> str:
        """Personalize email content"""
        
        # Replace placeholders with actual data
        personalized = template
        
        for key, value in recipient_data.items():
            placeholder = f"{{{key}}}"
            personalized = personalized.replace(placeholder, str(value))
        
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            personalized = personalized.replace(placeholder, str(value))
        
        return personalized
    
    def _generate_subject_line(self, email_type: str, context: Dict[str, Any]) -> str:
        """Generate appropriate subject line"""
        
        subject_lines = {
            "attendance_alert": f"Attendance Update - {context.get('date', 'Today')}",
            "performance_update": "Student Progress Update",
            "general": "Important Information from School"
        }
        
        return subject_lines.get(email_type, "School Communication")
    
    def _generate_signature(self, recipient_data: Dict[str, Any]) -> str:
        """Generate email signature"""
        
        return f"""
        Best regards,
        {recipient_data.get('teacher_name', 'Teacher')}
        {recipient_data.get('school_name', 'School')}
        """
    
    def _analyze_performance(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze student performance data"""
        
        grades = performance_data.get('grades', [])
        attendance = performance_data.get('attendance_rate', 0.5)
        
        if grades:
            avg_grade = np.mean(grades)
            trend = "improving" if len(grades) > 1 and grades[-1] > grades[0] else "stable"
        else:
            avg_grade = 0
            trend = "no data"
        
        return {
            "average_grade": avg_grade,
            "attendance_rate": attendance,
            "trend": trend,
            "summary": self._generate_performance_summary(avg_grade, attendance, trend)
        }
    
    def _select_feedback_template(self, performance_analysis: Dict[str, Any]) -> str:
        """Select appropriate feedback template"""
        
        avg_grade = performance_analysis['average_grade']
        
        if avg_grade >= 0.9:
            return self.feedback_templates['excellent']
        elif avg_grade >= 0.7:
            return self.feedback_templates['good']
        else:
            return self.feedback_templates['needs_improvement']
    
    def _generate_feedback_content(self, template: str, student_data: Dict[str, Any], 
                                 performance_analysis: Dict[str, Any]) -> str:
        """Generate personalized feedback content"""
        
        # Replace placeholders in template
        content = template
        
        replacements = {
            "student_name": student_data.get('name', 'Student'),
            "achievement": "consistent effort and high-quality work",
            "subject": "the subject",
            "strength": "analytical thinking",
            "improvement_area": "time management",
            "area_of_concern": "understanding of key concepts",
            "specific_recommendation": "additional practice and review"
        }
        
        for placeholder, value in replacements.items():
            content = content.replace(f"{{{placeholder}}}", value)
        
        return content
    
    def _generate_feedback_recommendations(self, performance_analysis: Dict[str, Any]) -> List[str]:
        """Generate feedback recommendations"""
        
        recommendations = []
        avg_grade = performance_analysis['average_grade']
        
        if avg_grade < 0.7:
            recommendations.extend([
                "Schedule additional tutoring sessions",
                "Complete extra practice problems",
                "Review previous assignments"
            ])
        elif avg_grade < 0.9:
            recommendations.extend([
                "Continue current study habits",
                "Challenge yourself with advanced problems",
                "Help peers who are struggling"
            ])
        else:
            recommendations.extend([
                "Consider advanced placement options",
                "Mentor other students",
                "Explore independent study projects"
            ])
        
        return recommendations
    
    def _get_parent_communication_template(self, communication_type: str) -> str:
        """Get parent communication template"""
        
        templates = {
            "attendance": "Your child was absent today. Please contact us if this was unplanned.",
            "performance": "Your child's recent performance shows {trend}. We recommend {action}.",
            "behavior": "Your child's behavior today was {description}. We appreciate your support.",
            "general": "Important information about your child: {message}"
        }
        
        return templates.get(communication_type, templates['general'])
    
    def _personalize_parent_communication(self, template: str, parent_data: Dict[str, Any], 
                                       context: Dict[str, Any]) -> str:
        """Personalize parent communication"""
        
        content = template
        
        # Replace placeholders
        for key, value in context.items():
            placeholder = f"{{{key}}}"
            content = content.replace(placeholder, str(value))
        
        return content
    
    def _apply_cultural_considerations(self, content: str, language: str) -> str:
        """Apply cultural considerations to communication"""
        
        cultural_adjustments = {
            "chinese": "尊敬的家长，",
            "spanish": "Estimado padre/madre,",
            "arabic": "عزيزي الوالد،",
            "hindi": "प्रिय अभिभावक,"
        }
        
        if language in cultural_adjustments:
            content = cultural_adjustments[language] + "\n\n" + content
        
        return content
    
    def _generate_report_content(self, template: str, data: Dict[str, Any]) -> str:
        """Generate report content"""
        
        content = template
        
        # Replace placeholders with data
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            content = content.replace(placeholder, str(value))
        
        return content
    
    def _generate_report_insights(self, data: Dict[str, Any]) -> List[str]:
        """Generate report insights"""
        
        insights = []
        
        if 'attendance_rate' in data:
            rate = data['attendance_rate']
            if rate < 0.8:
                insights.append("Attendance rate is below target")
            elif rate > 0.95:
                insights.append("Excellent attendance rate")
        
        if 'average_grade' in data:
            grade = data['average_grade']
            if grade < 0.7:
                insights.append("Performance needs improvement")
            elif grade > 0.9:
                insights.append("Outstanding performance")
        
        return insights
    
    def _generate_report_recommendations(self, data: Dict[str, Any]) -> List[str]:
        """Generate report recommendations"""
        
        recommendations = []
        
        if 'attendance_rate' in data and data['attendance_rate'] < 0.8:
            recommendations.append("Implement attendance incentives")
            recommendations.append("Increase parent communication")
        
        if 'average_grade' in data and data['average_grade'] < 0.7:
            recommendations.append("Provide additional academic support")
            recommendations.append("Schedule individual tutoring sessions")
        
        return recommendations
    
    def _generate_performance_summary(self, avg_grade: float, attendance: float, trend: str) -> str:
        """Generate performance summary"""
        
        if avg_grade >= 0.9:
            performance_level = "excellent"
        elif avg_grade >= 0.7:
            performance_level = "good"
        else:
            performance_level = "needs improvement"
        
        return f"Student shows {performance_level} performance with {trend} trend and {attendance*100:.1f}% attendance." 