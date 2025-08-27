const express = require('express');
const router = express.Router();
const AttendanceController = require('../../../controllers/AttendanceController'); // FIXED PATH
const { authenticateToken, requireRole } = require('../../middleware/auth');
const { query } = require('../../config/database'); // Added for QR code routes

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
          ass.session_id,
          ass.session_date,
          ass.session_time,
          ass.session_type,
          ass.status,
          ass.created_at,
          u.first_name as teacher_first_name,
          u.last_name as teacher_last_name
        FROM attendance_sessions ass
        JOIN users u ON ass.teacher_id = u.id
        WHERE ass.class_id = $1
      `;
      
      const params = [class_id];
      let paramIndex = 2;
      
      if (start_date) {
        query += ` AND ass.session_date >= $${paramIndex}`;
        params.push(start_date);
        paramIndex++;
      }
      
      if (end_date) {
        query += ` AND ass.session_date <= $${paramIndex}`;
        params.push(end_date);
      }
      
      query += ` ORDER BY ass.session_date DESC, ass.session_time DESC`;
      
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
        JOIN class_students cs ON u.id = cs.student_id
        WHERE cs.class_id = $1 AND cs.is_active = true AND u.role = 'student'
        ORDER BY u.first_name, u.last_name
      `;
      
      const studentsResult = await pool.query(studentsQuery, [class_id]);
      
      // Get attendance for the specified date
      let attendanceQuery = `
        SELECT 
          ar.student_id,
          ar.status,
          ar.arrival_time,
          ar.notes
        FROM attendance_records ar
        JOIN attendance_sessions ass ON ar.session_id = ass.session_id
        WHERE ass.class_id = $1
      `;
      
      const params = [class_id];
      let paramIndex = 2;
      
      if (date) {
        attendanceQuery += ` AND ass.session_date = $${paramIndex}`;
        params.push(date);
      } else {
        attendanceQuery += ` AND ass.session_date = CURRENT_DATE`;
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
        LEFT JOIN attendance_sessions ass ON c.id = ass.class_id
        LEFT JOIN attendance_records ar ON ass.session_id = ar.session_id
        WHERE c.school_id = $1
        AND (ass.session_date = $2 OR $2 IS NULL)
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
          DATE(ass.session_date) as date,
          COUNT(ar.record_id) as total_students,
          COUNT(CASE WHEN ar.status = 'present' THEN 1 END) as present_count,
          COUNT(CASE WHEN ar.status = 'absent' THEN 1 END) as absent_count,
          COUNT(CASE WHEN ar.status = 'late' THEN 1 END) as late_count,
          ROUND(
            (COUNT(CASE WHEN ar.status = 'present' THEN 1 END)::DECIMAL / COUNT(ar.record_id)::DECIMAL) * 100, 2
          ) as attendance_percentage
        FROM classes c
        JOIN attendance_sessions ass ON c.id = ass.class_id
        JOIN attendance_records ar ON ass.session_id = ar.session_id
        WHERE c.school_id = $1
        AND ass.session_date BETWEEN $2 AND $3
        GROUP BY DATE(ass.session_date)
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

// ============================================================================
// QR CODE ATTENDANCE ROUTES
// ============================================================================

/**
 * @route   POST /api/attendance/qr/generate
 * @desc    Generate QR code for attendance session
 * @access  Private (Teachers, Administrators, Backend Admins, Super Admins)
 */
router.post('/qr/generate', 
  authenticateToken, 
  requireRole(['teacher', 'administrator', 'admin', 'superadmin']), 
  async (req, res) => {
    try {
      const { class_id, session_date, session_time, expiry_minutes = 30 } = req.body;
      const { id: teacherId } = req.user;
      
      // Validate required fields
      if (!class_id || !session_date || !session_time) {
        return res.status(400).json({
          success: false,
          message: 'Missing required fields: class_id, session_date, session_time'
        });
      }
      
      // Verify teacher owns this class
      const classCheck = await query(`
        SELECT id FROM classes WHERE id = $1 AND teacher_id = $2
      `, [class_id, teacherId]);
      
      if (classCheck.rows.length === 0) {
        return res.status(403).json({
          success: false,
          message: 'You do not have permission to access this class'
        });
      }
      
      // Generate unique QR code data
      const qrData = {
        class_id: class_id,
        teacher_id: teacherId,
        session_date: session_date,
        session_time: session_time,
        timestamp: new Date().toISOString(),
        expiry: new Date(Date.now() + expiry_minutes * 60000).toISOString()
      };
      
      // Create QR code session in database
      const qrSession = await query(`
        INSERT INTO qr_attendance_sessions 
        (class_id, teacher_id, session_date, session_time, qr_data, expiry_time, is_active)
        VALUES ($1, $2, $3, $4, $5, $6, true)
        RETURNING *
      `, [
        class_id, 
        teacherId, 
        session_date, 
        session_time, 
        JSON.stringify(qrData),
        qrData.expiry
      ]);
      
      res.status(201).json({
        success: true,
        message: 'QR code generated successfully',
        data: {
          qr_session_id: qrSession.rows[0].id,
          qr_data: qrData,
          expiry_time: qrData.expiry,
          qr_code_url: `${process.env.FRONTEND_URL || 'http://localhost:3000'}/qr-attendance/${qrSession.rows[0].id}`
        }
      });
      
    } catch (error) {
      console.error('Error generating QR code:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to generate QR code',
        error: error.message
      });
    }
  }
);

/**
 * @route   POST /api/attendance/qr/scan
 * @desc    Scan QR code and mark attendance
 * @access  Private (Students, Teachers, Administrators, Backend Admins, Super Admins)
 */
router.post('/qr/scan', 
  authenticateToken, 
  requireRole(['student', 'teacher', 'administrator', 'admin', 'superadmin']), 
  async (req, res) => {
    try {
      const { qr_session_id, student_id } = req.body;
      const { id: userId, role: userRole } = req.user;
      
      // Validate required fields
      if (!qr_session_id) {
        return res.status(400).json({
          success: false,
          message: 'Missing required field: qr_session_id'
        });
      }
      
      // Get QR session details
      const qrSession = await query(`
        SELECT * FROM qr_attendance_sessions 
        WHERE id = $1 AND is_active = true AND expiry_time > NOW()
      `, [qr_session_id]);
      
      if (qrSession.rows.length === 0) {
        return res.status(404).json({
          success: false,
          message: 'QR code session not found or expired'
        });
      }
      
      const session = qrSession.rows[0];
      const qrData = JSON.parse(session.qr_data);
      
      // Determine student ID based on user role
      let targetStudentId = student_id;
      if (userRole === 'student') {
        targetStudentId = userId;
      } else if (!targetStudentId) {
        return res.status(400).json({
          success: false,
          message: 'Student ID required for non-student users'
        });
      }
      
      // Verify student is in the class
      const studentCheck = await query(`
        SELECT cs.student_id FROM class_students cs
        WHERE cs.class_id = $1 AND cs.student_id = $2 AND cs.is_active = true
      `, [qrData.class_id, targetStudentId]);
      
      if (studentCheck.rows.length === 0) {
        return res.status(403).json({
          success: false,
          message: 'Student not found in this class'
        });
      }
      
      // Check if attendance already marked
      const existingAttendance = await query(`
        SELECT ar.record_id FROM attendance_records ar
        JOIN attendance_sessions ass ON ar.session_id = ass.session_id
        WHERE ass.class_id = $1 AND ar.student_id = $2 AND ass.session_date = $3
      `, [qrData.class_id, targetStudentId, qrData.session_date]);
      
      if (existingAttendance.rows.length > 0) {
        return res.status(409).json({
          success: false,
          message: 'Attendance already marked for this student'
        });
      }
      
      // Create or get attendance session
      let attendanceSession = await query(`
        SELECT session_id FROM attendance_sessions 
        WHERE class_id = $1 AND session_date = $2 AND session_time = $3
      `, [qrData.class_id, qrData.session_date, qrData.session_time]);
      
      let sessionId;
      if (attendanceSession.rows.length === 0) {
        // Create new attendance session
        const newSession = await query(`
          INSERT INTO attendance_sessions 
          (class_id, teacher_id, session_date, session_time, session_type)
          VALUES ($1, $2, $3, $4, 'qr_scan')
          RETURNING session_id
        `, [qrData.class_id, qrData.teacher_id, qrData.session_date, qrData.session_time]);
        sessionId = newSession.rows[0].session_id;
      } else {
        sessionId = attendanceSession.rows[0].session_id;
      }
      
      // Mark attendance
      const attendanceRecord = await query(`
        INSERT INTO attendance_records 
        (session_id, student_id, status, marked_by, notes)
        VALUES ($1, $2, 'present', $3, 'QR code scan')
        RETURNING *
      `, [sessionId, targetStudentId, userId]);
      
      res.status(200).json({
        success: true,
        message: 'Attendance marked successfully via QR code',
        data: {
          record_id: attendanceRecord.rows[0].record_id,
          student_id: targetStudentId,
          status: 'present',
          timestamp: new Date().toISOString()
        }
      });
      
    } catch (error) {
      console.error('Error scanning QR code:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to scan QR code',
        error: error.message
      });
    }
  }
);

/**
 * @route   GET /api/attendance/qr/session/:sessionId/status
 * @desc    Get QR session status and attendance summary
 * @access  Private (Teachers, Administrators, Backend Admins, Super Admins)
 */
router.get('/qr/session/:sessionId/status', 
  authenticateToken, 
  requireRole(['teacher', 'administrator', 'admin', 'superadmin']), 
  async (req, res) => {
    try {
      const { sessionId } = req.params;
      const { id: teacherId } = req.user;
      
      // Get QR session details
      const qrSession = await query(`
        SELECT * FROM qr_attendance_sessions 
        WHERE id = $1 AND teacher_id = $2
      `, [sessionId, teacherId]);
      
      if (qrSession.rows.length === 0) {
        return res.status(404).json({
          success: false,
          message: 'QR session not found'
        });
      }
      
      const session = qrSession.rows[0];
      const qrData = JSON.parse(session.qr_data);
      
      // Get attendance summary
      const attendanceSummary = await query(`
        SELECT 
          COUNT(*) as total_marked,
          COUNT(CASE WHEN ar.status = 'present' THEN 1 END) as present_count,
          COUNT(CASE WHEN ar.status = 'absent' THEN 1 END) as absent_count,
          COUNT(CASE WHEN ar.status = 'late' THEN 1 END) as late_count
        FROM attendance_records ar
        JOIN attendance_sessions ass ON ar.session_id = ass.session_id
        WHERE ass.class_id = $1 AND ass.session_date = $2
      `, [qrData.class_id, qrData.session_date]);
      
      // Get total students in class
      const totalStudents = await query(`
        SELECT COUNT(*) as total FROM class_students 
        WHERE class_id = $1 AND is_active = true
      `, [qrData.class_id]);
      
      const summary = attendanceSummary.rows[0];
      const total = totalStudents.rows[0].total;
      
      res.status(200).json({
        success: true,
        data: {
          qr_session: session,
          attendance_summary: {
            total_students: parseInt(total),
            marked_attendance: parseInt(summary.total_marked),
            present: parseInt(summary.present_count),
            absent: parseInt(summary.absent_count),
            late: parseInt(summary.late_count),
            attendance_percentage: total > 0 ? Math.round((summary.total_marked / total) * 100) : 0
          },
          is_active: session.is_active && new Date() < new Date(session.expiry_time),
          time_remaining: Math.max(0, new Date(session.expiry_time) - new Date())
        }
      });
      
    } catch (error) {
      console.error('Error getting QR session status:', error);
      res.status(500).json({
        success: false,
        message: 'Failed to get QR session status',
        error: error.message
      });
    }
  }
);

module.exports = router;
