const express = require('express');
const router = express.Router();
const { query } = require('../../config/database');
const { authenticateToken } = require('../../middleware/auth');

// Middleware to check if user is superadmin
const requireSuperadmin = (req, res, next) => {
  if (req.user.role !== 'superadmin') {
    return res.status(403).json({
      success: false,
      message: 'Access denied. Superadmin privileges required.'
    });
  }
  next();
};

// GET /api/superadmin/dashboard - Get superadmin dashboard data
router.get('/dashboard', authenticateToken, requireSuperadmin, async (req, res) => {
  try {
    // Get system-wide statistics
    const statsQuery = `
      SELECT 
        COUNT(DISTINCT s.id) as total_schools,
        COUNT(DISTINCT t.id) as total_tenants,
        COUNT(DISTINCT u.id) as total_users,
        COUNT(DISTINCT CASE WHEN s.is_active = true THEN s.id END) as active_schools
      FROM schools s
      LEFT JOIN tenants t ON s.tenant_id = t.id
      LEFT JOIN users u ON u.tenant_id = t.id
    `;
    
    const statsResult = await query(statsQuery);
    const stats = statsResult.rows[0];

    // Get recent activities
    const activitiesQuery = `
      SELECT 
        'school_created' as action,
        s.name as school_name,
        s.created_at as time
      FROM schools s
      ORDER BY s.created_at DESC
      LIMIT 5
    `;
    
    const activitiesResult = await query(activitiesQuery);
    const recentActivities = activitiesResult.rows.map(row => ({
      id: Math.random().toString(36).substr(2, 9),
      action: `New school registered: ${row.school_name}`,
      time: `${Math.floor(Math.random() * 24)} hours ago`,
      school: row.school_name
    }));

    res.json({
      success: true,
      data: {
        stats: {
          totalSchools: parseInt(stats.total_schools) || 0,
          totalTenants: parseInt(stats.total_tenants) || 0,
          totalUsers: parseInt(stats.total_users) || 0,
          activeSchools: parseInt(stats.active_schools) || 0
        },
        recentActivities
      }
    });
  } catch (error) {
    console.error('Error fetching superadmin dashboard data:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching dashboard data'
    });
  }
});

// GET /api/superadmin/search-schools - Search schools by name or code
router.get('/search-schools', authenticateToken, requireSuperadmin, async (req, res) => {
  try {
    const { query: searchQuery, type = 'name' } = req.query;
    
    if (!searchQuery || !searchQuery.trim()) {
      return res.status(400).json({
        success: false,
        message: 'Search query is required'
      });
    }

    let searchQuerySQL;
    let searchParams;

    if (type === 'code') {
      // Search by school code
      searchQuerySQL = `
        SELECT 
          s.id,
          s.name,
          s.code,
          t.name as tenant_name,
          COUNT(u.id) as user_count
        FROM schools s
        LEFT JOIN tenants t ON s.tenant_id = t.id
        LEFT JOIN users u ON u.tenant_id = t.id
        WHERE s.code ILIKE $1
        GROUP BY s.id, s.name, s.code, t.name
        ORDER BY s.name
      `;
      searchParams = [`%${searchQuery}%`];
    } else {
      // Search by school name
      searchQuerySQL = `
        SELECT 
          s.id,
          s.name,
          s.code,
          t.name as tenant_name,
          COUNT(u.id) as user_count
        FROM schools s
        LEFT JOIN tenants t ON s.tenant_id = t.id
        LEFT JOIN users u ON u.tenant_id = t.id
        WHERE s.name ILIKE $1
        GROUP BY s.id, s.name, s.code, t.name
        ORDER BY s.name
      `;
      searchParams = [`%${searchQuery}%`];
    }

    const result = await query(searchQuerySQL, searchParams);
    
    const schools = result.rows.map(row => ({
      id: row.id,
      name: row.name,
      code: row.code,
      tenant: row.tenant_name,
      users: parseInt(row.user_count) || 0
    }));

    res.json({
      success: true,
      data: {
        schools,
        searchQuery,
        searchType: type,
        totalResults: schools.length
      }
    });
  } catch (error) {
    console.error('Error searching schools:', error);
    res.status(500).json({
      success: false,
      message: 'Error searching schools'
    });
  }
});

// GET /api/superadmin/school-users/:schoolId - Get users for a specific school
router.get('/school-users/:schoolId', authenticateToken, requireSuperadmin, async (req, res) => {
  try {
    const { schoolId } = req.params;
    
    if (!schoolId) {
      return res.status(400).json({
        success: false,
        message: 'School ID is required'
      });
    }

    // Get school details
    const schoolQuery = `
      SELECT s.id, s.name, s.code, t.name as tenant_name
      FROM schools s
      LEFT JOIN tenants t ON s.tenant_id = t.id
      WHERE s.id = $1
    `;
    
    const schoolResult = await query(schoolQuery, [schoolId]);
    
    if (schoolResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'School not found'
      });
    }

    const school = schoolResult.rows[0];

    // Get users for this school (through tenant)
    const usersQuery = `
      SELECT 
        u.id,
        u.first_name,
        u.last_name,
        u.email,
        u.role,
        u.is_active,
        u.created_at
      FROM users u
      JOIN tenants t ON u.tenant_id = t.id
      JOIN schools s ON s.tenant_id = t.id
      WHERE s.id = $1
      ORDER BY u.role, u.first_name, u.last_name
    `;
    
    const usersResult = await query(usersQuery, [schoolId]);
    
    const users = usersResult.rows.map(user => ({
      id: user.id,
      firstName: user.first_name,
      lastName: user.last_name,
      email: user.email,
      role: user.role,
      status: user.is_active ? 'active' : 'inactive',
      createdAt: user.created_at
    }));

    res.json({
      success: true,
      data: {
        school: {
          id: school.id,
          name: school.name,
          code: school.code,
          tenant: school.tenant_name
        },
        users,
        totalUsers: users.length
      }
    });
  } catch (error) {
    console.error('Error fetching school users:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching school users'
    });
  }
});

// GET /api/superadmin/all-schools - Get all schools (for dropdown/listing)
router.get('/all-schools', authenticateToken, requireSuperadmin, async (req, res) => {
  try {
    const schoolsQuery = `
      SELECT 
        s.id,
        s.name,
        s.code,
        t.name as tenant_name,
        COUNT(u.id) as user_count
      FROM schools s
      LEFT JOIN tenants t ON s.tenant_id = t.id
      LEFT JOIN users u ON u.tenant_id = t.id
      GROUP BY s.id, s.name, s.code, t.name
      ORDER BY s.name
    `;
    
    const result = await query(schoolsQuery);
    
    const schools = result.rows.map(row => ({
      id: row.id,
      name: row.name,
      code: row.code,
      tenant: row.tenant_name,
      users: parseInt(row.user_count) || 0
    }));

    res.json({
      success: true,
      data: {
        schools,
        totalSchools: schools.length
      }
    });
  } catch (error) {
    console.error('Error fetching all schools:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching schools'
    });
  }
});

// GET /api/superadmin/user-stats - Get user statistics by role
router.get('/user-stats', authenticateToken, requireSuperadmin, async (req, res) => {
  try {
    const userStatsQuery = `
      SELECT 
        role,
        COUNT(*) as count,
        COUNT(CASE WHEN is_active = true THEN 1 END) as active_count
      FROM users
      GROUP BY role
      ORDER BY count DESC
    `;
    
    const result = await query(userStatsQuery);
    
    const stats = result.rows.map(row => ({
      role: row.role,
      total: parseInt(row.count),
      active: parseInt(row.active_count),
      inactive: parseInt(row.count) - parseInt(row.active_count)
    }));

    res.json({
      success: true,
      data: {
        stats,
        totalUsers: stats.reduce((sum, stat) => sum + stat.total, 0)
      }
    });
  } catch (error) {
    console.error('Error fetching user stats:', error);
    res.status(500).json({
      success: false,
      message: 'Error fetching user statistics'
    });
  }
});

module.exports = router; 