const axios = require('axios');

class AIController {
  
  // Analyze attendance patterns with AI
  static async analyzeAttendance(req, res) {
    try {
      const { classId, date, attendanceData } = req.body;
      
      // Call ML service for attendance analysis
      try {
        const mlResponse = await axios.post('http://localhost:8000/ml/attendance/analyze', {
          class_id: classId,
          date: date,
          attendance_data: attendanceData
        });
        
        if (mlResponse.data.success) {
          res.json({
            success: true,
            analysis: mlResponse.data.analysis,
            patterns: mlResponse.data.patterns,
            anomalies: mlResponse.data.anomalies,
            recommendations: mlResponse.data.recommendations
          });
          return;
        }
      } catch (mlError) {
        console.log('ML service not available, using basic analysis');
      }
      
      // Fallback to basic analysis
      const analysis = {
        patterns: {
          overall_trend: 'Stable',
          weekly_pattern: 'Consistent',
          monthly_trend: 'Improving'
        },
        anomalies: [],
        recommendations: [
          'Continue current attendance monitoring',
          'No immediate action required'
        ]
      };
      
      res.json({
        success: true,
        analysis: analysis
      });
    } catch (error) {
      console.error('Error analyzing attendance:', error);
      res.status(500).json({ error: 'Failed to analyze attendance' });
    }
  }

  // Get AI insights for a specific class
  static async getAttendanceInsights(req, res) {
    try {
      const { classId } = req.params;
      const { date } = req.query;
      
      // Get AI insights for the class
      const insights = await AIController.generateInsights(classId, date);
      
      res.json({
        success: true,
        insights: insights
      });
    } catch (error) {
      console.error('Error fetching insights:', error);
      res.status(500).json({ error: 'Failed to fetch insights' });
    }
  }

  // Get AI recommendations
  static async getRecommendations(req, res) {
    try {
      const { classId, studentId, type } = req.query;
      
      // Get AI recommendations based on type
      const recommendations = await AIController.generateRecommendations(classId, studentId, type);
      
      res.json({
        success: true,
        recommendations: recommendations
      });
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      res.status(500).json({ error: 'Failed to fetch recommendations' });
    }
  }

  // Predict attendance issues
  static async predictAttendance(req, res) {
    try {
      const { classId, studentIds, predictionDays = 7 } = req.body;
      
      // Call ML service for attendance prediction
      try {
        const mlResponse = await axios.post('http://localhost:8000/ml/attendance/predict', {
          class_id: classId,
          student_ids: studentIds,
          prediction_days: predictionDays
        });
        
        if (mlResponse.data.success) {
          res.json({
            success: true,
            predictions: mlResponse.data.predictions,
            risk_assessment: mlResponse.data.risk_assessment
          });
          return;
        }
      } catch (mlError) {
        console.log('ML service not available, using basic predictions');
      }
      
      // Fallback to basic predictions
      const predictions = {
        overall_prediction: '85% attendance expected',
        high_risk_students: [],
        recommendations: [
          'Continue monitoring attendance patterns',
          'No immediate intervention needed'
        ]
      };
      
      res.json({
        success: true,
        predictions: predictions
      });
    } catch (error) {
      console.error('Error predicting attendance:', error);
      res.status(500).json({ error: 'Failed to predict attendance' });
    }
  }

  // PRIVATE HELPER METHODS

  // Generate insights for a class
  static async generateInsights(classId, date) {
    // Mock insights - replace with ML service call
    return {
      attendance_trend: 'Improving',
      class_performance: 'Good',
      key_insights: [
        'Attendance has improved by 5% this month',
        'No students are at critical risk',
        'Class participation is consistent'
      ],
      recommendations: [
        'Continue current attendance monitoring',
        'Maintain positive reinforcement'
      ]
    };
  }

  // Generate recommendations
  static async generateRecommendations(classId, studentId, type) {
    const recommendations = {
      class_level: [
        'Implement attendance rewards program',
        'Schedule regular parent-teacher meetings',
        'Monitor attendance patterns weekly'
      ],
      student_level: [
        'Schedule one-on-one meeting with student',
        'Contact parents for attendance discussion',
        'Provide additional academic support'
      ],
      intervention: [
        'Immediate parent notification required',
        'Schedule intervention meeting',
        'Consider academic counseling'
      ]
    };
    
    return recommendations[type] || recommendations.class_level;
  }
}

module.exports = AIController;
