import numpy as np
import pandas as pd
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from sentence_transformers import SentenceTransformer
import torch
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

class NLPServices:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize NLP models
        self.sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment-latest")
        self.text_generator = pipeline("text-generation", model="gpt2")
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
        # Load sentence transformer for similarity
        self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Template-based report generator
        self.report_templates = self._load_report_templates()
    
    def generate_automated_report(self, data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        """Generate automated reports using NLP"""
        
        try:
            if report_type == "attendance_report":
                return self._generate_attendance_report(data)
            elif report_type == "performance_report":
                return self._generate_performance_report(data)
            elif report_type == "task_completion_report":
                return self._generate_task_report(data)
            else:
                return self._generate_generic_report(data, report_type)
                
        except Exception as e:
            self.logger.error(f"Error generating {report_type} report: {str(e)}")
            return {"error": f"Failed to generate {report_type} report"}
    
    def analyze_student_feedback(self, feedback_text: str) -> Dict[str, Any]:
        """Analyze student feedback using sentiment analysis and key phrase extraction"""
        
        try:
            # Sentiment analysis
            sentiment_result = self.sentiment_analyzer(feedback_text)
            
            # Key phrase extraction
            key_phrases = self._extract_key_phrases(feedback_text)
            
            # Topic classification
            topics = self._classify_topics(feedback_text)
            
            # Generate insights
            insights = self._generate_feedback_insights(sentiment_result, key_phrases, topics)
            
            return {
                "sentiment": sentiment_result[0],
                "key_phrases": key_phrases,
                "topics": topics,
                "insights": insights,
                "recommendations": self._generate_feedback_recommendations(sentiment_result[0])
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing student feedback: {str(e)}")
            return {"error": "Failed to analyze feedback"}
    
    def analyze_parent_communication(self, messages: List[Dict]) -> Dict[str, Any]:
        """Analyze parent communication patterns and sentiment"""
        
        try:
            analysis_results = []
            
            for message in messages:
                # Sentiment analysis
                sentiment = self.sentiment_analyzer(message['content'])
                
                # Communication style analysis
                style = self._analyze_communication_style(message['content'])
                
                # Urgency detection
                urgency = self._detect_urgency(message['content'])
                
                analysis_results.append({
                    'message_id': message.get('id'),
                    'sentiment': sentiment[0],
                    'communication_style': style,
                    'urgency_level': urgency,
                    'key_topics': self._extract_key_phrases(message['content'])
                })
            
            # Aggregate analysis
            overall_sentiment = self._aggregate_sentiment(analysis_results)
            communication_trends = self._analyze_communication_trends(analysis_results)
            
            return {
                'individual_analysis': analysis_results,
                'overall_sentiment': overall_sentiment,
                'communication_trends': communication_trends,
                'recommendations': self._generate_communication_recommendations(analysis_results)
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing parent communication: {str(e)}")
            return {"error": "Failed to analyze communication"}
    
    def generate_smart_summaries(self, text_content: str, summary_type: str = "general") -> Dict[str, Any]:
        """Generate smart summaries using NLP"""
        
        try:
            # Generate summary
            summary = self.summarizer(text_content, max_length=130, min_length=30, do_sample=False)
            
            # Extract key points
            key_points = self._extract_key_points(text_content)
            
            # Generate action items
            action_items = self._extract_action_items(text_content)
            
            return {
                "summary": summary[0]['summary_text'],
                "key_points": key_points,
                "action_items": action_items,
                "summary_type": summary_type,
                "confidence_score": self._calculate_summary_confidence(summary[0]['summary_text'], text_content)
            }
            
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            return {"error": "Failed to generate summary"}
    
    def _generate_attendance_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate automated attendance report"""
        
        attendance_data = data.get('attendance_data', [])
        class_info = data.get('class_info', {})
        
        # Generate narrative
        total_students = len(attendance_data)
        present_count = sum(1 for a in attendance_data if a.get('status') == 'present')
        attendance_rate = (present_count / total_students) * 100 if total_students > 0 else 0
        
        # Generate report content
        report_content = f"""
        Attendance Report for {class_info.get('class_name', 'Class')}
        
        Summary:
        - Total Students: {total_students}
        - Present: {present_count}
        - Attendance Rate: {attendance_rate:.1f}%
        
        Key Insights:
        - {self._generate_attendance_insights(attendance_data)}
        
        Recommendations:
        - {self._generate_attendance_recommendations(attendance_rate)}
        """
        
        return {
            "report_type": "attendance_report",
            "content": report_content,
            "metrics": {
                "total_students": total_students,
                "present_count": present_count,
                "attendance_rate": attendance_rate
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def _generate_performance_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate automated performance report"""
        
        performance_data = data.get('performance_data', [])
        student_info = data.get('student_info', {})
        
        # Calculate performance metrics
        grades = [p.get('grade', 0) for p in performance_data]
        avg_grade = np.mean(grades) if grades else 0
        grade_distribution = self._calculate_grade_distribution(grades)
        
        # Generate report content
        report_content = f"""
        Performance Report for {student_info.get('student_name', 'Student')}
        
        Summary:
        - Average Grade: {avg_grade:.2f}
        - Total Assignments: {len(performance_data)}
        - Grade Distribution: {grade_distribution}
        
        Key Insights:
        - {self._generate_performance_insights(performance_data)}
        
        Recommendations:
        - {self._generate_performance_recommendations(avg_grade)}
        """
        
        return {
            "report_type": "performance_report",
            "content": report_content,
            "metrics": {
                "average_grade": avg_grade,
                "total_assignments": len(performance_data),
                "grade_distribution": grade_distribution
            },
            "generated_at": datetime.now().isoformat()
        }
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key phrases from text"""
        
        # Simple key phrase extraction using frequency and importance
        words = text.lower().split()
        word_freq = {}
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        for word in words:
            if word not in stop_words and len(word) > 3:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top key phrases
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:5]]
    
    def _classify_topics(self, text: str) -> List[str]:
        """Classify topics in text"""
        
        # Simple topic classification based on keywords
        topics = []
        
        education_keywords = ['learning', 'study', 'homework', 'assignment', 'grade', 'test', 'exam']
        behavior_keywords = ['behavior', 'attitude', 'participation', 'engagement', 'motivation']
        communication_keywords = ['communication', 'message', 'contact', 'parent', 'teacher']
        
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in education_keywords):
            topics.append('academic')
        if any(keyword in text_lower for keyword in behavior_keywords):
            topics.append('behavior')
        if any(keyword in text_lower for keyword in communication_keywords):
            topics.append('communication')
        
        return topics if topics else ['general']
    
    def _analyze_communication_style(self, text: str) -> str:
        """Analyze communication style"""
        
        # Simple style analysis
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['urgent', 'immediately', 'asap', 'critical']):
            return 'urgent'
        elif any(word in text_lower for word in ['please', 'thank you', 'appreciate']):
            return 'polite'
        elif any(word in text_lower for word in ['problem', 'issue', 'concern', 'worried']):
            return 'concerned'
        else:
            return 'neutral'
    
    def _detect_urgency(self, text: str) -> str:
        """Detect urgency level in text"""
        
        urgent_words = ['urgent', 'immediately', 'asap', 'critical', 'emergency', 'now']
        moderate_words = ['soon', 'quickly', 'promptly', 'when possible']
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in urgent_words):
            return 'high'
        elif any(word in text_lower for word in moderate_words):
            return 'medium'
        else:
            return 'low'
    
    def _load_report_templates(self) -> Dict[str, str]:
        """Load report templates"""
        
        return {
            "attendance": "Attendance Report for {class_name}\nSummary: {summary}\nInsights: {insights}",
            "performance": "Performance Report for {student_name}\nSummary: {summary}\nRecommendations: {recommendations}",
            "task": "Task Completion Report\nSummary: {summary}\nProgress: {progress}"
        } 