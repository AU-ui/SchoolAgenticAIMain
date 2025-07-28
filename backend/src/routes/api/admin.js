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
    let sql;
    let params = [];

    if (user.role === 'superadmin') {
      // Superadmin: see all users, optionally filter by role
      sql = 'SELECT id, email, first_name, last_name, role, tenant_id, is_active, email_verified FROM users WHERE 1=1';
      if (filterRole) {
        sql += ' AND role = $1';
        params.push(filterRole);
      }
    } else if (user.role === 'admin') {
      // Admin: only see users for their own school
      sql = 'SELECT id, email, first_name, last_name, role, tenant_id, is_active, email_verified FROM users WHERE tenant_id = $1';
      params.push(user.tenantId);
      if (filterRole) {
        sql += ' AND role = $2';
        params.push(filterRole);
      }
    } else if (filterTenantId) {
      sql = 'SELECT id, email, first_name, last_name, role, tenant_id, is_active, email_verified FROM users WHERE tenant_id = $1';
      params.push(filterTenantId);
      if (filterRole) {
        sql += ' AND role = $2';
        params.push(filterRole);
      }
    } else {
      // fallback: no access
      return res.status(403).json({ success: false, message: 'Forbidden' });
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
router.delete('/users/:id', authenticateToken, requireRole(['admin', 'superadmin']), async (req, res) => {
  try {
    const { id: adminId } = req.user;
    const userId = req.params.id;
    const { reason, deleted_by } = req.body;

    // Prevent self-deletion
    if (userId == adminId) {
      return res.status(400).json({
        success: false,
        message: 'You cannot delete your own account'
      });
    }

    // Check if user exists and get user info
    const userQuery = `
      SELECT u.id, u.email, u.role, u.tenant_id, t.name as tenant_name
      FROM users u
      JOIN tenants t ON u.tenant_id = t.id
      WHERE u.id = $1
    `;
    
    const userResult = await query(userQuery, [userId]);
    
    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    const userToDelete = userResult.rows[0];

    // Prevent deletion of superadmin by non-superadmin
    if (userToDelete.role === 'superadmin' && req.user.role !== 'superadmin') {
      return res.status(403).json({
        success: false,
        message: 'Only superadmin can delete superadmin accounts'
      });
    }

    // Start transaction
    await query('BEGIN');

    try {
      // Log the deletion
      const logQuery = `
        INSERT INTO user_deletion_logs (
          user_id, 
          user_email, 
          user_role, 
          tenant_id, 
          tenant_name,
          deleted_by, 
          deletion_reason, 
          deleted_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
      `;
      
      await query(logQuery, [
        userId,
        userToDelete.email,
        userToDelete.role,
        userToDelete.tenant_id,
        userToDelete.tenant_name,
        deleted_by,
        reason
      ]);

      // Delete related data based on user role
      if (userToDelete.role === 'student') {
        // Delete student-specific data
        await query('DELETE FROM student_attendance WHERE student_id IN (SELECT id FROM students WHERE user_id = $1)', [userId]);
        await query('DELETE FROM student_grades WHERE student_id IN (SELECT id FROM students WHERE user_id = $1)', [userId]);
        await query('DELETE FROM students WHERE user_id = $1', [userId]);
      } else if (userToDelete.role === 'teacher') {
        // Delete teacher-specific data
        await query('DELETE FROM teacher_assignments WHERE teacher_id IN (SELECT id FROM teachers WHERE user_id = $1)', [userId]);
        await query('DELETE FROM teachers WHERE user_id = $1', [userId]);
      } else if (userToDelete.role === 'parent') {
        // Delete parent-specific data
        await query('DELETE FROM parent_students WHERE parent_id IN (SELECT id FROM parents WHERE user_id = $1)', [userId]);
        await query('DELETE FROM parents WHERE user_id = $1', [userId]);
      }

      // Delete user sessions
      await query('DELETE FROM user_sessions WHERE user_id = $1', [userId]);

      // Finally, delete the user
      await query('DELETE FROM users WHERE id = $1', [userId]);

      // Commit transaction
      await query('COMMIT');

      res.json({
        success: true,
        message: 'User deleted successfully',
        data: {
          deleted_user: {
            id: userId,
            email: userToDelete.email,
            role: userToDelete.role
          }
        }
      });

    } catch (error) {
      // Rollback transaction on error
      await query('ROLLBACK');
      throw error;
    }

  } catch (error) {
    console.error('Error deleting user:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to delete user'
    });
  }
});

// PUT /api/admin/users/:id/deactivate
router.put('/users/:id/deactivate', authenticateToken, requireRole(['admin', 'superadmin']), async (req, res) => {
  try {
    const { id: adminId } = req.user;
    const userId = req.params.id;
    const { deactivated_by } = req.body;

    // Prevent self-deactivation
    if (userId == adminId) {
      return res.status(400).json({
        success: false,
        message: 'You cannot deactivate your own account'
      });
    }

    const updateQuery = `
      UPDATE users 
      SET status = 'inactive', updated_at = NOW()
      WHERE id = $1
      RETURNING id, email, role
    `;
    
    const result = await query(updateQuery, [userId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    res.json({
      success: true,
      message: 'User deactivated successfully',
      data: result.rows[0]
    });

  } catch (error) {
    console.error('Error deactivating user:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to deactivate user'
    });
  }
});

// PUT /api/admin/users/:id/activate
router.put('/users/:id/activate', authenticateToken, requireRole(['admin', 'superadmin']), async (req, res) => {
  try {
    const userId = req.params.id;
    const { activated_by } = req.body;

    const updateQuery = `
      UPDATE users 
      SET status = 'active', updated_at = NOW()
      WHERE id = $1
      RETURNING id, email, role
    `;
    
    const result = await query(updateQuery, [userId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    res.json({
      success: true,
      message: 'User activated successfully',
      data: result.rows[0]
    });

  } catch (error) {
    console.error('Error activating user:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to activate user'
    });
  }
});

// GET /api/admin/users
router.get('/users', authenticateToken, requireRole(['admin', 'superadmin']), async (req, res) => {
  try {
    const { tenantId } = req.user;
    
    const usersQuery = `
      SELECT 
        u.id,
        u.first_name,
        u.last_name,
        u.email,
        u.role,
        u.status,
        u.created_at,
        u.updated_at
      FROM users u
      WHERE u.tenant_id = $1
      ORDER BY u.created_at DESC
    `;
    
    const result = await query(usersQuery, [tenantId]);
    
    res.json({
      success: true,
      data: result.rows
    });
  } catch (error) {
    console.error('Error fetching users:', error);
    res.status(500).json({
      success: false,
      message: 'Failed to fetch users'
    });
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

// Validate school code and return school name with logo
router.get('/school-codes/validate/:code', async (req, res) => {
  try {
    const { code } = req.params;
    const result = await query(
      `SELECT sc.code, sc.is_active, sc.expires_at, sc.max_uses, sc.current_uses, sc.tenant_id, 
              t.name as school_name, t.logo_url
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
      logoUrl: row.logo_url, // Include logo URL
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