const express = require('express');
const router = express.Router();
const { authenticateToken } = require('../../middleware/auth');

// GET teacher's classes - Simple version
router.get('/teacher/:teacherId/classes', authenticateToken, async (req, res) => {
  try {
    const { teacherId } = req.params;
    
    // Return sample data for now
    const sampleClasses = [
      {
        id: 1,
        name: "Mathematics 101",
        grade_level: "10",
        academic_year: "2024-2025",
        subject: "Mathematics"
      },
      {
        id: 2,
        name: "Science Lab",
        grade_level: "9",
        academic_year: "2024-2025", 
        subject: "Science"
      }
    ];

    res.json({
      success: true,
      data: sampleClasses
    });

  } catch (error) {
    console.error('Error fetching teacher classes:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

module.exports = router;
