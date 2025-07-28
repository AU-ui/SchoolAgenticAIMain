const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { query } = require('../../config/database');
const { authenticateToken, requireRole } = require('../../middleware/auth');
const router = express.Router();

// Configure multer for file uploads
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = 'uploads/syllabus';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'syllabus-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'application/pdf') {
      cb(null, true);
    } else {
      cb(new Error('Only PDF files are allowed'), false);
    }
  },
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB limit
  }
});

// GET /api/teacher/classes
router.get('/classes', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { tenantId } = req.user;
    
    const classesQuery = `
      SELECT id, name, grade_level 
      FROM classes 
      WHERE tenant_id = $1 
      ORDER BY grade_level, name
    `;
    
    const result = await query(classesQuery, [tenantId]);
    
    res.json({
      success: true,
      data: result.rows
    });
  } catch (error) {
    console.error('Error fetching classes:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch classes'
    });
  }
});

// GET /api/teacher/boards
router.get('/boards', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const boardsQuery = `
      SELECT id, name, description 
      FROM education_boards 
      ORDER BY name
    `;
    
    const result = await query(boardsQuery);
    
    res.json({
      success: true,
      data: result.rows
    });
  } catch (error) {
    console.error('Error fetching boards:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch boards'
    });
  }
});

// GET /api/teacher/syllabus
router.get('/syllabus', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId, tenantId } = req.user;
    
    const syllabusQuery = `
      SELECT 
        s.id,
        s.filename,
        s.file_size,
        s.uploaded_at,
        s.subject,
        c.name as class_name,
        c.id as class_id,
        eb.name as board_name,
        eb.id as board_id
      FROM syllabus s
      JOIN classes c ON s.class_id = c.id
      JOIN education_boards eb ON s.board_id = eb.id
      WHERE s.teacher_id = $1 AND s.tenant_id = $2
      ORDER BY s.uploaded_at DESC
    `;
    
    const result = await query(syllabusQuery, [teacherId, tenantId]);
    
    res.json({
      success: true,
      data: result.rows
    });
  } catch (error) {
    console.error('Error fetching syllabus:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch syllabus'
    });
  }
});

// POST /api/teacher/syllabus/upload
router.post('/syllabus/upload', authenticateToken, requireRole(['teacher']), upload.single('syllabus'), async (req, res) => {
  try {
    const { id: teacherId, tenantId } = req.user;
    const { class_id, board_id, subject } = req.body;
    
    if (!req.file) {
      return res.status(400).json({
        success: false,
        message: 'No file uploaded'
      });
    }
    
    // Insert syllabus record
    const insertQuery = `
      INSERT INTO syllabus (
        filename, 
        file_path, 
        file_size, 
        subject, 
        class_id, 
        board_id, 
        teacher_id, 
        tenant_id, 
        uploaded_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
      RETURNING id
    `;
    
    const result = await query(insertQuery, [
      req.file.originalname,
      req.file.path,
      req.file.size,
      subject,
      class_id,
      board_id,
      teacherId,
      tenantId
    ]);
    
    res.json({
      success: true,
      message: 'Syllabus uploaded successfully',
      data: { id: result.rows[0].id }
    });
  } catch (error) {
    console.error('Error uploading syllabus:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to upload syllabus'
    });
  }
});

// GET /api/teacher/syllabus/:id/download
router.get('/syllabus/:id/download', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    const syllabusId = req.params.id;
    
    const query = `
      SELECT filename, file_path 
      FROM syllabus 
      WHERE id = $1 AND teacher_id = $2
    `;
    
    const result = await query(query, [syllabusId, teacherId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Syllabus not found'
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

// DELETE /api/teacher/syllabus/:id
router.delete('/syllabus/:id', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    const syllabusId = req.params.id;
    
    // Get file path before deletion
    const getQuery = `
      SELECT file_path 
      FROM syllabus 
      WHERE id = $1 AND teacher_id = $2
    `;
    
    const getResult = await query(getQuery, [syllabusId, teacherId]);
    
    if (getResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Syllabus not found'
      });
    }
    
    // Delete file from filesystem
    const filePath = getResult.rows[0].file_path;
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }
    
    // Delete from database
    const deleteQuery = `
      DELETE FROM syllabus 
      WHERE id = $1 AND teacher_id = $2
    `;
    
    await query(deleteQuery, [syllabusId, teacherId]);
    
    res.json({
      success: true,
      message: 'Syllabus deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting syllabus:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to delete syllabus'
    });
  }
});

// PUT /api/teacher/syllabus/:id/customize
router.put('/syllabus/:id/customize', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    const syllabusId = req.params.id;
    const {
      title,
      description,
      topics,
      learningObjectives,
      assessmentCriteria,
      resources,
      isPublic,
      sharedWithStudents
    } = req.body;
    
    // Update syllabus customization
    const updateQuery = `
      UPDATE syllabus 
      SET 
        title = $1,
        description = $2,
        topics = $3,
        learning_objectives = $4,
        assessment_criteria = $5,
        resources = $6,
        is_public = $7,
        shared_with_students = $8,
        updated_at = NOW()
      WHERE id = $9 AND teacher_id = $10
      RETURNING id
    `;
    
    const result = await query(updateQuery, [
      title,
      description,
      JSON.stringify(topics),
      JSON.stringify(learningObjectives),
      JSON.stringify(assessmentCriteria),
      JSON.stringify(resources),
      isPublic,
      sharedWithStudents,
      syllabusId,
      teacherId
    ]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Syllabus not found'
      });
    }
    
    res.json({
      success: true,
      message: 'Syllabus customized successfully'
    });
  } catch (error) {
    console.error('Error customizing syllabus:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to customize syllabus'
    });
  }
});

// POST /api/teacher/syllabus/:id/share
router.post('/syllabus/:id/share', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    const syllabusId = req.params.id;
    
    // Update syllabus to share with students
    const shareQuery = `
      UPDATE syllabus 
      SET shared_with_students = true, updated_at = NOW()
      WHERE id = $1 AND teacher_id = $2
      RETURNING id
    `;
    
    const result = await query(shareQuery, [syllabusId, teacherId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Syllabus not found'
      });
    }
    
    res.json({
      success: true,
      message: 'Syllabus shared with students successfully'
    });
  } catch (error) {
    console.error('Error sharing syllabus:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to share syllabus'
    });
  }
});

module.exports = router; 