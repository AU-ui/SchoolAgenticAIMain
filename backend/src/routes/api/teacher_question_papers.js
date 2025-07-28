const express = require('express');
const { query } = require('../../config/database');
const { authenticateToken, requireRole } = require('../../middleware/auth');
const PDFDocument = require('pdfkit');
const fs = require('fs');
const path = require('path');
const router = express.Router();

// GET /api/teacher/subjects
router.get('/subjects', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const subjectsQuery = `
      SELECT id, name, description 
      FROM subjects 
      ORDER BY name
    `;
    
    const result = await query(subjectsQuery);
    
    res.json({
      success: true,
      data: result.rows
    });
  } catch (error) {
    console.error('Error fetching subjects:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch subjects'
    });
  }
});

// GET /api/teacher/question-papers
router.get('/question-papers', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId, tenantId } = req.user;
    
    const papersQuery = `
      SELECT 
        qp.id,
        qp.title,
        qp.total_marks,
        qp.duration,
        qp.created_at,
        qp.filename,
        c.name as class_name,
        s.name as subject_name
      FROM question_papers qp
      JOIN classes c ON qp.class_id = c.id
      JOIN subjects s ON qp.subject_id = s.id
      WHERE qp.teacher_id = $1 AND qp.tenant_id = $2
      ORDER BY qp.created_at DESC
    `;
    
    const result = await query(papersQuery, [teacherId, tenantId]);
    
    res.json({
      success: true,
      data: result.rows
    });
  } catch (error) {
    console.error('Error fetching question papers:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch question papers'
    });
  }
});

// POST /api/teacher/question-papers
router.post('/question-papers', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId, tenantId } = req.user;
    const { title, class_id, subject_id, syllabus_id, total_marks, duration, sections } = req.body;
    
    // Insert question paper
    const insertQuery = `
      INSERT INTO question_papers (
        title, 
        class_id, 
        subject_id, 
        syllabus_id, 
        total_marks, 
        duration, 
        teacher_id, 
        tenant_id, 
        created_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
      RETURNING id
    `;
    
    const result = await query(insertQuery, [
      title, class_id, subject_id, syllabus_id, total_marks, duration, teacherId, tenantId
    ]);
    
    const paperId = result.rows[0].id;
    
    // Insert sections
    for (const section of sections) {
      const sectionQuery = `
        INSERT INTO question_paper_sections (
          question_paper_id, 
          name, 
          marks, 
          order_index
        ) VALUES ($1, $2, $3, $4)
      `;
      
      await query(sectionQuery, [
        paperId, 
        section.name, 
        section.marks, 
        sections.indexOf(section) + 1
      ]);
    }
    
    // Generate PDF
    const filename = await generateQuestionPaperPDF(paperId, title);
    
    // Update filename
    await query(
      'UPDATE question_papers SET filename = $1 WHERE id = $2',
      [filename, paperId]
    );
    
    res.json({
      success: true,
      message: 'Question paper created successfully',
      data: { id: paperId, filename }
    });
  } catch (error) {
    console.error('Error creating question paper:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to create question paper'
    });
  }
});

// GET /api/teacher/question-papers/:id/download
router.get('/question-papers/:id/download', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    const paperId = req.params.id;
    
    const query = `
      SELECT filename, title 
      FROM question_papers 
      WHERE id = $1 AND teacher_id = $2
    `;
    
    const result = await query(query, [paperId, teacherId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Question paper not found'
      });
    }
    
    const paper = result.rows[0];
    const filePath = path.join('uploads', 'question_papers', paper.filename);
    
    if (!fs.existsSync(filePath)) {
      return res.status(404).json({
        success: false,
        message: 'File not found'
      });
    }
    
    res.download(filePath, paper.filename);
  } catch (error) {
    console.error('Error downloading question paper:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to download question paper'
    });
  }
});

// DELETE /api/teacher/question-papers/:id
router.delete('/question-papers/:id', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    const paperId = req.params.id;
    
    // Get filename before deletion
    const getQuery = `
      SELECT filename 
      FROM question_papers 
      WHERE id = $1 AND teacher_id = $2
    `;
    
    const getResult = await query(getQuery, [paperId, teacherId]);
    
    if (getResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Question paper not found'
      });
    }
    
    // Delete file from filesystem
    const filename = getResult.rows[0].filename;
    const filePath = path.join('uploads', 'question_papers', filename);
    
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
    }
    
    // Delete sections first
    await query('DELETE FROM question_paper_sections WHERE question_paper_id = $1', [paperId]);
    
    // Delete question paper
    await query('DELETE FROM question_papers WHERE id = $1 AND teacher_id = $2', [paperId, teacherId]);
    
    res.json({
      success: true,
      message: 'Question paper deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting question paper:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to delete question paper'
    });
  }
});

// Helper function to generate PDF
async function generateQuestionPaperPDF(paperId, title) {
  return new Promise((resolve, reject) => {
    try {
      const doc = new PDFDocument();
      const filename = `question_paper_${paperId}_${Date.now()}.pdf`;
      const uploadDir = path.join('uploads', 'question_papers');
      
      if (!fs.existsSync(uploadDir)) {
        fs.mkdirSync(uploadDir, { recursive: true });
      }
      
      const filePath = path.join(uploadDir, filename);
      const stream = fs.createWriteStream(filePath);
      
      doc.pipe(stream);
      
      // Add header
      doc.fontSize(20).text(title, { align: 'center' });
      doc.moveDown();
      
      // Add sections (placeholder)
      doc.fontSize(14).text('Section A', { underline: true });
      doc.fontSize(12).text('Questions 1-10 (10 marks each)');
      doc.moveDown();
      
      doc.fontSize(14).text('Section B', { underline: true });
      doc.fontSize(12).text('Questions 11-15 (15 marks each)');
      doc.moveDown();
      
      doc.fontSize(14).text('Section C', { underline: true });
      doc.fontSize(12).text('Questions 16-20 (20 marks each)');
      
      doc.end();
      
      stream.on('finish', () => {
        resolve(filename);
      });
      
      stream.on('error', reject);
    } catch (error) {
      reject(error);
    }
  });
}

module.exports = router; 