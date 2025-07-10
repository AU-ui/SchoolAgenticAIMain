const express = require('express');
const { query } = require('../../config/database');
const { authenticateToken, requireRole } = require('../../middleware/auth');
const { generateBranchSchoolCode } = require('../../utils/generateBranchSchoolCode');

const router = express.Router();

// @route   GET /api/admin/dashboard
// @desc    Get admin dashboard data
// @access  Admin/Superadmin only
router.get('/dashboard', authenticateToken, requireRole(['admin', 'superadmin']), async (req, res) => {
  try {
    const { role, tenantId } = req.user;

    // Get statistics based on user role
    let statsQuery = '';
    let statsParams = [];

    if (role === 'superadmin') {
      // Superadmin sees all data
      statsQuery = `
        SELECT 
          (SELECT COUNT(*) FROM tenants WHERE is_active = true) as total_schools,
          (SELECT COUNT(*) FROM users WHERE is_active = true) as total_users,
          (SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = true) as total_admins,
          (SELECT COUNT(*) FROM users WHERE role = 'teacher' AND is_active = true) as total_teachers,
          (SELECT COUNT(*) FROM users WHERE role = 'student' AND is_active = true) as total_students,
          (SELECT COUNT(*) FROM users WHERE role = 'parent' AND is_active = true) as total_parents
      `;
    } else {
      // Admin sees only their tenant data
      statsQuery = `
        SELECT 
          (SELECT COUNT(*) FROM schools WHERE tenant_id = $1 AND is_active = true) as total_schools,
          (SELECT COUNT(*) FROM users WHERE tenant_id = $1 AND is_active = true) as total_users,
          (SELECT COUNT(*) FROM users WHERE role = 'admin' AND tenant_id = $1 AND is_active = true) as total_admins,
          (SELECT COUNT(*) FROM users WHERE role = 'teacher' AND tenant_id = $1 AND is_active = true) as total_teachers,
          (SELECT COUNT(*) FROM users WHERE role = 'student' AND tenant_id = $1 AND is_active = true) as total_students,
          (SELECT COUNT(*) FROM users WHERE role = 'parent' AND tenant_id = $1 AND is_active = true) as total_parents
      `;
      statsParams = [tenantId];
    }

    const statsResult = await query(statsQuery, statsParams);
    const stats = statsResult.rows[0];

    // Get schools data
    let schoolsQuery = '';
    let schoolsParams = [];

    if (role === 'superadmin') {
      schoolsQuery = `
        SELECT 
          t.id,
          t.name,
          t.address,
          t.phone,
          t.email,
          t.is_active,
          (SELECT COUNT(*) FROM users WHERE tenant_id = t.id AND role = 'student' AND is_active = true) as student_count,
          (SELECT COUNT(*) FROM users WHERE tenant_id = t.id AND role = 'teacher' AND is_active = true) as teacher_count
        FROM tenants t
        ORDER BY t.created_at DESC
        LIMIT 10
      `;
    } else {
      schoolsQuery = `
        SELECT 
          s.id,
          s.name,
          s.address,
          s.phone,
          s.email,
          s.is_active,
          (SELECT COUNT(*) FROM students WHERE school_id = s.id AND is_active = true) as student_count,
          (SELECT COUNT(*) FROM teachers WHERE school_id = s.id AND is_active = true) as teacher_count
        FROM schools s
        WHERE s.tenant_id = $1
        ORDER BY s.created_at DESC
        LIMIT 10
      `;
      schoolsParams = [tenantId];
    }

    const schoolsResult = await query(schoolsQuery, schoolsParams);
    const schools = schoolsResult.rows.map(school => ({
      id: school.id,
      name: school.name,
      location: school.address || 'Not specified',
      principal: 'To be implemented', // This would need a separate query
      studentCount: parseInt(school.student_count) || 0,
      teacherCount: parseInt(school.teacher_count) || 0,
      status: school.is_active ? 'Active' : 'Inactive'
    }));

    // Get recent activities (placeholder for now)
    const recentActivities = [
      {
        id: 1,
        type: 'user_registration',
        description: 'New teacher registered',
        timestamp: new Date().toISOString(),
        user: 'John Doe'
      },
      {
        id: 2,
        type: 'school_created',
        description: 'New school added to system',
        timestamp: new Date(Date.now() - 86400000).toISOString(),
        user: 'System Admin'
      }
    ];

    res.json({
      success: true,
      data: {
        stats: {
          totalSchools: parseInt(stats.total_schools) || 0,
          totalUsers: parseInt(stats.total_users) || 0,
          totalPrincipals: parseInt(stats.total_admins) || 0,
          totalTeachers: parseInt(stats.total_teachers) || 0,
          totalStudents: parseInt(stats.total_students) || 0,
          totalParents: parseInt(stats.total_parents) || 0
        },
        schools,
        recentActivities
      }
    });

  } catch (error) {
    console.error('Admin dashboard error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// GET /api/admin/users?role=teacher&tenantId=1
router.get('/users', authenticateToken, requireRole(['superadmin', 'admin']), async (req, res) => {
  try {
    const { role: filterRole, tenantId: filterTenantId } = req.query;
    const user = req.user;
    let sql = 'SELECT id, email, first_name, last_name, role, tenant_id, is_active, email_verified FROM users WHERE 1=1';
    let params = [];

    // Admin can only see users for their own school
    if (user.role === 'admin') {
      sql += ' AND tenant_id = $1';
      params.push(user.tenantId);
    } else if (filterTenantId) {
      sql += ' AND tenant_id = $1';
      params.push(filterTenantId);
    }
    if (filterRole) {
      sql += params.length ? ' AND role = $2' : ' AND role = $1';
      params.push(filterRole);
    }
    sql += ' ORDER BY created_at DESC';
    const result = await query(sql, params);
    res.json({ success: true, data: result.rows });
  } catch (error) {
    console.error('List users error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// PUT /api/admin/users/:id
router.put('/users/:id', authenticateToken, requireRole(['superadmin', 'admin']), async (req, res) => {
  try {
    const { id } = req.params;
    const { firstName, lastName, role, isActive } = req.body;
    const user = req.user;
    // Only superadmin can change role to/from admin or superadmin
    if (user.role === 'admin' && ['admin', 'superadmin'].includes(role)) {
      return res.status(403).json({ success: false, message: 'Admins cannot assign admin or superadmin roles.' });
    }
    // Admin can only update users in their own school
    let sql = 'UPDATE users SET';
    let updates = [];
    let params = [];
    if (firstName) { updates.push(' first_name = $' + (params.length + 1)); params.push(firstName); }
    if (lastName) { updates.push(' last_name = $' + (params.length + 1)); params.push(lastName); }
    if (role) { updates.push(' role = $' + (params.length + 1)); params.push(role); }
    if (typeof isActive === 'boolean') { updates.push(' is_active = $' + (params.length + 1)); params.push(isActive); }
    if (!updates.length) return res.status(400).json({ success: false, message: 'No fields to update.' });
    sql += updates.join(',') + ' WHERE id = $' + (params.length + 1);
    params.push(id);
    if (user.role === 'admin') {
      sql += ' AND tenant_id = $' + (params.length + 1);
      params.push(user.tenantId);
    }
    const result = await query(sql, params);
    res.json({ success: true, message: 'User updated.' });
  } catch (error) {
    console.error('Update user error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// DELETE /api/admin/users/:id (deactivate user)
router.delete('/users/:id', authenticateToken, requireRole(['superadmin', 'admin']), async (req, res) => {
  try {
    const { id } = req.params;
    const user = req.user;
    let sql = 'UPDATE users SET is_active = false WHERE id = $1';
    let params = [id];
    if (user.role === 'admin') {
      sql += ' AND tenant_id = $2';
      params.push(user.tenantId);
    }
    await query(sql, params);
    res.json({ success: true, message: 'User deactivated.' });
  } catch (error) {
    console.error('Deactivate user error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// POST /api/admin/school-codes (generate new school code)
router.post('/school-codes', authenticateToken, requireRole(['superadmin', 'admin', 'administrator']), async (req, res) => {
  try {
    const { expiresAt, maxUses, description, schoolId } = req.body;
    const user = req.user;
    
    // Determine tenant_id based on user role
    let tenantId = user.tenantId;
    if (user.role === 'superadmin' && req.body.tenantId) {
      tenantId = req.body.tenantId;
    }
    if (!schoolId) {
      return res.status(400).json({ success: false, message: 'schoolId is required' });
    }

    // Generate a unique code for this branch
    let code;
    let isUnique = false;
    while (!isUnique) {
      code = generateBranchSchoolCode(tenantId, schoolId);
      const check = await query('SELECT 1 FROM school_codes WHERE code = $1', [code]);
      if (check.rows.length === 0) isUnique = true;
    }

    const result = await query(
      `INSERT INTO school_codes (code, tenant_id, school_id, created_by, expires_at, max_uses, description)
       VALUES ($1, $2, $3, $4, $5, $6, $7)
       RETURNING id, code, tenant_id, school_id, created_at, expires_at, max_uses, current_uses, is_active`,
      [code, tenantId, schoolId, user.id, expiresAt || null, maxUses || 1, description || null]
    );
    
    res.json({ success: true, data: result.rows[0] });
  } catch (error) {
    console.error('Generate school code error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// GET /api/admin/school-codes (list school codes)
router.get('/school-codes', authenticateToken, requireRole(['superadmin', 'admin', 'administrator']), async (req, res) => {
  try {
    const user = req.user;
    let sql = 'SELECT sc.*, t.name as school_name FROM school_codes sc JOIN tenants t ON sc.tenant_id = t.id WHERE 1=1';
    let params = [];
    
    // Admin/administrator can only see codes for their school
    if (user.role !== 'superadmin') {
      sql += ' AND sc.tenant_id = $1';
      params.push(user.tenantId);
    }
    
    sql += ' ORDER BY sc.created_at DESC';
    const result = await query(sql, params);
    res.json({ success: true, data: result.rows });
  } catch (error) {
    console.error('List school codes error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// Regenerate school code (superadmin only)
router.post('/school-codes/:id/regenerate', authenticateToken, requireRole(['superadmin']), async (req, res) => {
  try {
    const { id } = req.params;
    // Find the old code
    const oldCodeResult = await query('SELECT * FROM school_codes WHERE id = $1', [id]);
    if (oldCodeResult.rows.length === 0) {
      return res.status(404).json({ success: false, message: 'School code not found' });
    }
    const oldCode = oldCodeResult.rows[0];
    // Disable the old code
    await query('UPDATE school_codes SET is_active = false WHERE id = $1', [id]);
    // Generate a new code
    const code = generateSchoolCode();
    const result = await query(
      `INSERT INTO school_codes (code, tenant_id, created_by, expires_at, max_uses, description)
       VALUES ($1, $2, $3, $4, $5, $6)
       RETURNING id, code, tenant_id, created_at, expires_at, max_uses, current_uses, is_active`,
      [code, oldCode.tenant_id, req.user.id, oldCode.expires_at, oldCode.max_uses, oldCode.description]
    );
    res.json({ success: true, data: result.rows[0] });
  } catch (error) {
    console.error('Regenerate school code error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// GET /api/admin/pending-users (list pending users for approval)
router.get('/pending-users', authenticateToken, requireRole(['superadmin', 'admin', 'administrator']), async (req, res) => {
  try {
    const user = req.user;
    let sql = 'SELECT id, email, first_name, last_name, role, created_at FROM users WHERE status = $1';
    let params = ['pending'];
    
    // Admin/administrator can only see pending users for their school
    if (user.role !== 'superadmin') {
      sql += ' AND tenant_id = $2';
      params.push(user.tenantId);
    }
    
    sql += ' ORDER BY created_at DESC';
    const result = await query(sql, params);
    res.json({ success: true, data: result.rows });
  } catch (error) {
    console.error('List pending users error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// PUT /api/admin/pending-users/:id/approve (approve pending user)
router.put('/pending-users/:id/approve', authenticateToken, requireRole(['superadmin', 'admin', 'administrator']), async (req, res) => {
  try {
    const { id } = req.params;
    const user = req.user;
    
    let sql = 'UPDATE users SET status = $1, updated_at = NOW() WHERE id = $2 AND status = $3';
    let params = ['active', id, 'pending'];
    
    // Admin/administrator can only approve users for their school
    if (user.role !== 'superadmin') {
      sql += ' AND tenant_id = $4';
      params.push(user.tenantId);
    }
    
    const result = await query(sql, params);
    if (result.rowCount === 0) {
      return res.status(404).json({ success: false, message: 'User not found or already processed' });
    }
    
    res.json({ success: true, message: 'User approved successfully' });
  } catch (error) {
    console.error('Approve user error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// PUT /api/admin/pending-users/:id/reject (reject pending user)
router.put('/pending-users/:id/reject', authenticateToken, requireRole(['superadmin', 'admin', 'administrator']), async (req, res) => {
  try {
    const { id } = req.params;
    const user = req.user;
    
    let sql = 'UPDATE users SET status = $1, updated_at = NOW() WHERE id = $2 AND status = $3';
    let params = ['rejected', id, 'pending'];
    
    // Admin/administrator can only reject users for their school
    if (user.role !== 'superadmin') {
      sql += ' AND tenant_id = $4';
      params.push(user.tenantId);
    }
    
    const result = await query(sql, params);
    if (result.rowCount === 0) {
      return res.status(404).json({ success: false, message: 'User not found or already processed' });
    }
    
    res.json({ success: true, message: 'User rejected successfully' });
  } catch (error) {
    console.error('Reject user error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// Validate school code and return school name
router.get('/school-codes/validate/:code', async (req, res) => {
  try {
    const { code } = req.params;
    const result = await query(
      `SELECT sc.code, sc.is_active, sc.expires_at, sc.max_uses, sc.current_uses, sc.tenant_id, t.name as school_name
       FROM school_codes sc
       JOIN tenants t ON sc.tenant_id = t.id
       WHERE sc.code = $1`,
      [code]
    );
    if (result.rows.length === 0) {
      return res.status(404).json({ success: false, message: 'Invalid school code' });
    }
    const row = result.rows[0];
    res.json({
      success: true,
      schoolName: row.school_name,
      isActive: row.is_active,
      expiresAt: row.expires_at,
      maxUses: row.max_uses,
      currentUses: row.current_uses,
      tenantId: row.tenant_id
    });
  } catch (error) {
    console.error('Validate school code error:', error);
    res.status(500).json({ success: false, message: 'Internal server error' });
  }
});

// Helper function to generate school code
function generateSchoolCode() {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
  let code = '';
  for (let i = 0; i < 8; i++) {
    if (i === 4) code += '-';
    code += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return code;
}

module.exports = router; 