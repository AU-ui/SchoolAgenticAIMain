const express = require('express');
const router = express.Router();
const { authenticateToken, requireRole } = require('../../middleware/auth');
const { query } = require('../../config/database');

// GET /api/student/dashboard - Get student dashboard data
router.get('/dashboard', authenticateToken, requireRole(['student']), async (req, res) => {
  try {
    const userId = req.user.id;
    const tenantId = req.user.tenant_id;

    // Get student information
    const studentQuery = `
      SELECT s.id, s.student_id as student_code, s.class_id, s.section,
             c.name as class_name, c.section as class_section,
             u.first_name, u.last_name, u.email, u.profile_image
      FROM students s
      JOIN users u ON s.user_id = u.id
      LEFT JOIN classes c ON s.class_id = c.id
      WHERE s.user_id = $1 AND u.tenant_id = $2
    `;
    const studentResult = await query(studentQuery, [userId, tenantId]);

    if (studentResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Student not found'
      });
    }

    const student = studentResult.rows[0];

    // Get recent assignments
    const assignmentsQuery = `
      SELECT a.id, a.title, a.description, a.due_date, a.points,
             sg.grade, sg.points_earned, sg.feedback,
             t.first_name || ' ' || t.last_name as teacher_name
      FROM assignments a
      LEFT JOIN student_grades sg ON a.id = sg.assignment_id AND sg.student_id = $1
      LEFT JOIN users t ON a.teacher_id = t.id
      WHERE a.class_id = $2
      ORDER BY a.due_date DESC
      LIMIT 5
    `;
    const assignmentsResult = await query(assignmentsQuery, [student.id, student.class_id]);

    // Get attendance summary
    const attendanceQuery = `
      SELECT 
        COUNT(*) as total_days,
        COUNT(CASE WHEN status = 'present' THEN 1 END) as present_days,
        COUNT(CASE WHEN status = 'absent' THEN 1 END) as absent_days,
        COUNT(CASE WHEN status = 'late' THEN 1 END) as late_days
      FROM attendance_records
      WHERE student_id = $1 AND timestamp >= NOW() - INTERVAL '30 days'
    `;
    const attendanceResult = await query(attendanceQuery, [student.id]);

    // Get recent grades
    const gradesQuery = `
      SELECT sg.grade, sg.points_earned, sg.feedback, sg.created_at,
             a.title as assignment_title, a.points as total_points
      FROM student_grades sg
      JOIN assignments a ON sg.assignment_id = a.id
      WHERE sg.student_id = $1
      ORDER BY sg.created_at DESC
      LIMIT 10
    `;
    const gradesResult = await query(gradesQuery, [student.id]);

    res.json({
      success: true,
      data: {
        student,
        assignments: assignmentsResult.rows,
        attendance: attendanceResult.rows[0],
        recentGrades: gradesResult.rows
      }
    });
  } catch (error) {
    console.error('Student dashboard error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load student dashboard'
    });
  }
});

// GET /api/student/classes - Get student's classes
router.get('/classes', authenticateToken, requireRole(['student']), async (req, res) => {
  try {
    const userId = req.user.id;
    const tenantId = req.user.tenant_id;

    const classesQuery = `
      SELECT c.id, c.name, c.section, c.schedule,
             t.first_name || ' ' || t.last_name as teacher_name,
             t.email as teacher_email
      FROM classes c
      JOIN students s ON c.id = s.class_id
      JOIN users t ON c.teacher_id = t.id
      WHERE s.user_id = $1 AND c.tenant_id = $2
    `;
    const classesResult = await query(classesQuery, [userId, tenantId]);

    res.json({
      success: true,
      data: classesResult.rows
    });
  } catch (error) {
    console.error('Student classes error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load student classes'
    });
  }
});

// GET /api/student/assignments - Get student's assignments
router.get('/assignments', authenticateToken, requireRole(['student']), async (req, res) => {
  try {
    const userId = req.user.id;
    const tenantId = req.user.tenant_id;

    const assignmentsQuery = `
      SELECT a.id, a.title, a.description, a.due_date, a.points, a.created_at,
             sg.grade, sg.points_earned, sg.feedback, sg.submitted_at,
             t.first_name || ' ' || t.last_name as teacher_name,
             c.name as class_name
      FROM assignments a
      JOIN classes c ON a.class_id = c.id
      JOIN students s ON c.id = s.class_id
      LEFT JOIN student_grades sg ON a.id = sg.assignment_id AND sg.student_id = s.id
      LEFT JOIN users t ON a.teacher_id = t.id
      WHERE s.user_id = $1 AND a.tenant_id = $2
      ORDER BY a.due_date DESC
    `;
    const assignmentsResult = await query(assignmentsQuery, [userId, tenantId]);

    res.json({
      success: true,
      data: assignmentsResult.rows
    });
  } catch (error) {
    console.error('Student assignments error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load student assignments'
    });
  }
});

// GET /api/student/grades - Get student's grades
router.get('/grades', authenticateToken, requireRole(['student']), async (req, res) => {
  try {
    const userId = req.user.id;
    const tenantId = req.user.tenant_id;

    const gradesQuery = `
      SELECT sg.grade, sg.points_earned, sg.feedback, sg.created_at,
             a.title as assignment_title, a.points as total_points,
             c.name as class_name,
             t.first_name || ' ' || t.last_name as teacher_name
      FROM student_grades sg
      JOIN assignments a ON sg.assignment_id = a.id
      JOIN classes c ON a.class_id = c.id
      JOIN students s ON sg.student_id = s.id
      LEFT JOIN users t ON sg.teacher_id = t.id
      WHERE s.user_id = $1 AND sg.tenant_id = $2
      ORDER BY sg.created_at DESC
    `;
    const gradesResult = await query(gradesQuery, [userId, tenantId]);

    res.json({
      success: true,
      data: gradesResult.rows
    });
  } catch (error) {
    console.error('Student grades error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load student grades'
    });
  }
});

// GET /api/student/schedule - Get student's schedule
router.get('/schedule', authenticateToken, requireRole(['student']), async (req, res) => {
  try {
    const userId = req.user.id;
    const tenantId = req.user.tenant_id;

    const scheduleQuery = `
      SELECT c.name as class_name, c.section, c.schedule,
             t.first_name || ' ' || t.last_name as teacher_name,
             c.room_number, c.subject
      FROM classes c
      JOIN students s ON c.id = s.class_id
      LEFT JOIN users t ON c.teacher_id = t.id
      WHERE s.user_id = $1 AND c.tenant_id = $2
      ORDER BY c.schedule
    `;
    const scheduleResult = await query(scheduleQuery, [userId, tenantId]);

    res.json({
      success: true,
      data: scheduleResult.rows
    });
  } catch (error) {
    console.error('Student schedule error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load student schedule'
    });
  }
});

// GET /api/student/attendance - Get student's attendance
router.get('/attendance', authenticateToken, requireRole(['student']), async (req, res) => {
  try {
    const userId = req.user.id;
    const tenantId = req.user.tenant_id;
    const { start_date, end_date } = req.query;

    let dateFilter = '';
    let queryParams = [userId, tenantId];

    if (start_date && end_date) {
      dateFilter = 'AND ar.timestamp BETWEEN $3 AND $4';
      queryParams.push(start_date, end_date);
    }

    const attendanceQuery = `
      SELECT ar.timestamp, ar.status, ar.notes,
             c.name as class_name,
             t.first_name || ' ' || t.last_name as teacher_name
      FROM attendance_records ar
      JOIN classes c ON ar.class_id = c.id
      JOIN students s ON ar.student_id = s.id
      LEFT JOIN users t ON c.teacher_id = t.id
      WHERE s.user_id = $1 AND ar.tenant_id = $2 ${dateFilter}
      ORDER BY ar.timestamp DESC
    `;
    const attendanceResult = await query(attendanceQuery, queryParams);

    res.json({
      success: true,
      data: attendanceResult.rows
    });
  } catch (error) {
    console.error('Student attendance error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load student attendance'
    });
  }
});

// GET /api/student/resources - Get student's resources
router.get('/resources', authenticateToken, requireRole(['student']), async (req, res) => {
  try {
    const userId = req.user.id;
    const tenantId = req.user.tenant_id;

    const resourcesQuery = `
      SELECT r.id, r.title, r.description, r.file_url, r.file_type, r.created_at,
             t.first_name || ' ' || t.last_name as teacher_name,
             c.name as class_name
      FROM resources r
      JOIN classes c ON r.class_id = c.id
      JOIN students s ON c.id = s.class_id
      LEFT JOIN users t ON r.teacher_id = t.id
      WHERE s.user_id = $1 AND r.tenant_id = $2 AND r.shared_with_students = true
      ORDER BY r.created_at DESC
    `;
    const resourcesResult = await query(resourcesQuery, [userId, tenantId]);

    res.json({
      success: true,
      data: resourcesResult.rows
    });
  } catch (error) {
    console.error('Student resources error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load student resources'
    });
  }
});

// GET /api/student/communication - Get student's communications
router.get('/communication', authenticateToken, requireRole(['student']), async (req, res) => {
  try {
    const userId = req.user.id;
    const tenantId = req.user.tenant_id;

    const communicationQuery = `
      SELECT m.id, m.subject, m.message, m.created_at, m.is_read,
             s.first_name || ' ' || s.last_name as sender_name,
             s.email as sender_email
      FROM messages m
      JOIN users s ON m.sender_id = s.id
      WHERE m.recipient_id = $1 AND m.tenant_id = $2
      ORDER BY m.created_at DESC
      LIMIT 20
    `;
    const communicationResult = await query(communicationQuery, [userId, tenantId]);

    res.json({
      success: true,
      data: communicationResult.rows
    });
  } catch (error) {
    console.error('Student communication error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load student communications'
    });
  }
});

// POST /api/student/assignments/:assignmentId/submit - Submit assignment
router.post('/assignments/:assignmentId/submit', authenticateToken, requireRole(['student']), async (req, res) => {
  try {
    const { assignmentId } = req.params;
    const userId = req.user.id;
    const { submission_text, file_url } = req.body;

    // Verify student has access to this assignment
    const assignmentQuery = `
      SELECT a.id, a.title, a.due_date
      FROM assignments a
      JOIN classes c ON a.class_id = c.id
      JOIN students s ON c.id = s.class_id
      WHERE a.id = $1 AND s.user_id = $2
    `;
    const assignmentResult = await query(assignmentQuery, [assignmentId, userId]);

    if (assignmentResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Assignment not found or access denied'
      });
    }

    // Insert submission
    const submissionQuery = `
      INSERT INTO assignment_submissions (assignment_id, student_id, submission_text, file_url, submitted_at)
      VALUES ($1, $2, $3, $4, NOW())
      ON CONFLICT (assignment_id, student_id) 
      DO UPDATE SET submission_text = $3, file_url = $4, submitted_at = NOW()
    `;
    await query(submissionQuery, [assignmentId, userId, submission_text, file_url]);

    res.json({
      success: true,
      message: 'Assignment submitted successfully'
    });
  } catch (error) {
    console.error('Assignment submission error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to submit assignment'
    });
  }
});

module.exports = router; 