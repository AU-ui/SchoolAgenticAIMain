const express = require('express');
const { query } = require('../../config/database');

const router = express.Router();

// @route   GET /api/landing/schools
// @desc    Get list of active schools for landing page
// @access  Public
router.get('/schools', async (req, res) => {
  try {
    const schools = await query(
      `SELECT t.id, t.name, t.domain, t.address, t.phone, t.email, t.logo_url,
              COUNT(DISTINCT s.id) as school_count,
              COUNT(DISTINCT u.id) as user_count
       FROM tenants t
       LEFT JOIN schools s ON t.id = s.tenant_id AND s.is_active = true
       LEFT JOIN users u ON t.id = u.tenant_id AND u.is_active = true
       WHERE t.is_active = true
       GROUP BY t.id, t.name, t.domain, t.address, t.phone, t.email, t.logo_url
       ORDER BY t.name ASC`
    );

    res.json({
      success: true,
      data: {
        schools: schools.rows.map(school => ({
          id: school.id,
          name: school.name,
          domain: school.domain,
          address: school.address,
          phone: school.phone,
          email: school.email,
          logoUrl: school.logo_url,
          schoolCount: parseInt(school.school_count),
          userCount: parseInt(school.user_count)
        }))
      }
    });

  } catch (error) {
    console.error('Get schools error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// @route   GET /api/landing/schools/:id
// @desc    Get specific school details for landing page
// @access  Public
router.get('/schools/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const school = await query(
      `SELECT t.id, t.name, t.domain, t.address, t.phone, t.email, t.logo_url,
              COUNT(DISTINCT s.id) as school_count,
              COUNT(DISTINCT u.id) as user_count,
              COUNT(DISTINCT CASE WHEN u.role = 'teacher' THEN u.id END) as teacher_count,
              COUNT(DISTINCT CASE WHEN u.role = 'student' THEN u.id END) as student_count,
              COUNT(DISTINCT CASE WHEN u.role = 'parent' THEN u.id END) as parent_count
       FROM tenants t
       LEFT JOIN schools s ON t.id = s.tenant_id AND s.is_active = true
       LEFT JOIN users u ON t.id = u.tenant_id AND u.is_active = true
       WHERE t.id = $1 AND t.is_active = true
       GROUP BY t.id, t.name, t.domain, t.address, t.phone, t.email, t.logo_url`,
      [id]
    );

    if (school.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'School not found'
      });
    }

    const schoolData = school.rows[0];

    res.json({
      success: true,
      data: {
        school: {
          id: schoolData.id,
          name: schoolData.name,
          domain: schoolData.domain,
          address: schoolData.address,
          phone: schoolData.phone,
          email: schoolData.email,
          logoUrl: schoolData.logo_url,
          schoolCount: parseInt(schoolData.school_count),
          userCount: parseInt(schoolData.user_count),
          teacherCount: parseInt(schoolData.teacher_count),
          studentCount: parseInt(schoolData.student_count),
          parentCount: parseInt(schoolData.parent_count)
        }
      }
    });

  } catch (error) {
    console.error('Get school details error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// @route   POST /api/landing/contact
// @desc    Submit contact form from landing page
// @access  Public
router.post('/contact', async (req, res) => {
  try {
    const { name, email, phone, message, schoolId } = req.body;

    // Basic validation
    if (!name || !email || !message) {
      return res.status(400).json({
        success: false,
        message: 'Name, email, and message are required'
      });
    }

    // Store contact inquiry (you might want to create a contacts table)
    // For now, we'll just log it
    console.log('Contact inquiry received:', {
      name,
      email,
      phone,
      message,
      schoolId,
      timestamp: new Date().toISOString()
    });

    res.json({
      success: true,
      message: 'Thank you for your message. We will get back to you soon!'
    });

  } catch (error) {
    console.error('Contact form error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// @route   GET /api/landing/stats
// @desc    Get platform statistics for landing page
// @access  Public
router.get('/stats', async (req, res) => {
  try {
    const stats = await query(
      `SELECT 
        COUNT(DISTINCT t.id) as total_schools,
        COUNT(DISTINCT u.id) as total_users,
        COUNT(DISTINCT CASE WHEN u.role = 'teacher' THEN u.id END) as total_teachers,
        COUNT(DISTINCT CASE WHEN u.role = 'student' THEN u.id END) as total_students,
        COUNT(DISTINCT CASE WHEN u.role = 'parent' THEN u.id END) as total_parents
       FROM tenants t
       LEFT JOIN users u ON t.id = u.tenant_id AND u.is_active = true
       WHERE t.is_active = true`
    );

    const platformStats = stats.rows[0];

    res.json({
      success: true,
      data: {
        stats: {
          totalSchools: parseInt(platformStats.total_schools),
          totalUsers: parseInt(platformStats.total_users),
          totalTeachers: parseInt(platformStats.total_teachers),
          totalStudents: parseInt(platformStats.total_students),
          totalParents: parseInt(platformStats.total_parents)
        }
      }
    });

  } catch (error) {
    console.error('Get stats error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

module.exports = router; 