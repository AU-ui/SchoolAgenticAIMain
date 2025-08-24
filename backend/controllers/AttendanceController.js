const { pool } = require('../src/config/database');
const axios = require('axios');

// ML Service Configuration
const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:5001';

class AttendanceController {
  
  // ============================================================================
  // CORE ATTENDANCE OPERATIONS
  // ============================================================================
  
  /**
   * Create a new attendance session
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async createAttendanceSession(req, res) {
    try {
      const { class_id, teacher_id, session_date, session_time, session_type = 'regular' } = req.body;
      
      // Validate required fields
      if (!class_id || !teacher_id || !session_date || !session_time) {
        return res.status(400).json({
          success: false,
          message: 'Missing required fields: class_id, teacher_id, session_date, session_time'
        });
      }
      
      // Check if session already exists
      const existingSession = await pool.query(
        'SELECT session_id FROM attendance_sessions WHERE class_id = $1 AND session_date = $2 AND session_time = $3',
        [class_id, session_date, session_time]
      );
      
      if (existingSession.rows.length > 0) {
        return res.status(409).json({
          success: false,
          message: 'Attendance session already exists for this class, date, and time'
        });
      }
      
      // Create new session
      const result = await pool.query(
        `INSERT INTO attendance_sessions 
         (class_id, teacher_id, session_date, session_time, session_type) 
         VALUES ($1, $2, $3, $4, $5) 
         RETURNING *`,
        [class_id, teacher_id, session_date, session_time, session_type]
      );
      
      res.status(201).json({
        success: true,
        message: 'Attendance session created successfully',
        data: result.rows[0]
      });
      
    } catch (error) {
      console.error('Error creating attendance session:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to create attendance session',
        error: error.message
      });
    }
  }
  
  /**
   * Mark attendance for students
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async markAttendance(req, res) {
    try {
      const { session_id, attendance_data, marked_by } = req.body;
      
      // Validate required fields
      if (!session_id || !attendance_data || !marked_by) {
        return res.status(400).json({
          success: false,
          message: 'Missing required fields: session_id, attendance_data, marked_by'
        });
      }
      
      // Validate attendance_data structure
      if (!Array.isArray(attendance_data)) {
        return res.status(400).json({
          success: false,
          message: 'attendance_data must be an array'
        });
      }
      
      // Validate each attendance record
      for (const record of attendance_data) {
        if (!record.student_id || !record.status) {
          return res.status(400).json({
            success: false,
            message: 'Each attendance record must have student_id and status'
          });
        }
        
        if (!['present', 'absent', 'late', 'excused'].includes(record.status)) {
          return res.status(400).json({
            success: false,
            message: `Invalid status: ${record.status}. Must be present, absent, late, or excused`
          });
        }
      }
      
      // Check if session exists
      const sessionExists = await pool.query(
        'SELECT session_id FROM attendance_sessions WHERE session_id = $1',
        [session_id]
      );
      
      if (sessionExists.rows.length === 0) {
        return res.status(404).json({
          success: false,
          message: 'Attendance session not found'
        });
      }
      
      // Insert attendance records
      const results = [];
      for (const record of attendance_data) {
        const result = await pool.query(
          `INSERT INTO attendance_records 
           (session_id, student_id, status, arrival_time, departure_time, notes, marked_by) 
           VALUES ($1, $2, $3, $4, $5, $6, $7) 
           ON CONFLICT (session_id, student_id) 
           DO UPDATE SET 
             status = EXCLUDED.status,
             arrival_time = EXCLUDED.arrival_time,
             departure_time = EXCLUDED.departure_time,
             notes = EXCLUDED.notes,
             marked_by = EXCLUDED.marked_by,
             updated_at = CURRENT_TIMESTAMP
           RETURNING *`,
          [
            session_id,
            record.student_id,
            record.status,
            record.arrival_time || null,
            record.departure_time || null,
            record.notes || null,
            marked_by
          ]
        );
        
        results.push(result.rows[0]);
      }
      
      res.status(200).json({
        success: true,
        message: 'Attendance marked successfully',
        data: results
      });
      
    } catch (error) {
      console.error('Error marking attendance:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to mark attendance',
        error: error.message
      });
    }
  }
  
  // ============================================================================
  // ATTENDANCE RETRIEVAL OPERATIONS
  // ============================================================================
  
  /**
   * Get attendance for a specific session
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async getSessionAttendance(req, res) {
    try {
      const { session_id } = req.params;
      
      const result = await pool.query(
        `SELECT 
           ar.record_id,
           ar.student_id,
           ar.status,
           ar.arrival_time,
           ar.departure_time,
           ar.notes,
           ar.marked_by,
           ar.created_at,
           u.first_name,
           u.last_name,
           u.email
         FROM attendance_records ar
         JOIN users u ON ar.student_id = u.id
         WHERE ar.session_id = $1
         ORDER BY u.first_name, u.last_name`,
        [session_id]
      );
      
      res.status(200).json({
        success: true,
        data: result.rows
      });
      
    } catch (error) {
      console.error('Error fetching session attendance:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to fetch session attendance',
        error: error.message
      });
    }
  }
  
  /**
   * Get student attendance history
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async getStudentAttendanceHistory(req, res) {
    try {
      const { student_id } = req.params;
      const { start_date, end_date, class_id } = req.query;
      
      let query = `
        SELECT 
          ar.record_id,
          ar.session_id,
          ar.status,
          ar.arrival_time,
          ar.departure_time,
          ar.notes,
          ar.created_at,
          as.session_date,
          as.session_time,
          as.session_type,
          c.name as class_name,
          u.first_name as teacher_first_name,
          u.last_name as teacher_last_name
        FROM attendance_records ar
        JOIN attendance_sessions as ON ar.session_id = as.session_id
        JOIN classes c ON as.class_id = c.id
        JOIN users u ON as.teacher_id = u.id
        WHERE ar.student_id = $1
      `;
      
      const params = [student_id];
      let paramIndex = 2;
      
      if (start_date) {
        query += ` AND as.session_date >= $${paramIndex}`;
        params.push(start_date);
        paramIndex++;
      }
      
      if (end_date) {
        query += ` AND as.session_date <= $${paramIndex}`;
        params.push(end_date);
        paramIndex++;
      }
      
      if (class_id) {
        query += ` AND as.class_id = $${paramIndex}`;
        params.push(class_id);
      }
      
      query += ` ORDER BY as.session_date DESC, as.session_time DESC`;
      
      const result = await pool.query(query, params);
      
      res.status(200).json({
        success: true,
        data: result.rows
      });
      
    } catch (error) {
      console.error('Error fetching student attendance history:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to fetch student attendance history',
        error: error.message
      });
    }
  }
  
  // ============================================================================
  // ANALYTICS OPERATIONS (Enhanced with ML)
  // ============================================================================
  
  /**
   * Get student attendance analytics with AI predictions
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async getStudentAnalytics(req, res) {
    try {
      const { student_id } = req.params;
      const { period_type = 'monthly', months = 3 } = req.query;
      
      // Calculate date range
      const endDate = new Date();
      const startDate = new Date();
      startDate.setMonth(startDate.getMonth() - parseInt(months));
      
      const result = await pool.query(
        `SELECT 
           COUNT(*) as total_sessions,
           COUNT(CASE WHEN ar.status = 'present' THEN 1 END) as present_count,
           COUNT(CASE WHEN ar.status = 'absent' THEN 1 END) as absent_count,
           COUNT(CASE WHEN ar.status = 'late' THEN 1 END) as late_count,
           COUNT(CASE WHEN ar.status = 'excused' THEN 1 END) as excused_count,
           ROUND(
             (COUNT(CASE WHEN ar.status = 'present' THEN 1 END) * 100.0 / COUNT(*)), 2
           ) as attendance_percentage
         FROM attendance_records ar
         JOIN attendance_sessions as ON ar.session_id = as.session_id
         WHERE ar.student_id = $1 
         AND as.session_date BETWEEN $2 AND $3`,
        [student_id, startDate.toISOString().split('T')[0], endDate.toISOString().split('T')[0]]
      );
      
      const analytics = result.rows[0];
      
      // Get AI predictions from ML service
      try {
        const mlResponse = await axios.get(`${ML_SERVICE_URL}/predict/${student_id}`);
        if (mlResponse.data.success) {
          analytics.ai_prediction = mlResponse.data.data;
        }
      } catch (mlError) {
        console.warn('ML service not available, using fallback prediction');
        analytics.ai_prediction = {
          predicted_attendance: analytics.attendance_percentage / 100,
          attendance_probability: analytics.attendance_percentage / 100,
          risk_score: analytics.attendance_percentage < 70 ? -0.5 : 0.2,
          risk_level: analytics.attendance_percentage < 70 ? 'high' : 'low',
          confidence: 0.8
        };
      }
      
      res.status(200).json({
        success: true,
        data: analytics
      });
      
    } catch (error) {
      console.error('Error fetching student analytics:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to fetch student analytics',
        error: error.message
      });
    }
  }
  
  /**
   * Get class attendance summary with AI insights
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async getClassAttendanceSummary(req, res) {
    try {
      const { class_id } = req.params;
      const { date } = req.query;
      
      let query = `
        SELECT 
          u.id as student_id,
          u.first_name,
          u.last_name,
          u.email,
          ar.status,
          ar.arrival_time,
          ar.notes
        FROM users u
        LEFT JOIN attendance_records ar ON u.id = ar.student_id
        LEFT JOIN attendance_sessions as ON ar.session_id = as.session_id
        WHERE u.role = 'student'
        AND u.id IN (
          SELECT DISTINCT student_id 
          FROM students 
          WHERE class_id = $1
        )
      `;
      
      const params = [class_id];
      
      if (date) {
        query += ` AND as.session_date = $2`;
        params.push(date);
      }
      
      query += ` ORDER BY u.first_name, u.last_name`;
      
      const result = await pool.query(query, params);
      
      // Get AI insights for the class
      let aiInsights = null;
      try {
        const mlResponse = await axios.get(`${ML_SERVICE_URL}/analyze?class_id=${class_id}`);
        if (mlResponse.data.success) {
          aiInsights = mlResponse.data.data;
        }
      } catch (mlError) {
        console.warn('ML service not available for class insights');
      }
      
      res.status(200).json({
        success: true,
        data: {
          students: result.rows,
          ai_insights: aiInsights
        }
      });
      
    } catch (error) {
      console.error('Error fetching class attendance summary:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to fetch class attendance summary',
        error: error.message
      });
    }
  }
  
  // ============================================================================
  // AI/ML INTEGRATION OPERATIONS
  // ============================================================================
  
  /**
   * Get AI-powered attendance predictions for a student
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async getAIPredictions(req, res) {
    try {
      const { student_id } = req.params;
      const { days_ahead = 7 } = req.query;
      
      // Call ML service for predictions
      const mlResponse = await axios.get(`${ML_SERVICE_URL}/predict/${student_id}?days_ahead=${days_ahead}`);
      
      if (mlResponse.data.success) {
        res.status(200).json({
          success: true,
          data: mlResponse.data.data
        });
      } else {
        res.status(404).json({
          success: false,
          message: 'No prediction data available'
        });
      }
      
    } catch (error) {
      console.error('Error fetching AI predictions:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to fetch AI predictions',
        error: error.message
      });
    }
  }
  
  /**
   * Get students at risk of poor attendance
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async getRiskStudents(req, res) {
    try {
      const { class_id, threshold = 0.7 } = req.query;
      
      // Call ML service for risk assessment
      const mlResponse = await axios.get(`${ML_SERVICE_URL}/risk-students?class_id=${class_id}&threshold=${threshold}`);
      
      if (mlResponse.data.success) {
        res.status(200).json({
          success: true,
          data: mlResponse.data.data
        });
      } else {
        res.status(404).json({
          success: false,
          message: 'No risk data available'
        });
      }
      
    } catch (error) {
      console.error('Error fetching risk students:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to fetch risk students',
        error: error.message
      });
    }
  }
  
  /**
   * Trigger AI analysis of attendance patterns
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async triggerAIAnalysis(req, res) {
    try {
      const { class_id, analysis_type = 'comprehensive' } = req.body;
      
      // Call ML service for analysis
      const mlResponse = await axios.post(`${ML_SERVICE_URL}/analyze`, {
        class_id,
        analysis_type
      });
      
      if (mlResponse.data.success) {
        res.status(200).json({
          success: true,
          message: 'AI analysis completed successfully',
          data: mlResponse.data.data
        });
      } else {
        res.status(500).json({
          success: false,
          message: 'AI analysis failed'
        });
      }
      
    } catch (error) {
      console.error('Error triggering AI analysis:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to trigger AI analysis',
        error: error.message
      });
    }
  }
  
  /**
   * Retrain ML models
   * @param {Object} req - Express request object
   * @param {Object} res - Express response object
   */
  static async retrainModels(req, res) {
    try {
      // Call ML service to retrain models
      const mlResponse = await axios.post(`${ML_SERVICE_URL}/train`);
      
      if (mlResponse.data.success) {
        res.status(200).json({
          success: true,
          message: 'Models retrained successfully'
        });
      } else {
        res.status(500).json({
          success: false,
          message: 'Model retraining failed'
        });
      }
      
    } catch (error) {
      console.error('Error retraining models:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to retrain models',
        error: error.message
      });
    }
  }
}

module.exports = AttendanceController;
