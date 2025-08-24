const axios = require('axios');

class MLService {
    constructor() {
        this.baseURL = process.env.ML_SERVICE_URL || 'http://localhost:8000';
        this.timeout = process.env.ML_SERVICE_TIMEOUT || 10000;
    }

    async makeRequest(endpoint, data = null, method = 'POST') {
        try {
            const config = {
                method,
                url: `${this.baseURL}${endpoint}`,
                timeout: this.timeout,
                headers: {
                    'Content-Type': 'application/json'
                }
            };

            if (data) {
                config.data = data;
            }

            const response = await axios(config);
            return response.data;
        } catch (error) {
            console.error(`ML Service Error (${endpoint}):`, error.message);
            return { success: false, error: error.message };
        }
    }

    // Teacher Analytics Methods
    async analyzeAttendancePatterns(attendanceData) {
        return await this.makeRequest('/api/ml/teacher/attendance/analyze', attendanceData);
    }

    async predictStudentPerformance(studentData) {
        return await this.makeRequest('/api/ml/teacher/performance/predict', studentData);
    }

    async optimizeTimetable(classData, teacherPreferences) {
        return await this.makeRequest('/api/ml/teacher/timetable/optimize', {
            class_data: classData,
            teacher_preferences: teacherPreferences
        });
    }

    async generateAIReport(reportType, data, templateId = null) {
        return await this.makeRequest('/api/ml/teacher/reports/generate', {
            report_type: reportType,
            data: data,
            template_id: templateId
        });
    }

    // Parent Analytics Methods
    async analyzeSentiment(messages) {
        return await this.makeRequest('/api/ml/parent/sentiment/analyze', {
            messages: messages,
            analyze_tone: true,
            detect_urgency: true
        });
    }

    async translateMessage(text, sourceLanguage, targetLanguage) {
        return await this.makeRequest('/api/ml/parent/translation/translate', {
            text: text,
            source_language: sourceLanguage,
            target_language: targetLanguage
        });
    }

    async predictEngagement(parentData, messageContent, messageType, sendTime) {
        return await this.makeRequest('/api/ml/parent/engagement/predict', {
            parent_data: parentData,
            message_content: messageContent,
            message_type: messageType,
            send_time: sendTime
        });
    }

    async optimizeCommunicationStrategy(parentData) {
        return await this.makeRequest('/api/ml/parent/communication/optimize', parentData);
    }

    async getParentInsights(parentId) {
        return await this.makeRequest(`/api/ml/parent/insights/${parentId}`, null, 'GET');
    }

    async scheduleSmartNotifications(parentData) {
        return await this.makeRequest('/api/ml/parent/notifications/smart-schedule', parentData);
    }

    async analyzeLanguagePreferences(messages) {
        return await this.makeRequest('/api/ml/parent/language/preferences', messages);
    }

    async classifyEmergencyUrgency(message) {
        return await this.makeRequest('/api/ml/parent/emergency/classify', message);
    }

    // Health check
    async healthCheck() {
        return await this.makeRequest('/health', null, 'GET');
    }

    // Simple ML service with mock data for now
    async getAttendanceInsights(classId) {
      // Mock AI insights
      return {
        total_students: 25,
        attendance_rate: 0.92,
        risk_students: 3,
        trends: {
          improving: 15,
          declining: 2,
          stable: 8
        },
        recommendations: [
          "Student John Doe shows declining attendance pattern",
          "Consider intervention for students with <80% attendance",
          "Class attendance is above school average"
        ]
      };
    }

    async getAttendancePredictions(params) {
      // Mock predictions
      return params.students.map(studentId => ({
        student_id: studentId,
        attendance_probability: 0.85 + Math.random() * 0.1,
        risk_level: Math.random() > 0.8 ? 'high' : 'low',
        trend: Math.random() > 0.5 ? 'improving' : 'stable'
      }));
    }

    async checkAttendanceAnomalies(params) {
      // Mock anomaly check
      return {
        has_anomalies: false,
        anomalies: [],
        confidence: 0.95
      };
    }
}

module.exports = new MLService(); 