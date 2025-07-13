const express = require('express');
const { query } = require('../../config/database');
const { authenticateToken, requireRole } = require('../../middleware/auth');
const router = express.Router();

// GET /api/teacher/reports/templates
router.get('/templates', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const templatesQuery = `
      SELECT id, name, description, template_type, content
      FROM report_templates
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

// GET /api/teacher/reports
router.get('/', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    
    const reportsQuery = `
      SELECT 
        id,
        title,
        report_type,
        class_id,
        created_at,
        status,
        insights_count,
        recommendations_count
      FROM teacher_reports
      WHERE teacher_id = $1
      ORDER BY created_at DESC
    `;
    
    const reportsResult = await query(reportsQuery, [teacherId]);
    
    res.json({
      success: true,
      data: {
        reports: reportsResult.rows
      }
    });
  } catch (error) {
    console.error('Reports fetch error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// POST /api/teacher/reports/generate
router.post('/generate', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { id: teacherId } = req.user;
    const { title, reportType, classId, templateId, dateRange, includeInsights, includeRecommendations } = req.body;
    
    // Call ML service for report generation
    const mlResponse = await fetch('http://localhost:8000/ml/teacher/reports/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        report_type: reportType,
        data: {
          class_id: classId,
          date_range: dateRange,
          include_insights: includeInsights,
          include_recommendations: includeRecommendations
        },
        template_id: templateId
      })
    });
    
    if (!mlResponse.ok) {
      throw new Error('ML service unavailable');
    }
    
    const mlData = await mlResponse.json();
    
    // Save report to database
    const insertQuery = `
      INSERT INTO teacher_reports (teacher_id, title, report_type, class_id, template_id, 
                                 insights_count, recommendations_count, report_data, status)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'completed')
      RETURNING id
    `;
    
    const insightsCount = mlData.data.insights ? mlData.data.insights.length : 0;
    const recommendationsCount = mlData.data.recommendations ? mlData.data.recommendations.length : 0;
    
    const result = await query(insertQuery, [
      teacherId, title, reportType, classId, templateId, 
      insightsCount, recommendationsCount, JSON.stringify(mlData.data)
    ]);
    
    res.json({
      success: true,
      data: {
        reportId: result.rows[0].id,
        report: mlData.data.report || 'Report generated successfully'
      }
    });
  } catch (error) {
    console.error('Report generation error:', error);
    res.status(500).json({ success: false, message: 'Failed to generate report' });
  }
});

// GET /api/teacher/reports/:reportId/download
router.get('/:reportId/download', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { reportId } = req.params;
    const { id: teacherId } = req.user;
    
    const reportQuery = `
      SELECT report_data FROM teacher_reports 
      WHERE id = $1 AND teacher_id = $2
    `;
    
    const reportResult = await query(reportQuery, [reportId, teacherId]);
    
    if (reportResult.rows.length === 0) {
      return res.status(404).json({ success: false, message: 'Report not found' });
    }
    
    const reportData = reportResult.rows[0].report_data;
    
    // Generate PDF report (simplified)
    const pdfContent = `Report: ${reportData.title || 'Generated Report'}\n\n${reportData.content || 'Report content'}`;
    
    res.setHeader('Content-Type', 'application/pdf');
    res.setHeader('Content-Disposition', `attachment; filename=report_${reportId}.pdf`);
    res.send(Buffer.from(pdfContent));
    
  } catch (error) {
    console.error('Report download error:', error);
    res.status(500).json({ success: false, message: 'Failed to download report' });
  }
});

// DELETE /api/teacher/reports/:reportId
router.delete('/:reportId', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { reportId } = req.params;
    const { id: teacherId } = req.user;
    
    await query('DELETE FROM teacher_reports WHERE id = $1 AND teacher_id = $2', [reportId, teacherId]);
    
    res.json({ success: true, message: 'Report deleted successfully' });
  } catch (error) {
    console.error('Report deletion error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

module.exports = router; 