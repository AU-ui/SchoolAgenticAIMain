const express = require('express');
const { query } = require('../../config/database');
const { authenticateToken, requireRole } = require('../../middleware/auth');
const router = express.Router();

// GET /api/teacher/classes/:classId
router.get('/classes/:classId', authenticateToken, requireRole(['teacher']), async (req, res) => {
  try {
    const { classId } = req.params;
    const classQuery = `
      SELECT id, name
      FROM classes
      WHERE id = $1
    `;
    const result = await query(classQuery, [classId]);
    if (result.rows.length === 0) {
      return res.status(404).json({ success: false, message: 'Class not found' });
    }
    res.json({ success: true, data: result.rows[0] });
  } catch (error) {
    console.error('Class fetch error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

module.exports = router; 