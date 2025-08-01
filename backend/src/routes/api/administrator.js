const express = require('express');
const router = express.Router();
const { authenticateToken, requireRole } = require('../../middleware/auth');
const { query } = require('../../config/database');

// GET /api/administrator/dashboard - Get administrator dashboard data
router.get('/dashboard', authenticateToken, requireRole(['administrator']), async (req, res) => {
  try {
    const userId = req.user.id;
    const tenantId = req.user.tenant_id;

    // Get school statistics
    const statsQuery = `
      SELECT 
        (SELECT COUNT(*) FROM users WHERE tenant_id = $1 AND role = 'teacher') as total_teachers,
        (SELECT COUNT(*) FROM users WHERE tenant_id = $1 AND role = 'student') as total_students,
        (SELECT COUNT(*) FROM users WHERE tenant_id = $1 AND role = 'parent') as total_parents,
        (SELECT COUNT(*) FROM classes WHERE tenant_id = $1) as total_classes,
        (SELECT COUNT(*) FROM users WHERE tenant_id = $1 AND status = 'pending') as pending_users
    `;
    const statsResult = await query(statsQuery, [tenantId]);

    // Get recent activities
    const activitiesQuery = `
      SELECT 'user_registration' as type, u.first_name, u.last_name, u.email, u.created_at,
             u.role, u.status
      FROM users u
      WHERE u.tenant_id = $1 AND u.created_at >= NOW() - INTERVAL '7 days'
      UNION ALL
      SELECT 'attendance_record' as type, u.first_name, u.last_name, c.name as class_name, ar.timestamp,
             'student' as role, ar.status
      FROM attendance_records ar
      JOIN students s ON ar.student_id = s.id
      JOIN users u ON s.user_id = u.id
      JOIN classes c ON ar.class_id = c.id
      WHERE ar.tenant_id = $1 AND ar.timestamp >= NOW() - INTERVAL '7 days'
      ORDER BY created_at DESC, timestamp DESC
      LIMIT 10
    `;
    const activitiesResult = await query(activitiesQuery, [tenantId]);

    // Get pending approvals
    const pendingQuery = `
      SELECT u.id, u.first_name, u.last_name, u.email, u.role, u.created_at,
             u.school_code, u.phone
      FROM users u
      WHERE u.tenant_id = $1 AND u.status = 'pending'
      ORDER BY u.created_at DESC
    `;
    const pendingResult = await query(pendingQuery, [tenantId]);

    res.json({
      success: true,
      data: {
        statistics: statsResult.rows[0],
        recentActivities: activitiesResult.rows,
        pendingApprovals: pendingResult.rows
      }
    });
  } catch (error) {
    console.error('Administrator dashboard error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load administrator dashboard'
    });
  }
});

// GET /api/administrator/users - Get all users in the school
router.get('/users', authenticateToken, requireRole(['administrator']), async (req, res) => {
  try {
    const tenantId = req.user.tenant_id;
    const { role, status, search } = req.query;

    let whereClause = 'WHERE u.tenant_id = $1';
    let queryParams = [tenantId];
    let paramIndex = 2;

    if (role) {
      whereClause += ` AND u.role = $${paramIndex}`;
      queryParams.push(role);
      paramIndex++;
    }

    if (status) {
      whereClause += ` AND u.status = $${paramIndex}`;
      queryParams.push(status);
      paramIndex++;
    }

    if (search) {
      whereClause += ` AND (u.first_name ILIKE $${paramIndex} OR u.last_name ILIKE $${paramIndex} OR u.email ILIKE $${paramIndex})`;
      const searchTerm = `%${search}%`;
      queryParams.push(searchTerm, searchTerm, searchTerm);
    }

    const usersQuery = `
      SELECT u.id, u.first_name, u.last_name, u.email, u.role, u.status, u.created_at,
             u.phone, u.school_code, u.profile_image,
             CASE 
               WHEN u.role = 'teacher' THEN (SELECT COUNT(*) FROM classes WHERE teacher_id = u.id)
               WHEN u.role = 'student' THEN (SELECT COUNT(*) FROM students WHERE user_id = u.id)
               ELSE 0
             END as related_count
      FROM users u
      ${whereClause}
      ORDER BY u.created_at DESC
    `;
    const usersResult = await query(usersQuery, queryParams);

    res.json({
      success: true,
      data: usersResult.rows
    });
  } catch (error) {
    console.error('Administrator users error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load users'
    });
  }
});

// GET /api/administrator/classes - Get all classes in the school
router.get('/classes', authenticateToken, requireRole(['administrator']), async (req, res) => {
  try {
    const tenantId = req.user.tenant_id;

    const classesQuery = `
      SELECT c.id, c.name, c.section, c.schedule, c.room_number, c.subject,
             t.first_name || ' ' || t.last_name as teacher_name,
             t.email as teacher_email,
             COUNT(s.id) as student_count
      FROM classes c
      LEFT JOIN users t ON c.teacher_id = t.id
      LEFT JOIN students s ON c.id = s.class_id
      WHERE c.tenant_id = $1
      GROUP BY c.id, c.name, c.section, c.schedule, c.room_number, c.subject,
               t.first_name, t.last_name, t.email
      ORDER BY c.name, c.section
    `;
    const classesResult = await query(classesQuery, [tenantId]);

    res.json({
      success: true,
      data: classesResult.rows
    });
  } catch (error) {
    console.error('Administrator classes error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load classes'
    });
  }
});

// GET /api/administrator/attendance - Get attendance overview
router.get('/attendance', authenticateToken, requireRole(['administrator']), async (req, res) => {
  try {
    const tenantId = req.user.tenant_id;
    const { class_id, date } = req.query;

    let whereClause = 'WHERE ar.tenant_id = $1';
    let queryParams = [tenantId];
    let paramIndex = 2;

    if (class_id) {
      whereClause += ` AND ar.class_id = $${paramIndex}`;
      queryParams.push(class_id);
      paramIndex++;
    }

    if (date) {
      whereClause += ` AND DATE(ar.timestamp) = $${paramIndex}`;
      queryParams.push(date);
      paramIndex++;
    }

    const attendanceQuery = `
      SELECT ar.timestamp, ar.status, ar.notes,
             c.name as class_name, c.section,
             s.first_name || ' ' || s.last_name as student_name,
             t.first_name || ' ' || t.last_name as teacher_name
      FROM attendance_records ar
      JOIN classes c ON ar.class_id = c.id
      JOIN students st ON ar.student_id = st.id
      JOIN users s ON st.user_id = s.id
      LEFT JOIN users t ON c.teacher_id = t.id
      ${whereClause}
      ORDER BY ar.timestamp DESC
      LIMIT 100
    `;
    const attendanceResult = await query(attendanceQuery, queryParams);

    res.json({
      success: true,
      data: attendanceResult.rows
    });
  } catch (error) {
    console.error('Administrator attendance error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to load attendance data'
    });
  }
});

// GET /api/administrator/reports - Get school reports
router.get('/reports', authenticateToken, requireRole(['administrator']), async (req, res) => {
  try {
    const tenantId = req.user.tenant_id;
    const { report_type, start_date, end_date } = req.query;

    let reportData = {};

    if (report_type === 'attendance') {
      const attendanceReportQuery = `
        SELECT 
          c.name as class_name,
          COUNT(ar.id) as total_records,
          COUNT(CASE WHEN ar.status = 'present' THEN 1 END) as present_count,
          COUNT(CASE WHEN ar.status = 'absent' THEN 1 END) as absent_count,
          COUNT(CASE WHEN ar.status = 'late' THEN 1 END) as late_count,
          ROUND(
            (COUNT(CASE WHEN ar.status = 'present' THEN 1 END) * 100.0 / COUNT(ar.id)
          ), 2) as attendance_percentage
        FROM classes c
        LEFT JOIN attendance_records ar ON c.id = ar.class_id
        WHERE c.tenant_id = $1
        ${start_date && end_date ? 'AND ar.timestamp BETWEEN $2 AND $3' : ''}
        GROUP BY c.id, c.name
        ORDER BY attendance_percentage DESC
      `;
      
      const queryParams = [tenantId];
      if (start_date && end_date) {
        queryParams.push(start_date, end_date);
      }
      
      const attendanceResult = await query(attendanceReportQuery, queryParams);
      reportData.attendance = attendanceResult.rows;
    }

    if (report_type === 'academic') {
      const academicReportQuery = `
        SELECT 
          c.name as class_name,
          COUNT(DISTINCT sg.student_id) as students_with_grades,
          AVG(sg.grade) as average_grade,
          COUNT(sg.id) as total_assignments_graded
        FROM classes c
        LEFT JOIN students s ON c.id = s.class_id
        LEFT JOIN student_grades sg ON s.id = sg.student_id
        WHERE c.tenant_id = $1
        ${start_date && end_date ? 'AND sg.created_at BETWEEN $2 AND $3' : ''}
        GROUP BY c.id, c.name
        ORDER BY average_grade DESC
      `;
      
      const queryParams = [tenantId];
      if (start_date && end_date) {
        queryParams.push(start_date, end_date);
      }
      
      const academicResult = await query(academicReportQuery, queryParams);
      reportData.academic = academicResult.rows;
    }

    res.json({
      success: true,
      data: reportData
    });
  } catch (error) {
    console.error('Administrator reports error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to generate reports'
    });
  }
});

// POST /api/administrator/users/:userId/approve - Approve user
router.post('/users/:userId/approve', authenticateToken, requireRole(['administrator']), async (req, res) => {
  try {
    const { userId } = req.params;
    const tenantId = req.user.tenant_id;

    // Verify user belongs to administrator's school
    const userQuery = `
      SELECT u.id, u.first_name, u.last_name, u.email, u.role, u.status
      FROM users u
      WHERE u.id = $1 AND u.tenant_id = $2
    `;
    const userResult = await query(userQuery, [userId, tenantId]);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found or access denied'
      });
    }

    const user = userResult.rows[0];

    if (user.status !== 'pending') {
      return res.status(400).json({
        success: false,
        message: 'User is not pending approval'
      });
    }

    // Update user status
    const updateQuery = `
      UPDATE users 
      SET status = 'active', approved_at = NOW(), approved_by = $1
      WHERE id = $2 AND tenant_id = $3
    `;
    await query(updateQuery, [req.user.id, userId, tenantId]);

    res.json({
      success: true,
      message: 'User approved successfully'
    });
  } catch (error) {
    console.error('User approval error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to approve user'
    });
  }
});

// POST /api/administrator/users/:userId/reject - Reject user
router.post('/users/:userId/reject', authenticateToken, requireRole(['administrator']), async (req, res) => {
  try {
    const { userId } = req.params;
    const { reason } = req.body;
    const tenantId = req.user.tenant_id;

    // Verify user belongs to administrator's school
    const userQuery = `
      SELECT u.id, u.first_name, u.last_name, u.email, u.role, u.status
      FROM users u
      WHERE u.id = $1 AND u.tenant_id = $2
    `;
    const userResult = await query(userQuery, [userId, tenantId]);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found or access denied'
      });
    }

    const user = userResult.rows[0];

    if (user.status !== 'pending') {
      return res.status(400).json({
        success: false,
        message: 'User is not pending approval'
      });
    }

    // Update user status
    const updateQuery = `
      UPDATE users 
      SET status = 'rejected', rejected_at = NOW(), rejected_by = $1, rejection_reason = $2
      WHERE id = $3 AND tenant_id = $4
    `;
    await query(updateQuery, [req.user.id, reason, userId, tenantId]);

    res.json({
      success: true,
      message: 'User rejected successfully'
    });
  } catch (error) {
    console.error('User rejection error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to reject user'
    });
  }
});

// PUT /api/administrator/users/:userId - Update user
router.put('/users/:userId', authenticateToken, requireRole(['administrator']), async (req, res) => {
  try {
    const { userId } = req.params;
    const { first_name, last_name, email, phone, role, status } = req.body;
    const tenantId = req.user.tenant_id;

    // Verify user belongs to administrator's school
    const userQuery = `
      SELECT u.id FROM users u WHERE u.id = $1 AND u.tenant_id = $2
    `;
    const userResult = await query(userQuery, [userId, tenantId]);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found or access denied'
      });
    }

    // Update user
    const updateQuery = `
      UPDATE users 
      SET first_name = COALESCE($1, first_name),
          last_name = COALESCE($2, last_name),
          email = COALESCE($3, email),
          phone = COALESCE($4, phone),
          role = COALESCE($5, role),
          status = COALESCE($6, status),
          updated_at = NOW()
      WHERE id = $7 AND tenant_id = $8
    `;
    await query(updateQuery, [first_name, last_name, email, phone, role, status, userId, tenantId]);

    res.json({
      success: true,
      message: 'User updated successfully'
    });
  } catch (error) {
    console.error('User update error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to update user'
    });
  }
});

// DELETE /api/administrator/users/:userId - Delete user
router.delete('/users/:userId', authenticateToken, requireRole(['administrator']), async (req, res) => {
  try {
    const { userId } = req.params;
    const tenantId = req.user.tenant_id;

    // Verify user belongs to administrator's school
    const userQuery = `
      SELECT u.id, u.role FROM users u WHERE u.id = $1 AND u.tenant_id = $2
    `;
    const userResult = await query(userQuery, [userId, tenantId]);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found or access denied'
      });
    }

    const user = userResult.rows[0];

    // Delete user and related data
    await query('BEGIN');

    try {
      if (user.role === 'teacher') {
        await query('DELETE FROM classes WHERE teacher_id = $1', [userId]);
      } else if (user.role === 'student') {
        await query('DELETE FROM students WHERE user_id = $1', [userId]);
        await query('DELETE FROM student_grades WHERE student_id = (SELECT id FROM students WHERE user_id = $1)', [userId]);
        await query('DELETE FROM attendance_records WHERE student_id = (SELECT id FROM students WHERE user_id = $1)', [userId]);
      } else if (user.role === 'parent') {
        await query('DELETE FROM parent_students WHERE parent_id = $1', [userId]);
      }

      await query('DELETE FROM users WHERE id = $1 AND tenant_id = $2', [userId, tenantId]);

      await query('COMMIT');

      res.json({
        success: true,
        message: 'User deleted successfully'
      });
    } catch (error) {
      await query('ROLLBACK');
      throw error;
    }
  } catch (error) {
    console.error('User deletion error:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to delete user'
    });
  }
});

module.exports = router; 