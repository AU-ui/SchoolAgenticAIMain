const express = require('express');
const router = express.Router();
const AIController = require('../controllers/AIController');

// AI Integration API Routes
router.post('/analyze-attendance', AIController.analyzeAttendance);    // AI analysis of attendance patterns
router.get('/insights/:classId', AIController.getAttendanceInsights);  // Get AI insights for a class
router.get('/recommendations', AIController.getRecommendations);       // Get AI recommendations
router.post('/predict-attendance', AIController.predictAttendance);    // Predict attendance issues

module.exports = router;
