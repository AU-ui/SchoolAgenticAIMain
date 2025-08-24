const express = require('express');
const { query } = require('../../config/database');
const { authenticateToken, requireRole } = require('../../middleware/auth');
const router = express.Router();

// Add ML service integration to existing teacher routes
const mlService = require('../../services/mlService');

const multer = require('multer');
const path = require('path');
const fs = require('fs');

// Configure multer for student image uploads
const studentImageStorage = multer.diskStorage({
  destination: function (req, file, cb) {
    const uploadDir = 'uploads/student-images';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'student-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const uploadStudentImage = multer({ 
  storage: studentImageStorage,
  limits: { fileSize: 5 * 1024 * 1024 }, // 5MB limit
  fileFilter: (req, file, cb) => {
    if (file.mimetype.startsWith('image/')) {
      cb(null, true);
    } else {
      cb(new Error('Only image files are allowed!'), false);
    }
  }
});

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
      LEFT JOIN students s ON c.id = s.class_id AND s.is_active = true
      WHERE c.teacher_id = $1 AND c.is_active = true
      GROUP BY c.id, c.name, c.grade_level, c.academic_year
      ORDER BY c.name
    `;
    
    const classesResult = await query(classesQuery, [teacherId]);
    
    res.json({
      success: true,
        classes: classesResult.rows
    });
  } catch (error) {
    console.error('Error fetching teacher classes:', error);
    res.status(500).json({ success: false, message: 'Failed to fetch classes' });
  }
});

// GET /api/teacher/classes/:classId/students
router.get('/classes/:classId/students', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { classId } = req.params;
    const { id: teacherId } = req.user;
    const { date } = req.query;

    // Verify teacher owns this class
    const classCheck = await query(`
      SELECT id FROM classes WHERE id = $1 AND teacher_id = $2
    `, [classId, teacherId]);

    if (classCheck.rows.length === 0) {
        return res.status(403).json({ 
          success: false, 
        message: 'You do not have permission to access this class'
      });
    }

    // Get students with their attendance status for the date
    const studentsQuery = `
      SELECT 
        s.id,
        s.student_id as student_code,
        CONCAT(u.first_name, ' ', u.last_name) as name,
        u.email,
        u.photo_url,
        COALESCE(ar.status, 'not_marked') as attendance_status,
        ar.notes,
        ar.created_at as marked_at
      FROM students s
      JOIN users u ON s.user_id = u.id
      LEFT JOIN attendance_records ar ON s.id = ar.student_id 
        AND ar.class_id = $1 
        AND ar.date = $2
      WHERE s.class_id = $1 AND s.is_active = true
      ORDER BY u.first_name, u.last_name
    `;
    
    const studentsResult = await query(studentsQuery, [
      classId, 
      date || new Date().toISOString().split('T')[0]
    ]);

    // Get AI predictions for students if ML service is available
    let studentsWithAI = studentsResult.rows;
    try {
      const predictions = await mlService.getAttendancePredictions({
        class_id: classId,
        students: studentsResult.rows.map(s => s.id),
        date: date || new Date().toISOString().split('T')[0]
      });
      
      studentsWithAI = studentsResult.rows.map(student => {
        const prediction = predictions?.find(p => p.student_id === student.id);
        return {
          ...student,
          ai_prediction: prediction?.attendance_probability || 0,
          risk_level: prediction?.risk_level || 'unknown',
          trend: prediction?.trend || 'stable'
        };
      });
    } catch (mlError) {
      console.warn('ML service not available, proceeding without AI predictions:', mlError.message);
    }
    
    res.json({
      success: true,
      students: studentsWithAI
    });
  } catch (error) {
    console.error('Error fetching students:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch students'
    });
  }
});

// POST /api/teacher/attendance/save
router.post('/attendance/save', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { class_id, date, attendance_data } = req.body;
    const { id: teacherId } = req.user;
    
    // Validate date (only allow today)
    const today = new Date().toISOString().split('T')[0];
    if (date !== today) {
      return res.status(400).json({ 
        success: false, 
        message: 'Can only mark attendance for today' 
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

    // Validate attendance data
    if (!attendance_data || typeof attendance_data !== 'object') {
      return res.status(400).json({
        success: false,
        message: 'Invalid attendance data'
      });
    }

    // Check for anomalies using AI if available
    let anomalyCheck = null;
    try {
      anomalyCheck = await mlService.checkAttendanceAnomalies({
        class_id: class_id,
        date: date,
        attendance_data: attendance_data
      });
      
      if (anomalyCheck?.anomalies_detected) {
        return res.status(400).json({
          success: false,
          message: 'Anomaly detected in attendance data',
          details: anomalyCheck.anomaly_details
        });
      }
    } catch (mlError) {
      console.warn('ML service not available for anomaly detection:', mlError.message);
    }

    // Save attendance records
    const client = await query.getClient();
    try {
      await client.query('BEGIN');
      
      // Delete existing records for this class and date
      await client.query(
        'DELETE FROM attendance_records WHERE class_id = $1 AND date = $2',
        [class_id, date]
      );
      
      // Insert new attendance records
      for (const [studentId, status] of Object.entries(attendance_data)) {
        if (['present', 'absent', 'late'].includes(status)) {
          await client.query(
            `INSERT INTO attendance_records 
             (student_id, class_id, date, status, teacher_id, created_at) 
             VALUES ($1, $2, $3, $4, $5, NOW())`,
            [studentId, class_id, date, status, teacherId]
          );
        }
      }
      
      await client.query('COMMIT');
      
      // Update ML model with new data if available
      try {
        await mlService.updateAttendanceModel({
          class_id: class_id,
          date: date,
          attendance_data: attendance_data
        });
      } catch (mlError) {
        console.warn('ML service not available for model update:', mlError.message);
      }
    
    res.json({
      success: true,
        message: 'Attendance marked successfully',
        ai_insights: anomalyCheck?.insights || null
      });
      
  } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
    
  } catch (error) {
    console.error('Error marking attendance:', error);
        res.status(500).json({
            success: false,
      message: 'Failed to mark attendance'
        });
    }
});

// GET /api/teacher/ml/insights/:classId
router.get('/ml/insights/:classId', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { classId } = req.params;
      const { id: teacherId } = req.user;

    // Verify teacher has access to this class
    const classCheck = await query(
      'SELECT id FROM classes WHERE id = $1 AND teacher_id = $2',
      [classId, teacherId]
    );
    
    if (classCheck.rows.length === 0) {
      return res.status(403).json({
        success: false, 
        message: 'Access denied to this class'
      });
    }
    
    // Get AI insights
    const insights = await mlService.getAttendanceInsights({
      class_id: classId,
      teacher_id: teacherId
    });

    res.json({
      success: true,
      insights: insights || {}
    });
  } catch (error) {
    console.error('Error fetching AI insights:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch AI insights'
    });
  }
});

module.exports = router; 