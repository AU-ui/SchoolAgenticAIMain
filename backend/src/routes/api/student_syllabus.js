const express = require('express');
const { query } = require('../../config/database');
const { authenticateToken, requireRole } = require('../../middleware/auth');
const fs = require('fs');
const path = require('path');
const router = express.Router();

// GET /api/student/syllabus
router.get('/syllabus', authenticateToken, requireRole(['student']), async (req, res) => {
  try {
    const { id: studentId, tenantId } = req.user;
    
    // Get student's class
    const studentQuery = `
      SELECT class_id FROM students WHERE user_id = $1 AND tenant_id = $2
    `;
    
    const studentResult = await query(studentQuery, [studentId, tenantId]);
    
    if (studentResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Student not found'
      });
    }
    
    const classId = studentResult.rows[0].class_id;
    
    // Get shared syllabi for student's class
    const syllabusQuery = `
      SELECT 
        s.id,
        s.title,
        s.description,
        s.subject,
        s.filename,
        s.topics,
        s.learning_objectives,
        s.assessment_criteria,
        s.resources,
        s.shared_with_students,
        s.uploaded_at,
        c.name as class_name,
        eb.name as board_name,
        CONCAT(u.first_name, ' ', u.last_name) as teacher_name
      FROM syllabus s
      JOIN classes c ON s.class_id = c.id
      JOIN education_boards eb ON s.board_id = eb.id
      JOIN users u ON s.teacher_id = u.id
      WHERE s.class_id = $1 
        AND s.tenant_id = $2 
        AND s.shared_with_students = true
      ORDER BY s.uploaded_at DESC
    `;
    
    const result = await query(syllabusQuery, [classId, tenantId]);
    
    res.json({
      success: true,
      data: result.rows
    });
  } catch (error) {
    console.error('Error fetching student syllabus:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch syllabus'
    });
  }
});

// GET /api/student/syllabus/:id/download
router.get('/syllabus/:id/download', authenticateToken, requireRole(['student']), async (req, res) => {
  try {
    const { id: studentId, tenantId } = req.user;
    const syllabusId = req.params.id;
    
    // Verify student has access to this syllabus
    const accessQuery = `
      SELECT s.filename, s.file_path, s.shared_with_students
      FROM syllabus s
      JOIN students st ON s.class_id = st.class_id
      WHERE s.id = $1 AND st.user_id = $2 AND s.tenant_id = $3 AND s.shared_with_students = true
    `;
    
    const result = await query(accessQuery, [syllabusId, studentId, tenantId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Syllabus not found or access denied'
      });
    }
    
    const syllabus = result.rows[0];
    
    if (!fs.existsSync(syllabus.file_path)) {
      return res.status(404).json({
        success: false,
        message: 'File not found'
      });
    }
    
    res.download(syllabus.file_path, syllabus.filename);
  } catch (error) {
    console.error('Error downloading syllabus:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to download syllabus'
    });
  }
});

module.exports = router; 