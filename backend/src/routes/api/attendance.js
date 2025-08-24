const express = require('express');
const router = express.Router();
const AttendanceController = require('../../../controllers/AttendanceController'); // FIXED PATH
const { authenticateToken, requireRole } = require('../../middleware/auth');

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
      
      const { pool } = require('../../config/database');
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
 * @desc    Mark attendance for students in a session
 * @access  Private (Teachers, Administrators, Backend Admins, Super Admins)
 */
router.post('/mark', 
  authenticateToken, 
  requireRole(['teacher', 'administrator', 'admin', 'superadmin']), 
  AttendanceController.markAttendance
);

/**
 * @route   PUT /api/attendance/records/:record_id
 * @desc    Update a specific attendance record
 * @access  Private (Teachers, Administrators, Backend Admins, Super Admins)
 */
router.put('/records/:record_id', 
  authenticateToken, 
  requireRole(['teacher', 'administrator', 'admin', 'superadmin']), 
  async (req, res) => {
    try {
      const { record_id } = req.params;
      const { status, arrival_time, notes } = req.body;
      
      const { pool } = require('../../config/database');
      
      const query = `
        UPDATE attendance_records 
        SET status = $1, arrival_time = $2, notes = $3, updated_at = CURRENT_TIMESTAMP
        WHERE record_id = $4
        RETURNING *
      `;
      
      const result = await pool.query(query, [status, arrival_time, notes, record_id]);
      
      if (result.rows.length === 0) {
        return res.status(404).json({
          success: false,
          message: 'Attendance record not found'
        });
      }
      
      res.status(200).json({
        success: true,
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
// ATTENDANCE HISTORY & ANALYTICS ROUTES
// ============================================================================

/**
 * @route   GET /api/attendance/student/:student_id/history
 * @desc    Get attendance history for a student
 * @access  Private (Teachers, Parents, Students, Administrators, Backend Admins, Super Admins)
 */
router.get('/student/:student_id/history', 
  authenticateToken, 
  requireRole(['teacher', 'parent', 'student', 'administrator', 'admin', 'superadmin']), 
  AttendanceController.getStudentAttendanceHistory
);

/**
 * @route   GET /api/attendance/student/:student_id/analytics
 * @desc    Get attendance analytics for a student
 * @access  Private (Teachers, Parents, Students, Administrators, Backend Admins, Super Admins)
 */
router.get('/student/:student_id/analytics', 
  authenticateToken, 
  requireRole(['teacher', 'parent', 'student', 'administrator', 'admin', 'superadmin']), 
  AttendanceController.getStudentAnalytics
);

/**
 * @route   GET /api/attendance/class/:class_id/summary
 * @desc    Get attendance summary for a class
 * @access  Private (Teachers, Administrators, Backend Admins, Super Admins)
 */
router.get('/class/:class_id/summary', 
  authenticateToken, 
  requireRole(['teacher', 'administrator', 'admin', 'superadmin']), 
  async (req, res) => {
    try {
      const { class_id } = req.params;
      const { date } = req.query;
      
      const { pool } = require('../../config/database');
      
      // Get students in the class
      const studentsQuery = `
        SELECT 
          u.id as student_id,
          u.first_name,
          u.last_name,
          u.email
        FROM users u
        WHERE u.role = 'student'
        ORDER BY u.first_name, u.last_name
      `;
      
      const studentsResult = await pool.query(studentsQuery);
      
      // Get attendance for the specified date
      let attendanceQuery = `
        SELECT 
          ar.student_id,
          ar.status,
          ar.arrival_time,
          ar.notes
        FROM attendance_records ar
        JOIN attendance_sessions as ON ar.session_id = as.session_id
        WHERE as.class_id = $1
      `;
      
      const params = [class_id];
      let paramIndex = 2;
      
      if (date) {
        attendanceQuery += ` AND as.session_date = $${paramIndex}`;
        params.push(date);
      } else {
        attendanceQuery += ` AND as.session_date = CURRENT_DATE`;
      }
      
      const attendanceResult = await pool.query(attendanceQuery, params);
      
      // Combine student data with attendance data
      const studentsWithAttendance = studentsResult.rows.map(student => {
        const attendance = attendanceResult.rows.find(a => a.student_id === student.student_id);
        return {
          ...student,
          attendance: attendance || null
        };
      });
      
      res.status(200).json({
        success: true,
        data: {
          students: studentsWithAttendance,
          date: date || new Date().toISOString().split('T')[0]
        }
      });
      
    } catch (error) {
      console.error('Error fetching class summary:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to fetch class summary',
        error: error.message
      });
    }
  }
);

/**
 * @route   GET /api/attendance/class/:class_id/analytics
 * @desc    Get attendance analytics for a class
 * @access  Private (Teachers, Administrators, Backend Admins, Super Admins)
 */
router.get('/class/:class_id/analytics', 
  authenticateToken, 
  requireRole(['teacher', 'administrator', 'admin', 'superadmin']), 
  AttendanceController.getClassAttendanceSummary
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
      
      const { pool } = require('../../config/database');
      
      const query = `
        SELECT 
          c.id as class_id,
          c.name as class_name,
          COUNT(ar.record_id) as total_students,
          COUNT(CASE WHEN ar.status = 'present' THEN 1 END) as present_count,
          COUNT(CASE WHEN ar.status = 'absent' THEN 1 END) as absent_count,
          COUNT(CASE WHEN ar.status = 'late' THEN 1 END) as late_count,
          ROUND(
            (COUNT(CASE WHEN ar.status = 'present' THEN 1 END)::DECIMAL / COUNT(ar.record_id)::DECIMAL) * 100, 2
          ) as attendance_percentage
        FROM classes c
        LEFT JOIN attendance_sessions as ON c.id = as.class_id
        LEFT JOIN attendance_records ar ON as.session_id = ar.session_id
        WHERE c.school_id = $1
        AND (as.session_date = $2 OR $2 IS NULL)
        GROUP BY c.id, c.name
        ORDER BY c.name
      `;
      
      const result = await pool.query(query, [school_id, date]);
      
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
      
      const { pool } = require('../../config/database');
      
      const query = `
        SELECT 
          DATE(as.session_date) as date,
          COUNT(ar.record_id) as total_students,
          COUNT(CASE WHEN ar.status = 'present' THEN 1 END) as present_count,
          COUNT(CASE WHEN ar.status = 'absent' THEN 1 END) as absent_count,
          COUNT(CASE WHEN ar.status = 'late' THEN 1 END) as late_count,
          ROUND(
            (COUNT(CASE WHEN ar.status = 'present' THEN 1 END)::DECIMAL / COUNT(ar.record_id)::DECIMAL) * 100, 2
          ) as attendance_percentage
        FROM classes c
        JOIN attendance_sessions as ON c.id = as.class_id
        JOIN attendance_records ar ON as.session_id = ar.session_id
        WHERE c.school_id = $1
        AND as.session_date BETWEEN $2 AND $3
        GROUP BY DATE(as.session_date)
        ORDER BY date DESC
      `;
      
      const result = await pool.query(query, [school_id, start_date, end_date]);
      
      res.status(200).json({
        success: true,
        data: result.rows
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
 * @desc    Get AI predictions for student attendance
 * @access  Private (Teachers, Parents, Students, Administrators, Backend Admins, Super Admins)
 */
router.get('/smart/predictions/:student_id', 
  authenticateToken, 
  requireRole(['teacher', 'parent', 'student', 'administrator', 'admin', 'superadmin']), 
  AttendanceController.getAIPredictions
);

/**
 * @route   POST /api/attendance/smart/analyze
 * @desc    Trigger AI analysis for attendance patterns
 * @access  Private (Teachers, Administrators, Backend Admins, Super Admins)
 */
router.post('/smart/analyze', 
  authenticateToken, 
  requireRole(['teacher', 'administrator', 'admin', 'superadmin']), 
  AttendanceController.triggerAIAnalysis
);

/**
 * @route   GET /api/attendance/risk-students
 * @desc    Get students at risk based on AI analysis
 * @access  Private (Teachers, Administrators, Backend Admins, Super Admins)
 */
router.get('/risk-students', 
  authenticateToken, 
  requireRole(['teacher', 'administrator', 'admin', 'superadmin']), 
  AttendanceController.getRiskStudents
);

/**
 * @route   POST /api/attendance/smart/retrain
 * @desc    Retrain AI models with new data
 * @access  Private (Administrators, Backend Admins, Super Admins)
 */
router.post('/smart/retrain', 
  authenticateToken, 
  requireRole(['administrator', 'admin', 'superadmin']), 
  AttendanceController.retrainModels
);

module.exports = router;
