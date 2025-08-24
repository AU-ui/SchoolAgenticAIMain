const express = require('express');
const router = express.Router();
const AttendanceController = require('../controllers/AttendanceController');
const { authenticateToken, requireRole } = require('../src/middleware/auth');

// ============================================================================
// ATTENDANCE SESSION MANAGEMENT ROUTES
// ============================================================================

/**
 * @route   POST /api/attendance/sessions
 * @desc    Create a new attendance session
 * @access  Private (Teachers, Administrators, Backend Admins, Super Admins)
 */
router.post('/sessions', 
  authenticateToken, 
  requireRole(['teacher', 'administrator', 'admin', 'superadmin']), 
  AttendanceController.createAttendanceSession
);

/**
 * @route   GET /api/attendance/sessions/:session_id
 * @desc    Get attendance for a specific session
 * @access  Private (All roles: Teachers, Parents, Students, Administrators, Backend Admins, Super Admins)
 */
router.get('/sessions/:session_id', 
  authenticateToken, 
  requireRole(['teacher', 'parent', 'student', 'administrator', 'admin', 'superadmin']), 
  AttendanceController.getSessionAttendance
);

/**
 * @route   GET /api/attendance/sessions/class/:class_id
 * @desc    Get all sessions for a class
 * @access  Private (Teachers, Administrators, Backend Admins, Super Admins)
 */
router.get('/sessions/class/:class_id', 
  authenticateToken, 
  requireRole(['teacher', 'administrator', 'admin', 'superadmin']), 
  async (req, res) => {
    try {
      const { class_id } = req.params;
      const { start_date, end_date } = req.query;
      
      let query = `
        SELECT 
          as.session_id,
          as.session_date,
          as.session_time,
          as.session_type,
          as.status,
          as.created_at,
          u.first_name as teacher_first_name,
          u.last_name as teacher_last_name
        FROM attendance_sessions as
        JOIN users u ON as.teacher_id = u.id
        WHERE as.class_id = $1
      `;
      
      const params = [class_id];
      let paramIndex = 2;
      
      if (start_date) {
        query += ` AND as.session_date >= $${paramIndex}`;
        params.push(start_date);
        paramIndex++;
      }
      
      if (end_date) {
        query += ` AND as.session_date <= $${paramIndex}`;
        params.push(end_date);
      }
      
      query += ` ORDER BY as.session_date DESC, as.session_time DESC`;
      
      const { pool } = require('../src/config/database');
      const result = await pool.query(query, params);
      
      res.status(200).json({
        success: true,
        data: result.rows
      });
      
    } catch (error) {
      console.error('Error fetching class sessions:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to fetch class sessions',
        error: error.message
      });
    }
  }
);

// ============================================================================
// ATTENDANCE MARKING ROUTES
// ============================================================================

/**
 * @route   POST /api/attendance/mark
 * @desc    Mark attendance for students
 * @access  Private (Teachers, Administrators, Backend Admins, Super Admins)
 */
router.post('/mark', 
  authenticateToken, 
  requireRole(['teacher', 'administrator', 'admin', 'superadmin']), 
  AttendanceController.markAttendance
);

/**
 * @route   PUT /api/attendance/mark/:record_id
 * @desc    Update a specific attendance record
 * @access  Private (Teachers, Administrators, Backend Admins, Super Admins)
 */
router.put('/mark/:record_id', 
  authenticateToken, 
  requireRole(['teacher', 'administrator', 'admin', 'superadmin']), 
  async (req, res) => {
    try {
      const { record_id } = req.params;
      const { status, arrival_time, departure_time, notes } = req.body;
      const { id: marked_by } = req.user; // Get user ID from token
      
      // Validate status
      if (status && !['present', 'absent', 'late', 'excused'].includes(status)) {
        return res.status(400).json({
          success: false,
          message: 'Invalid status. Must be present, absent, late, or excused'
        });
      }
      
      const { pool } = require('../src/config/database');
      const result = await pool.query(
        `UPDATE attendance_records 
         SET status = COALESCE($1, status),
             arrival_time = COALESCE($2, arrival_time),
             departure_time = COALESCE($3, departure_time),
             notes = COALESCE($4, notes),
             marked_by = $5,
             updated_at = CURRENT_TIMESTAMP
         WHERE record_id = $6
         RETURNING *`,
        [status, arrival_time, departure_time, notes, marked_by, record_id]
      );
      
      if (result.rows.length === 0) {
        return res.status(404).json({
          success: false,
          message: 'Attendance record not found'
        });
      }
      
      res.status(200).json({
        success: true,
        message: 'Attendance record updated successfully',
        data: result.rows[0]
      });
      
    } catch (error) {
      console.error('Error updating attendance record:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to update attendance record',
        error: error.message
      });
    }
  }
);

// ============================================================================
// ATTENDANCE HISTORY ROUTES
// ============================================================================

/**
 * @route   GET /api/attendance/student/:student_id/history
 * @desc    Get student attendance history
 * @access  Private (All roles: Teachers, Parents, Students, Administrators, Backend Admins, Super Admins)
 */
router.get('/student/:student_id/history', 
  authenticateToken, 
  requireRole(['teacher', 'parent', 'student', 'administrator', 'admin', 'superadmin']), 
  AttendanceController.getStudentAttendanceHistory
);

/**
 * @route   GET /api/attendance/student/:student_id/analytics
 * @desc    Get student attendance analytics
 * @access  Private (All roles: Teachers, Parents, Students, Administrators, Backend Admins, Super Admins)
 */
router.get('/student/:student_id/analytics', 
  authenticateToken, 
  requireRole(['teacher', 'parent', 'student', 'administrator', 'admin', 'superadmin']), 
  AttendanceController.getStudentAnalytics
);

// ============================================================================
// CLASS ATTENDANCE ROUTES
// ============================================================================

/**
 * @route   GET /api/attendance/class/:class_id/summary
 * @desc    Get class attendance summary
 * @access  Private (Teachers, Administrators, Backend Admins, Super Admins)
 */
router.get('/class/:class_id/summary', 
  authenticateToken, 
  requireRole(['teacher', 'administrator', 'admin', 'superadmin']), 
  AttendanceController.getClassAttendanceSummary
);

/**
 * @route   GET /api/attendance/class/:class_id/analytics
 * @desc    Get class attendance analytics
 * @access  Private (Teachers, Administrators, Backend Admins, Super Admins)
 */
router.get('/class/:class_id/analytics', 
  authenticateToken, 
  requireRole(['teacher', 'administrator', 'admin', 'superadmin']), 
  async (req, res) => {
    try {
      const { class_id } = req.params;
      const { start_date, end_date } = req.query;
      
      // Calculate date range if not provided
      const endDate = end_date || new Date().toISOString().split('T')[0];
      const startDate = start_date || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      
      const { pool } = require('../src/config/database');
      const result = await pool.query(
        `SELECT 
           COUNT(*) as total_sessions,
           COUNT(CASE WHEN ar.status = 'present' THEN 1 END) as present_count,
           COUNT(CASE WHEN ar.status = 'absent' THEN 1 END) as absent_count,
           COUNT(CASE WHEN ar.status = 'late' THEN 1 END) as late_count,
           COUNT(CASE WHEN ar.status = 'excused' THEN 1 END) as excused_count,
           ROUND(
             (COUNT(CASE WHEN ar.status = 'present' THEN 1 END) * 100.0 / COUNT(*)), 2
           ) as overall_attendance_percentage
         FROM attendance_records ar
         JOIN attendance_sessions as ON ar.session_id = as.session_id
         WHERE as.class_id = $1 
         AND as.session_date BETWEEN $2 AND $3`,
        [class_id, startDate, endDate]
      );
      
      const analytics = result.rows[0];
      
      // Add AI insights placeholder
      analytics.ai_insights = {
        trend: 'stable',
        recommendation: 'Continue current attendance practices',
        risk_students: []
      };
      
      res.status(200).json({
        success: true,
        data: analytics
      });
      
    } catch (error) {
      console.error('Error fetching class analytics:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to fetch class analytics',
        error: error.message
      });
    }
  }
);

// ============================================================================
// SCHOOL-WIDE ATTENDANCE ROUTES (Admin & Super Admin Only)
// ============================================================================

/**
 * @route   GET /api/attendance/school/:school_id/overview
 * @desc    Get school-wide attendance overview
 * @access  Private (Administrators, Backend Admins, Super Admins)
 */
router.get('/school/:school_id/overview', 
  authenticateToken, 
  requireRole(['administrator', 'admin', 'superadmin']), 
  async (req, res) => {
    try {
      const { school_id } = req.params;
      const { date } = req.query;
      
      const { pool } = require('../src/config/database');
      const result = await pool.query(
        `SELECT 
           c.id as class_id,
           c.name as class_name,
           COUNT(ar.record_id) as total_students,
           COUNT(CASE WHEN ar.status = 'present' THEN 1 END) as present_count,
           COUNT(CASE WHEN ar.status = 'absent' THEN 1 END) as absent_count,
           COUNT(CASE WHEN ar.status = 'late' THEN 1 END) as late_count,
           ROUND(
             (COUNT(CASE WHEN ar.status = 'present' THEN 1 END) * 100.0 / COUNT(ar.record_id)), 2
           ) as attendance_percentage
         FROM classes c
         LEFT JOIN attendance_sessions as ON c.id = as.class_id
         LEFT JOIN attendance_records ar ON as.session_id = ar.session_id
         WHERE c.school_id = $1
         ${date ? 'AND as.session_date = $2' : ''}
         GROUP BY c.id, c.name
         ORDER BY c.name`,
        date ? [school_id, date] : [school_id]
      );
      
      res.status(200).json({
        success: true,
        data: result.rows
      });
      
    } catch (error) {
      console.error('Error fetching school overview:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to fetch school overview',
        error: error.message
      });
    }
  }
);

/**
 * @route   GET /api/attendance/school/:school_id/analytics
 * @desc    Get school-wide attendance analytics
 * @access  Private (Administrators, Backend Admins, Super Admins)
 */
router.get('/school/:school_id/analytics', 
  authenticateToken, 
  requireRole(['administrator', 'admin', 'superadmin']), 
  async (req, res) => {
    try {
      const { school_id } = req.params;
      const { start_date, end_date } = req.query;
      
      const endDate = end_date || new Date().toISOString().split('T')[0];
      const startDate = start_date || new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      
      const { pool } = require('../src/config/database');
      const result = await pool.query(
        `SELECT 
           COUNT(DISTINCT ar.record_id) as total_attendance_records,
           COUNT(DISTINCT CASE WHEN ar.status = 'present' THEN ar.record_id END) as total_present,
           COUNT(DISTINCT CASE WHEN ar.status = 'absent' THEN ar.record_id END) as total_absent,
           COUNT(DISTINCT CASE WHEN ar.status = 'late' THEN ar.record_id END) as total_late,
           ROUND(
             (COUNT(DISTINCT CASE WHEN ar.status = 'present' THEN ar.record_id END) * 100.0 / COUNT(DISTINCT ar.record_id)), 2
           ) as overall_attendance_percentage
         FROM attendance_records ar
         JOIN attendance_sessions as ON ar.session_id = as.session_id
         JOIN classes c ON as.class_id = c.id
         WHERE c.school_id = $1 
         AND as.session_date BETWEEN $2 AND $3`,
        [school_id, startDate, endDate]
      );
      
      const analytics = result.rows[0];
      
      res.status(200).json({
        success: true,
        data: analytics
      });
      
    } catch (error) {
      console.error('Error fetching school analytics:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to fetch school analytics',
        error: error.message
      });
    }
  }
);

// ============================================================================
// SMART ATTENDANCE ROUTES (AI/ML Integration)
// ============================================================================

/**
 * @route   GET /api/attendance/smart/predictions/:student_id
 * @desc    Get AI-powered attendance predictions for a student
 * @access  Private (All roles: Teachers, Parents, Students, Administrators, Backend Admins, Super Admins)
 */
router.get('/smart/predictions/:student_id', 
  authenticateToken, 
  requireRole(['teacher', 'parent', 'student', 'administrator', 'admin', 'superadmin']), 
  async (req, res) => {
    try {
      const { student_id } = req.params;
      
      // Placeholder for AI/ML integration
      // This will be connected to the ML service later
      const predictions = {
        next_week_attendance: 85.5,
        risk_level: 'low',
        pattern: 'consistent',
        recommendations: [
          'Student shows good attendance pattern',
          'Continue current routine',
          'Monitor for any changes'
        ]
      };
      
      res.status(200).json({
        success: true,
        data: predictions
      });
      
    } catch (error) {
      console.error('Error fetching attendance predictions:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to fetch attendance predictions',
        error: error.message
      });
    }
  }
);

/**
 * @route   POST /api/attendance/smart/analyze
 * @desc    Trigger AI analysis of attendance patterns
 * @access  Private (Teachers, Administrators, Backend Admins, Super Admins)
 */
router.post('/smart/analyze', 
  authenticateToken, 
  requireRole(['teacher', 'administrator', 'admin', 'superadmin']), 
  async (req, res) => {
    try {
      const { class_id, analysis_type = 'comprehensive' } = req.body;
      
      // Placeholder for AI analysis
      const analysis = {
        class_id,
        analysis_type,
        timestamp: new Date().toISOString(),
        insights: {
          overall_trend: 'improving',
          at_risk_students: [],
          recommendations: [
            'Overall class attendance is improving',
            'Continue positive reinforcement',
            'Monitor specific students for patterns'
          ]
        }
      };
      
      res.status(200).json({
        success: true,
        message: 'AI analysis completed successfully',
        data: analysis
      });
      
    } catch (error) {
      console.error('Error performing AI analysis:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to perform AI analysis',
        error: error.message
      });
    }
  }
);

module.exports = router;
