const axios = require('axios');

class MLService {
    constructor() {
        this.baseURL = process.env.ML_SERVICE_URL || 'http://localhost:8000';
    }

    async analyzeSentiment(messages) {
        try {
            const response = await axios.post(`${this.baseURL}/api/ml/parent/sentiment/analyze`, {
                messages: messages,
                analyze_tone: true,
                detect_urgency: true
            });
            return response.data;
        } catch (error) {
            console.error('Sentiment analysis error:', error);
            return { success: false, data: [] };
        }
    }

    async translateMessage(text, sourceLanguage, targetLanguage) {
        try {
            const response = await axios.post(`${this.baseURL}/api/ml/parent/translation/translate`, {
                text: text,
                source_language: sourceLanguage,
                target_language: targetLanguage
            });
            return response.data;
        } catch (error) {
            console.error('Translation error:', error);
            return { success: false, data: { translated_text: text } };
        }
    }

    async predictEngagement(parentData, messageContent, messageType, sendTime) {
        try {
            const response = await axios.post(`${this.baseURL}/api/ml/parent/engagement/predict`, {
                parent_data: parentData,
                message_content: messageContent,
                message_type: messageType,
                send_time: sendTime
            });
            return response.data;
        } catch (error) {
            console.error('Engagement prediction error:', error);
            return { success: false, data: { response_probability: 0.5 } };
        }
    }

    async optimizeCommunicationStrategy(parentData) {
        try {
            const response = await axios.post(`${this.baseURL}/api/ml/parent/communication/optimize`, parentData);
            return response.data;
        } catch (error) {
            console.error('Communication optimization error:', error);
            return { success: false, data: {} };
        }
    }
}

module.exports = new MLService(); 