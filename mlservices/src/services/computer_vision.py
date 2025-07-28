import cv2
import numpy as np
import pytesseract
from PIL import Image
import face_recognition
import qrcode
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import base64
import io

class ComputerVisionService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize face recognition
        self.known_face_encodings = []
        self.known_face_names = []
        
        # QR code detector
        self.qr_detector = cv2.QRCodeDetector()
        
        # OCR configuration
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def process_qr_code_attendance(self, image_data: str) -> Dict[str, Any]:
        """Process QR code for attendance tracking"""
        
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Detect QR code
            data, bbox, _ = self.qr_detector.detectAndDecode(image_cv)
            
            if data:
                # Parse QR code data
                qr_data = self._parse_qr_data(data)
                
                # Verify QR code validity
                validity = self._verify_qr_validity(qr_data)
                
                return {
                    "success": True,
                    "qr_data": qr_data,
                    "validity": validity,
                    "timestamp": datetime.now().isoformat(),
                    "confidence": 0.95
                }
            else:
                return {
                    "success": False,
                    "error": "No QR code detected",
                    "confidence": 0.0
                }
                
        except Exception as e:
            self.logger.error(f"Error processing QR code: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def scan_document_ocr(self, image_data: str, document_type: str = "assignment") -> Dict[str, Any]:
        """Scan and extract text from documents using OCR"""
        
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            
            # Preprocess image for better OCR
            processed_image = self._preprocess_image_for_ocr(image)
            
            # Extract text using OCR
            text = pytesseract.image_to_string(processed_image)
            
            # Post-process extracted text
            cleaned_text = self._clean_ocr_text(text)
            
            # Extract structured data based on document type
            structured_data = self._extract_structured_data(cleaned_text, document_type)
            
            return {
                "success": True,
                "extracted_text": cleaned_text,
                "structured_data": structured_data,
                "document_type": document_type,
                "confidence": self._calculate_ocr_confidence(processed_image),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in document OCR: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def face_recognition_attendance(self, image_data: str, class_roster: List[Dict]) -> Dict[str, Any]:
        """Verify attendance using face recognition"""
        
        try:
            # Decode base64 image
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
            image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Detect faces in image
            face_locations = face_recognition.face_locations(image_cv)
            face_encodings = face_recognition.face_encodings(image_cv, face_locations)
            
            recognized_students = []
            
            for face_encoding in face_encodings:
                # Compare with known faces
                matches = face_recognition.compare_faces(
                    self.known_face_encodings, face_encoding, tolerance=0.6
                )
                
                if True in matches:
                    first_match_index = matches.index(True)
                    student_name = self.known_face_names[first_match_index]
                    
                    # Find student in roster
                    student_info = next(
                        (s for s in class_roster if s['name'] == student_name), None
                    )
                    
                    if student_info:
                        recognized_students.append({
                            'student_id': student_info['id'],
                            'name': student_name,
                            'confidence': 0.9,
                            'face_location': face_locations[0]
                        })
            
            return {
                "success": True,
                "recognized_students": recognized_students,
                "total_faces_detected": len(face_locations),
                "recognition_rate": len(recognized_students) / len(face_locations) if face_locations else 0,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in face recognition: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def analyze_student_behavior(self, video_data: str, duration_seconds: int = 30) -> Dict[str, Any]:
        """Analyze student behavior from video (if applicable)"""
        
        try:
            # This is a placeholder for video analysis
            # In a real implementation, you would use video processing libraries
            
            # Simulate behavior analysis
            behavior_metrics = {
                "attention_level": np.random.uniform(0.6, 0.9),
                "engagement_score": np.random.uniform(0.5, 0.8),
                "participation_rate": np.random.uniform(0.3, 0.7),
                "distraction_indicators": np.random.uniform(0.1, 0.4)
            }
            
            # Generate insights
            insights = self._generate_behavior_insights(behavior_metrics)
            
            return {
                "success": True,
                "behavior_metrics": behavior_metrics,
                "insights": insights,
                "recommendations": self._generate_behavior_recommendations(behavior_metrics),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in behavior analysis: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def _parse_qr_data(self, qr_data: str) -> Dict[str, Any]:
        """Parse QR code data"""
        
        try:
            # Expected format: "class_id:session_id:timestamp:teacher_id"
            parts = qr_data.split(':')
            
            if len(parts) >= 4:
                return {
                    "class_id": parts[0],
                    "session_id": parts[1],
                    "timestamp": parts[2],
                    "teacher_id": parts[3],
                    "raw_data": qr_data
                }
            else:
                return {"raw_data": qr_data, "error": "Invalid QR format"}
                
        except Exception as e:
            return {"raw_data": qr_data, "error": str(e)}
    
    def _verify_qr_validity(self, qr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify QR code validity"""
        
        try:
            # Check if session is still active
            session_timestamp = datetime.fromisoformat(qr_data.get('timestamp', ''))
            current_time = datetime.now()
            
            # QR codes are valid for 1 hour
            time_diff = (current_time - session_timestamp).total_seconds()
            
            return {
                "is_valid": time_diff < 3600,  # 1 hour
                "time_remaining": max(0, 3600 - time_diff),
                "session_age_seconds": time_diff
            }
            
        except Exception as e:
            return {"is_valid": False, "error": str(e)}
    
    def _preprocess_image_for_ocr(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for better OCR results"""
        
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Apply noise reduction
        denoised = cv2.medianBlur(gray, 3)
        
        # Apply thresholding
        _, thresholded = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresholded
    
    def _clean_ocr_text(self, text: str) -> str:
        """Clean OCR extracted text"""
        
        # Remove extra whitespace
        cleaned = ' '.join(text.split())
        
        # Remove common OCR artifacts
        cleaned = cleaned.replace('|', 'I')
        cleaned = cleaned.replace('0', 'O')  # Context-dependent
        
        return cleaned
    
    def _extract_structured_data(self, text: str, document_type: str) -> Dict[str, Any]:
        """Extract structured data from OCR text"""
        
        structured_data = {}
        
        if document_type == "assignment":
            # Extract assignment-specific data
            lines = text.split('\n')
            
            for line in lines:
                if 'name:' in line.lower():
                    structured_data['student_name'] = line.split(':')[1].strip()
                elif 'date:' in line.lower():
                    structured_data['date'] = line.split(':')[1].strip()
                elif 'grade:' in line.lower():
                    structured_data['grade'] = line.split(':')[1].strip()
        
        return structured_data
    
    def _calculate_ocr_confidence(self, processed_image: np.ndarray) -> float:
        """Calculate OCR confidence score"""
        
        # Simple confidence calculation based on image quality
        # In a real implementation, you would use more sophisticated methods
        
        # Calculate image clarity
        laplacian_var = cv2.Laplacian(processed_image, cv2.CV_64F).var()
        
        # Normalize confidence
        confidence = min(1.0, laplacian_var / 1000)
        
        return confidence
    
    def _generate_behavior_insights(self, metrics: Dict[str, float]) -> List[str]:
        """Generate insights from behavior metrics"""
        
        insights = []
        
        if metrics['attention_level'] < 0.7:
            insights.append("Student shows signs of reduced attention")
        
        if metrics['engagement_score'] > 0.8:
            insights.append("Student is highly engaged in the activity")
        
        if metrics['distraction_indicators'] > 0.3:
            insights.append("Student may need redirection")
        
        return insights
    
    def _generate_behavior_recommendations(self, metrics: Dict[str, float]) -> List[str]:
        """Generate recommendations based on behavior metrics"""
        
        recommendations = []
        
        if metrics['attention_level'] < 0.7:
            recommendations.append("Consider moving student closer to front")
            recommendations.append("Provide more interactive activities")
        
        if metrics['engagement_score'] < 0.6:
            recommendations.append("Incorporate more hands-on activities")
            recommendations.append("Use visual aids and multimedia")
        
        return recommendations 