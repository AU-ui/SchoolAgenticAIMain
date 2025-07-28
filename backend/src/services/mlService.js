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
}

module.exports = new MLService(); 