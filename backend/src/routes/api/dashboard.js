const express = require('express');
const router = express.Router();
const { authenticateToken } = require('../../middleware/auth');
const pool = require('../../config/database');

// GET teacher's classes - Real database version
router.get('/teacher/:teacherId/classes', authenticateToken, async (req, res) => {
  try {
    const { teacherId } = req.params;
    
          // Fetch real classes from database
      const query = `
        SELECT 
          c.id,
          c.name,
          c.grade_level,
          c.academic_year,
          c.name as subject,
          c.is_active,
          s.name as school_name
        FROM classes c
        JOIN schools s ON c.school_id = s.id
        WHERE c.teacher_id = $1 AND c.is_active = true
        ORDER BY c.name
      `;
    
    const result = await pool.query(query, [teacherId]);
    
    console.log(`Found ${result.rows.length} classes for teacher ${teacherId}`);
    
    res.json({
      success: true,
      data: result.rows
    });

  } catch (error) {
    console.error('Error fetching teacher classes:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message
    });
  }
});

module.exports = router;
