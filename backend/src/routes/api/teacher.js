const express = require('express');
const { query } = require('../../config/database');
const { authenticateToken, requireRole } = require('../../middleware/auth');
const router = express.Router();

// GET /api/teacher/dashboard
router.get('/dashboard', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId, tenantId } = req.user;
    
    // Get teacher's classes and stats
    const statsQuery = `
      SELECT 
        (SELECT COUNT(*) FROM students s 
         JOIN classes c ON s.class_id = c.id 
         WHERE c.teacher_id = $1) as total_students,
        (SELECT COUNT(*) FROM classes WHERE teacher_id = $1 AND is_active = true) as total_classes,
        (SELECT COUNT(*) FROM teacher_tasks WHERE teacher_id = $1 AND status = 'pending') as pending_tasks,
        (SELECT COUNT(*) FROM student_grades WHERE teacher_id = $1 AND created_at >= NOW() - INTERVAL '7 days') as recent_grades
    `;
    
    const statsResult = await query(statsQuery, [teacherId]);
    const stats = statsResult.rows[0];
    
    // Get recent activities
    const activitiesQuery = `
      SELECT 
        'attendance' as type,
        '📊' as icon,
        'Attendance marked' as title,
        'Marked attendance for Class 10A' as description,
        NOW() - INTERVAL '2 hours' as time
      UNION ALL
      SELECT 
        'task' as type,
        '📝' as icon,
        'Task completed' as title,
        'Completed grade assignment for Math' as description,
        NOW() - INTERVAL '4 hours' as time
      ORDER BY time DESC
      LIMIT 5
    `;
    
    const activitiesResult = await query(activitiesQuery);
    
    res.json({
      success: true,
      data: {
        stats,
        recentActivities: activitiesResult.rows
      }
    });
  } catch (error) {
    console.error('Teacher dashboard error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// GET /api/teacher/classes
router.get('/classes', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    
    const classesQuery = `
      SELECT 
        c.id,
        c.name,
        c.grade_level,
        c.academic_year,
        COUNT(s.id) as student_count
      FROM classes c
      LEFT JOIN students s ON c.id = s.class_id
      WHERE c.teacher_id = $1 AND c.is_active = true
      GROUP BY c.id, c.name, c.grade_level, c.academic_year
      ORDER BY c.name
    `;
    
    const classesResult = await query(classesQuery, [teacherId]);
    
    res.json({
      success: true,
      data: {
        classes: classesResult.rows
      }
    });
  } catch (error) {
    console.error('Teacher classes error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// GET /api/teacher/classes/:classId/students
router.get('/classes/:classId/students', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { classId } = req.params;
    const { id: teacherId } = req.user;
    
    const studentsQuery = `
      SELECT 
        s.id,
        u.first_name,
        u.last_name,
        s.student_id as student_code
      FROM students s
      JOIN users u ON s.user_id = u.id
      WHERE s.class_id = $1 AND s.is_active = true
      ORDER BY u.first_name, u.last_name
    `;
    
    const studentsResult = await query(studentsQuery, [classId]);
    
    res.json({
      success: true,
      data: {
        students: studentsResult.rows
      }
    });
  } catch (error) {
    console.error('Students fetch error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// POST /api/teacher/attendance/qr-genera
router.post('/attendance/qr-generate', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { classId, duration = 300 } = req.body;
    const { id: teacherId } = req.user;
    
    // Generate session ID
    const sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // Create attendance session
    await query(`
      INSERT INTO attendance_sessions (id, class_id, teacher_id, expires_at)
      VALUES ($1, $2, $3, NOW() + INTERVAL '${duration} seconds')
    `, [sessionId, classId, teacherId]);
    
    // Generate QR code data
    const qrData = JSON.stringify({
      sessionId,
      classId,
      timestamp: Date.now(),
      expiresAt: Date.now() + (duration * 1000)
    });
    
    res.json({
      success: true,
      data: {
        sessionId,
        qrCode: qrData,
        expiresAt: new Date(Date.now() + (duration * 1000))
      }
    });
  } catch (error) {
    console.error('QR generation error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// GET /api/teacher/attendance/session/:sessionId
router.get('/attendance/session/:sessionId', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { sessionId } = req.params;
    
    // Get session data
    const sessionQuery = `
      SELECT 
        s.id,
        s.class_id,
        s.teacher_id,
        s.expires_at,
        s.is_active,
        c.name as class_name
      FROM attendance_sessions s
      JOIN classes c ON s.class_id = c.id
      WHERE s.id = $1
    `;
    
    const sessionResult = await query(sessionQuery, [sessionId]);
    
    if (sessionResult.rows.length === 0) {
      return res.status(404).json({ success: false, message: 'Session not found' });
    }
    
    const session = sessionResult.rows[0];
    
    // Get attendance records for this session
    const attendanceQuery = `
      SELECT 
        ar.id,
        ar.student_id,
        ar.status,
        ar.timestamp,
        s.first_name,
        s.last_name,
        s.student_id as student_code
      FROM attendance_records ar
      JOIN students st ON ar.student_id = st.id
      JOIN users s ON st.user_id = s.id
      WHERE ar.session_id = $1
      ORDER BY ar.timestamp DESC
    `;
    
    const attendanceResult = await query(attendanceQuery, [sessionId]);
    
    // Calculate stats
    const stats = {
      totalStudents: attendanceResult.rows.length,
      present: attendanceResult.rows.filter(r => r.status === 'present').length,
      absent: attendanceResult.rows.filter(r => r.status === 'absent').length,
      late: attendanceResult.rows.filter(r => r.status === 'late').length
    };
    
    res.json({
      success: true,
      data: {
        session,
        attendance: attendanceResult.rows,
        stats,
        scanResults: attendanceResult.rows.filter(r => r.status === 'present')
      }
    });
  } catch (error) {
    console.error('Session data error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// POST /api/teacher/attendance/manual
router.post('/attendance/manual', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { classId, studentId, status, date } = req.body;
    const { id: teacherId } = req.user;
    
    // Check if attendance already exists for this student on this date
    const existingQuery = `
      SELECT id FROM attendance_records 
      WHERE class_id = $1 AND student_id = $2 AND DATE(timestamp) = $3
    `;
    
    const existingResult = await query(existingQuery, [classId, studentId, date]);
    
    if (existingResult.rows.length > 0) {
      // Update existing record
      await query(`
        UPDATE attendance_records 
        SET status = $1, updated_at = NOW() 
        WHERE id = $2
      `, [status, existingResult.rows[0].id]);
    } else {
      // Create new record
      await query(`
        INSERT INTO attendance_records (class_id, student_id, status, timestamp)
        VALUES ($1, $2, $3, $4)
      `, [classId, studentId, status, date]);
    }
    
    res.json({ success: true, message: 'Attendance marked successfully' });
  } catch (error) {
    console.error('Manual attendance error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// GET /api/teacher/attendance/:classId
router.get('/attendance/:classId', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { classId } = req.params;
    const { id: teacherId } = req.user;
    const { date = new Date().toISOString().split('T')[0] } = req.query;
    
    // Get students and their attendance for the specified date
    const attendanceQuery = `
      SELECT 
        s.id as student_id,
        u.first_name,
        u.last_name,
        s.student_id as student_code,
        COALESCE(ar.status, 'absent') as attendance_status,
        ar.timestamp as attendance_time
      FROM students s
      JOIN users u ON s.user_id = u.id
      LEFT JOIN attendance_records ar ON s.id = ar.student_id 
        AND ar.class_id = $1 
        AND DATE(ar.timestamp) = $2
      WHERE s.class_id = $1 AND s.is_active = true
      ORDER BY u.first_name, u.last_name
    `;
    
    const attendanceResult = await query(attendanceQuery, [classId, date]);
    
    // Calculate stats
    const stats = {
      total: attendanceResult.rows.length,
      present: attendanceResult.rows.filter(r => r.attendance_status === 'present').length,
      absent: attendanceResult.rows.filter(r => r.attendance_status === 'absent').length,
      late: attendanceResult.rows.filter(r => r.attendance_status === 'late').length,
      excused: attendanceResult.rows.filter(r => r.attendance_status === 'excused').length
    };
    
    res.json({
      success: true,
      data: {
        attendance: attendanceResult.rows,
        stats,
        date
      }
    });
  } catch (error) {
    console.error('Attendance fetch error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// GET /api/teacher/attendance/report/:classId
router.get('/attendance/report/:classId', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { classId } = req.params;
    const { startDate, endDate } = req.query;
    
    const reportQuery = `
      SELECT 
        u.first_name,
        u.last_name,
        s.student_id as student_code,
        COUNT(CASE WHEN ar.status = 'present' THEN 1 END) as present_days,
        COUNT(CASE WHEN ar.status = 'absent' THEN 1 END) as absent_days,
        COUNT(CASE WHEN ar.status = 'late' THEN 1 END) as late_days,
        COUNT(CASE WHEN ar.status = 'excused' THEN 1 END) as excused_days
      FROM attendance_records ar
      JOIN students st ON ar.student_id = st.id
      JOIN users u ON st.user_id = u.id
      WHERE ar.class_id = $1
      AND DATE(ar.timestamp) BETWEEN $2 AND $3
      GROUP BY u.first_name, u.last_name, s.student_id
      ORDER BY u.first_name, u.last_name
    `;
    
    const reportResult = await query(reportQuery, [classId, startDate, endDate]);
    
    // Generate CSV
    const csvHeader = 'Student Name,Student Code,Present Days,Absent Days,Late Days,Excused Days\n';
    const csvData = reportResult.rows.map(row => 
      `${row.first_name} ${row.last_name},${row.student_code},${row.present_days},${row.absent_days},${row.late_days},${row.excused_days}`
    ).join('\n');
    
    const csvContent = csvHeader + csvData;
    
    res.json({
      success: true,
      data: {
        report: csvContent
      }
    });
  } catch (error) {
    console.error('Report generation error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// Task Management APIs
router.get('/tasks', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    
    const tasksQuery = `
      SELECT 
        id,
        title,
        description,
        priority,
        status,
        due_date,
        tags,
        created_at,
        updated_at
      FROM teacher_tasks
      WHERE teacher_id = $1
      ORDER BY created_at DESC
    `;
    
    const tasksResult = await query(tasksQuery, [teacherId]);
    
    res.json({
      success: true,
      data: {
        tasks: tasksResult.rows
      }
    });
  } catch (error) {
    console.error('Tasks fetch error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

router.post('/tasks', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    const { title, description, priority, dueDate, tags } = req.body;
    
    const insertQuery = `
      INSERT INTO teacher_tasks (teacher_id, title, description, priority, due_date, tags, status)
      VALUES ($1, $2, $3, $4, $5, $6, 'pending')
      RETURNING id
    `;
    
    const result = await query(insertQuery, [teacherId, title, description, priority, dueDate, tags, 'pending']);
    
    res.json({
      success: true,
      data: {
        taskId: result.rows[0].id
      }
    });
  } catch (error) {
    console.error('Task creation error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

router.patch('/tasks/:taskId', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { taskId } = req.params;
    const { id: teacherId } = req.user;
    const { status, title, description, priority, dueDate, category } = req.body;
    
    const result = await query(`
      UPDATE teacher_tasks 
      SET status = COALESCE($1, status),
          title = COALESCE($2, title),
          description = COALESCE($3, description),
          priority = COALESCE($4, priority),
          due_date = COALESCE($5, due_date),
          category = COALESCE($6, category),
          updated_at = NOW()
      WHERE id = $7 AND teacher_id = $8
      RETURNING *
    `, [status, title, description, priority, dueDate, category, taskId, teacherId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ success: false, message: 'Task not found' });
    }
    
    res.json({
      success: true,
      data: {
        task: result.rows[0]
      }
    });
  } catch (error) {
    console.error('Task update error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

router.delete('/tasks/:taskId', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { taskId } = req.params;
    const { id: teacherId } = req.user;
    
    const result = await query(`
      DELETE FROM teacher_tasks 
      WHERE id = $1 AND teacher_id = $2
      RETURNING id
    `, [taskId, teacherId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ success: false, message: 'Task not found' });
    }
    
    res.json({ success: true, message: 'Task deleted successfully' });
  } catch (error) {
    console.error('Task deletion error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// Resource Booking APIs
router.post('/resources/book', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    const { resourceId, classId, bookingDate, startTime, endTime, purpose } = req.body;
    
    const result = await query(`
      INSERT INTO resource_bookings (resource_id, teacher_id, class_id, booking_date, start_time, end_time, purpose)
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING *
    `, [resourceId, teacherId, classId, bookingDate, startTime, endTime, purpose]);
    
    res.json({
      success: true,
      data: {
        booking: result.rows[0]
      }
    });
  } catch (error) {
    console.error('Resource booking error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

router.delete('/resources/bookings/:bookingId', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { bookingId } = req.params;
    const { id: teacherId } = req.user;
    
    const result = await query(`
      DELETE FROM resource_bookings 
      WHERE id = $1 AND teacher_id = $2
      RETURNING id
    `, [bookingId, teacherId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({ success: false, message: 'Booking not found' });
    }
    
    res.json({ success: true, message: 'Booking cancelled successfully' });
  } catch (error) {
    console.error('Booking cancellation error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// Grade Management APIs
router.get('/assignments/:assignmentId/grades', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { assignmentId } = req.params;
    const { id: teacherId } = req.user;
    
    const gradesQuery = `
      SELECT 
        sg.*,
        s.first_name,
        s.last_name,
        s.student_id as student_code
      FROM student_grades sg
      JOIN students st ON sg.student_id = st.id
      JOIN users s ON st.user_id = s.id
      WHERE sg.assignment_id = $1 AND sg.teacher_id = $2
      ORDER BY s.first_name, s.last_name
    `;
    
    const gradesResult = await query(gradesQuery, [assignmentId, teacherId]);
    
    res.json({
      success: true,
      data: {
        grades: gradesResult.rows
      }
    });
  } catch (error) {
    console.error('Grades fetch error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

router.post('/assignments/:assignmentId/grades', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { assignmentId } = req.params;
    const { id: teacherId } = req.user;
    const { studentId, grade, pointsEarned, feedback } = req.body;
    
    // Check if grade already exists
    const existingGrade = await query(`
      SELECT id FROM student_grades 
      WHERE assignment_id = $1 AND student_id = $2
    `, [assignmentId, studentId]);
    
    if (existingGrade.rows.length > 0) {
      // Update existing grade
      const result = await query(`
        UPDATE student_grades 
        SET grade = $1, points_earned = $2, feedback = $3, updated_at = NOW()
        WHERE assignment_id = $4 AND student_id = $5
        RETURNING *
      `, [grade, pointsEarned, feedback, assignmentId, studentId]);
      
      res.json({
        success: true,
        data: {
          grade: result.rows[0]
        }
      });
    } else {
      // Create new grade
      const result = await query(`
        INSERT INTO student_grades (assignment_id, student_id, teacher_id, grade, points_earned, feedback)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING *
      `, [assignmentId, studentId, teacherId, grade, pointsEarned, feedback]);
      
      res.json({
        success: true,
        data: {
          grade: result.rows[0]
        }
      });
    }
  } catch (error) {
    console.error('Grade submission error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// Timetable Management APIs
router.get('/timetable', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    
    const timetableQuery = `
      SELECT 
        cs.*,
        c.name as class_name,
        c.grade_level
      FROM class_schedules cs
      JOIN classes c ON cs.class_id = c.id
      WHERE cs.teacher_id = $1 AND cs.is_active = true
      ORDER BY cs.day_of_week, cs.start_time
    `;
    
    const timetableResult = await query(timetableQuery, [teacherId]);
    
    res.json({
      success: true,
      data: {
        timetable: timetableResult.rows
      }
    });
  } catch (error) {
    console.error('Timetable fetch error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

router.post('/timetable', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    const { classId, dayOfWeek, startTime, endTime, roomNumber, subject } = req.body;
    
    const result = await query(`
      INSERT INTO class_schedules (class_id, teacher_id, day_of_week, start_time, end_time, room_number, subject)
      VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING *
    `, [classId, teacherId, dayOfWeek, startTime, endTime, roomNumber, subject]);
    
    res.json({
      success: true,
      data: {
        schedule: result.rows[0]
      }
    });
  } catch (error) {
    console.error('Schedule creation error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// AI Report Generation APIs
router.get('/reports/templates', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const templatesQuery = `
      SELECT * FROM report_templates 
      WHERE is_active = true
      ORDER BY name
    `;
    
    const templatesResult = await query(templatesQuery);
    
    res.json({
      success: true,
      data: {
        templates: templatesResult.rows
      }
    });
  } catch (error) {
    console.error('Templates fetch error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

router.post('/reports/generate', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    const { templateId, classId, dateRange, parameters } = req.body;
    
    // This would integrate with ML services for report generation
    // For now, return a placeholder response
    
    res.json({
      success: true,
      data: {
        report: {
          id: `report_${Date.now()}`,
          title: 'Generated Report',
          content: 'Report content would be generated by ML services',
          generatedAt: new Date().toISOString(),
          parameters
        }
      }
    });
  } catch (error) {
    console.error('Report generation error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// Substitute Teacher Management APIs
router.get('/substitutes', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    
    const substitutesQuery = `
      SELECT 
        sr.*,
        c.name as class_name,
        u.first_name as substitute_first_name,
        u.last_name as substitute_last_name
      FROM substitute_requests sr
      JOIN classes c ON sr.class_id = c.id
      LEFT JOIN users u ON sr.substitute_id = u.id
      WHERE sr.teacher_id = $1
      ORDER BY sr.request_date DESC
    `;
    
    const substitutesResult = await query(substitutesQuery, [teacherId]);
    
    res.json({
      success: true,
      data: {
        substitutes: substitutesResult.rows
      }
    });
  } catch (error) {
    console.error('Substitutes fetch error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

router.post('/substitutes', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    const { classId, requestDate, startTime, endTime, reason } = req.body;
    
    const result = await query(`
      INSERT INTO substitute_requests (teacher_id, class_id, request_date, start_time, end_time, reason)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING *
    `, [teacherId, classId, requestDate, startTime, endTime, reason]);
    
    res.json({
      success: true,
      data: {
        substitute: result.rows[0]
      }
    });
  } catch (error) {
    console.error('Substitute request error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

module.exports = router; 