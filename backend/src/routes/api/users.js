const express = require('express');
const bcrypt = require('bcryptjs');
const { query } = require('../../config/database');
const { sendEmail } = require('../../services/emailService');
const { 
  authenticateToken, 
  requireAdminAccess, 
  requireRole, 
  requireTenantAccess,
  validateAdminPassword 
} = require('../../middleware/auth');

const router = express.Router();

// Get all users (admin/superadmin only)
router.get('/', authenticateToken, requireAdminAccess, async (req, res) => {
  try {
    const { role, tenantId } = req.user;
    let usersQuery;
    let queryParams = [];

    if (role === 'superadmin') {
      // Superadmin can see all users
      usersQuery = `
        SELECT u.id, u.email, u.first_name, u.last_name, u.role, u.tenant_id, 
               u.is_active, u.email_verified, u.requires_approval, u.created_at,
               t.name as tenant_name
        FROM users u
        LEFT JOIN tenants t ON u.tenant_id = t.id
        ORDER BY u.created_at DESC
      `;
    } else {
      // Admin can only see users from their tenant
      usersQuery = `
        SELECT u.id, u.email, u.first_name, u.last_name, u.role, u.tenant_id, 
               u.is_active, u.email_verified, u.requires_approval, u.created_at,
               t.name as tenant_name
        FROM users u
        LEFT JOIN tenants t ON u.tenant_id = t.id
        WHERE u.tenant_id = $1
        ORDER BY u.created_at DESC
      `;
      queryParams = [tenantId];
    }

    const result = await query(usersQuery, queryParams);

    res.json({
      success: true,
      users: result.rows
    });
  } catch (error) {
    console.error('Error fetching users:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Get pending approvals (admin/superadmin only)
router.get('/pending', authenticateToken, requireAdminAccess, async (req, res) => {
  try {
    const { role, tenantId } = req.user;
    let query;
    let queryParams = [];

    if (role === 'superadmin') {
      query = `
        SELECT u.id, u.email, u.first_name, u.last_name, u.role, u.tenant_id, 
               u.created_at, t.name as tenant_name
        FROM users u
        LEFT JOIN tenants t ON u.tenant_id = t.id
        WHERE u.requires_approval = true
        ORDER BY u.created_at ASC
      `;
    } else {
      query = `
        SELECT u.id, u.email, u.first_name, u.last_name, u.role, u.tenant_id, 
               u.created_at, t.name as tenant_name
        FROM users u
        LEFT JOIN tenants t ON u.tenant_id = t.id
        WHERE u.requires_approval = true AND u.tenant_id = $1
        ORDER BY u.created_at ASC
      `;
      queryParams = [tenantId];
    }

    const result = await query(query, queryParams);

    res.json({
      success: true,
      pendingUsers: result.rows
    });
  } catch (error) {
    console.error('Error fetching pending users:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Approve user (admin/superadmin only)
router.post('/:userId/approve', authenticateToken, requireAdminAccess, async (req, res) => {
  try {
    const { userId } = req.params;
    const { role, tenantId } = req.user;

    // Check if user exists and get their details
    let userQuery;
    let queryParams = [userId];

    if (role !== 'superadmin') {
      userQuery = `
        SELECT u.*, t.name as tenant_name 
        FROM users u 
        LEFT JOIN tenants t ON u.tenant_id = t.id 
        WHERE u.id = $1 AND u.tenant_id = $2
      `;
      queryParams = [userId, tenantId];
    } else {
      userQuery = `
        SELECT u.*, t.name as tenant_name 
        FROM users u 
        LEFT JOIN tenants t ON u.tenant_id = t.id 
        WHERE u.id = $1
      `;
    }

    const userResult = await query(userQuery, queryParams);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found or access denied'
      });
    }

    const user = userResult.rows[0];

    if (!user.requires_approval) {
      return res.status(400).json({
        success: false,
        message: 'User does not require approval'
      });
    }

    // Approve the user
    await query(
      'UPDATE users SET requires_approval = false, is_active = true WHERE id = $1',
      [userId]
    );

    // Send approval email
    await sendEmail({
      to: user.email,
      subject: 'Account Approved - SchoolAgenticAI',
      html: `
        <h2>Account Approved!</h2>
        <p>Dear ${user.first_name} ${user.last_name},</p>
        <p>Your account has been approved by an administrator.</p>
        <p>You can now log in to your account at our platform.</p>
        <p>Thank you for your patience!</p>
      `
    });

    res.json({
      success: true,
      message: 'User approved successfully'
    });

  } catch (error) {
    console.error('Error approving user:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Reject user (admin/superadmin only)
router.post('/:userId/reject', authenticateToken, requireAdminAccess, async (req, res) => {
  try {
    const { userId } = req.params;
    const { reason } = req.body;
    const { role, tenantId } = req.user;

    // Check if user exists and get their details
    let userQuery;
    let queryParams = [userId];

    if (role !== 'superadmin') {
      userQuery = `
        SELECT u.*, t.name as tenant_name 
        FROM users u 
        LEFT JOIN tenants t ON u.tenant_id = t.id 
        WHERE u.id = $1 AND u.tenant_id = $2
      `;
      queryParams = [userId, tenantId];
    } else {
      userQuery = `
        SELECT u.*, t.name as tenant_name 
        FROM users u 
        LEFT JOIN tenants t ON u.tenant_id = t.id 
        WHERE u.id = $1
      `;
    }

    const userResult = await query(userQuery, queryParams);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found or access denied'
      });
    }

    const user = userResult.rows[0];

    if (!user.requires_approval) {
      return res.status(400).json({
        success: false,
        message: 'User does not require approval'
      });
    }

    // Reject the user (deactivate)
    await query(
      'UPDATE users SET requires_approval = false, is_active = false WHERE id = $1',
      [userId]
    );

    // Send rejection email
    await sendEmail({
      to: user.email,
      subject: 'Account Application Status - SchoolAgenticAI',
      html: `
        <h2>Account Application Update</h2>
        <p>Dear ${user.first_name} ${user.last_name},</p>
        <p>We regret to inform you that your account application has not been approved.</p>
        ${reason ? `<p>Reason: ${reason}</p>` : ''}
        <p>If you believe this is an error, please contact your school administrator.</p>
      `
    });

    res.json({
      success: true,
      message: 'User rejected successfully'
    });

  } catch (error) {
    console.error('Error rejecting user:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Update user (admin/superadmin only)
router.put('/:userId', authenticateToken, requireAdminAccess, async (req, res) => {
  try {
    const { userId } = req.params;
    const { firstName, lastName, role, isActive } = req.body;
    const { role: currentUserRole, tenantId } = req.user;

    // Check if user exists and get their details
    let userQuery;
    let queryParams = [userId];

    if (currentUserRole !== 'superadmin') {
      userQuery = `
        SELECT u.*, t.name as tenant_name 
        FROM users u 
        LEFT JOIN tenants t ON u.tenant_id = t.id 
        WHERE u.id = $1 AND u.tenant_id = $2
      `;
      queryParams = [userId, tenantId];
    } else {
      userQuery = `
        SELECT u.*, t.name as tenant_name 
        FROM users u 
        LEFT JOIN tenants t ON u.tenant_id = t.id 
        WHERE u.id = $1
      `;
    }

    const userResult = await query(userQuery, queryParams);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found or access denied'
      });
    }

    const user = userResult.rows[0];

    // Only superadmin can change roles to admin/superadmin
    if (role && ['admin', 'superadmin'].includes(role) && currentUserRole !== 'superadmin') {
      return res.status(403).json({
        success: false,
        message: 'Only superadmin can assign admin roles'
      });
    }

    // Update user
    const updateQuery = `
      UPDATE users 
      SET first_name = COALESCE($1, first_name),
          last_name = COALESCE($2, last_name),
          role = COALESCE($3, role),
          is_active = COALESCE($4, is_active),
          updated_at = NOW()
      WHERE id = $5
      RETURNING *
    `;

    const result = await query(updateQuery, [
      firstName || user.first_name,
      lastName || user.last_name,
      role || user.role,
      isActive !== undefined ? isActive : user.is_active,
      userId
    ]);

    res.json({
      success: true,
      message: 'User updated successfully',
      user: result.rows[0]
    });

  } catch (error) {
    console.error('Error updating user:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Deactivate user (admin/superadmin only)
router.post('/:userId/deactivate', authenticateToken, requireAdminAccess, async (req, res) => {
  try {
    const { userId } = req.params;
    const { role, tenantId } = req.user;

    // Check if user exists and get their details
    let userQuery;
    let queryParams = [userId];

    if (role !== 'superadmin') {
      userQuery = `
        SELECT u.*, t.name as tenant_name 
        FROM users u 
        LEFT JOIN tenants t ON u.tenant_id = t.id 
        WHERE u.id = $1 AND u.tenant_id = $2
      `;
      queryParams = [userId, tenantId];
    } else {
      userQuery = `
        SELECT u.*, t.name as tenant_name 
        FROM users u 
        LEFT JOIN tenants t ON u.tenant_id = t.id 
        WHERE u.id = $1
      `;
    }

    const userResult = await query(userQuery, queryParams);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found or access denied'
      });
    }

    const user = userResult.rows[0];

    // Prevent deactivating superadmin
    if (user.role === 'superadmin') {
      return res.status(400).json({
        success: false,
        message: 'Cannot deactivate superadmin account'
      });
    }

    // Deactivate user
    await query(
      'UPDATE users SET is_active = false, updated_at = NOW() WHERE id = $1',
      [userId]
    );

    res.json({
      success: true,
      message: 'User deactivated successfully'
    });

  } catch (error) {
    console.error('Error deactivating user:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Reactivate user (admin/superadmin only)
router.post('/:userId/reactivate', authenticateToken, requireAdminAccess, async (req, res) => {
  try {
    const { userId } = req.params;
    const { role, tenantId } = req.user;

    // Check if user exists and get their details
    let userQuery;
    let queryParams = [userId];

    if (role !== 'superadmin') {
      userQuery = `
        SELECT u.*, t.name as tenant_name 
        FROM users u 
        LEFT JOIN tenants t ON u.tenant_id = t.id 
        WHERE u.id = $1 AND u.tenant_id = $2
      `;
      queryParams = [userId, tenantId];
    } else {
      userQuery = `
        SELECT u.*, t.name as tenant_name 
        FROM users u 
        LEFT JOIN tenants t ON u.tenant_id = t.id 
        WHERE u.id = $1
      `;
    }

    const userResult = await query(userQuery, queryParams);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found or access denied'
      });
    }

    // Reactivate user
    await query(
      'UPDATE users SET is_active = true, updated_at = NOW() WHERE id = $1',
      [userId]
    );

    res.json({
      success: true,
      message: 'User reactivated successfully'
    });

  } catch (error) {
    console.error('Error reactivating user:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// PUT /api/users/profile - Update user profile
router.put('/profile', authenticateToken, async (req, res) => {
  try {
    const { id: userId } = req.user;
    const { firstName, lastName, email, phone, address, bio } = req.body;

    // Validate required fields
    if (!firstName || !lastName || !email) {
      return res.status(400).json({
        success: false,
        message: 'First name, last name, and email are required'
      });
    }

    // Check if email is already taken by another user
    const emailCheckQuery = `
      SELECT id FROM users 
      WHERE email = $1 AND id != $2
    `;
    const emailCheckResult = await query(emailCheckQuery, [email, userId]);
    
    if (emailCheckResult.rows.length > 0) {
      return res.status(400).json({
        success: false,
        message: 'Email address is already in use'
      });
    }

    // Update user profile
    const updateQuery = `
      UPDATE users 
      SET 
        first_name = $1,
        last_name = $2,
        email = $3,
        phone = $4,
        address = $5,
        bio = $6,
        updated_at = NOW()
      WHERE id = $7
      RETURNING id, first_name, last_name, email, phone, address, bio, role, tenant_id
    `;

    const result = await query(updateQuery, [
      firstName, lastName, email, phone, address, bio, userId
    ]);

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    res.json({
      success: true,
      message: 'Profile updated successfully',
      user: result.rows[0]
    });

  } catch (error) {
    console.error('Profile update error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// PUT /api/users/password - Change user password
router.put('/password', authenticateToken, async (req, res) => {
  try {
    const { id: userId } = req.user;
    const { currentPassword, newPassword } = req.body;

    // Validate input
    if (!currentPassword || !newPassword) {
      return res.status(400).json({
        success: false,
        message: 'Current password and new password are required'
      });
    }

    if (newPassword.length < 6) {
      return res.status(400).json({
        success: false,
        message: 'New password must be at least 6 characters long'
      });
    }

    // Get current user to verify current password
    const userQuery = `
      SELECT password FROM users WHERE id = $1
    `;
    const userResult = await query(userQuery, [userId]);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    // Verify current password
    const bcrypt = require('bcryptjs');
    const isValidPassword = await bcrypt.compare(currentPassword, userResult.rows[0].password);
    
    if (!isValidPassword) {
      return res.status(400).json({
        success: false,
        message: 'Current password is incorrect'
      });
    }

    // Hash new password
    const saltRounds = 10;
    const hashedPassword = await bcrypt.hash(newPassword, saltRounds);

    // Update password
    const updateQuery = `
      UPDATE users 
      SET password = $1, updated_at = NOW()
      WHERE id = $2
    `;

    await query(updateQuery, [hashedPassword, userId]);

    res.json({
      success: true,
      message: 'Password changed successfully'
    });

  } catch (error) {
    console.error('Password change error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// DELETE /api/users/account - Delete user account
router.delete('/account', authenticateToken, async (req, res) => {
  try {
    const { id: userId } = req.user;
    const { password, reason } = req.body;

    // Validate input
    if (!password) {
      return res.status(400).json({
        success: false,
        message: 'Password is required to confirm account deletion'
      });
    }

    // Get current user to verify password
    const userQuery = `
      SELECT password, role FROM users WHERE id = $1
    `;
    const userResult = await query(userQuery, [userId]);

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    // Verify password
    const bcrypt = require('bcryptjs');
    const isValidPassword = await bcrypt.compare(password, userResult.rows[0].password);
    
    if (!isValidPassword) {
      return res.status(400).json({
        success: false,
        message: 'Password is incorrect'
      });
    }

    // Check if user has important roles that shouldn't be deleted
    const userRole = userResult.rows[0].role;
    if (userRole === 'superadmin') {
      return res.status(403).json({
        success: false,
        message: 'Super admin accounts cannot be deleted'
      });
    }

    // Log the deletion reason if provided
    if (reason) {
      const logQuery = `
        INSERT INTO user_deletion_logs (user_id, reason, deleted_at)
        VALUES ($1, $2, NOW())
      `;
      await query(logQuery, [userId, reason]);
    }

    // Start transaction for safe deletion
    await query('BEGIN');

    try {
      // Delete related records based on user role
      if (userRole === 'teacher') {
        // Remove teacher from classes
        await query(`
          UPDATE classes SET teacher_id = NULL WHERE teacher_id = $1
        `, [userId]);
        
        // Delete teacher-specific records
        await query(`
          DELETE FROM teacher_tasks WHERE teacher_id = $1
        `, [userId]);
      } else if (userRole === 'student') {
        // Delete student-specific records
        await query(`
          DELETE FROM students WHERE user_id = $1
        `, [userId]);
        
        await query(`
          DELETE FROM student_grades WHERE student_id = $1
        `, [userId]);
      } else if (userRole === 'parent') {
        // Delete parent-specific records
        await query(`
          DELETE FROM parent_students WHERE parent_id = $1
        `, [userId]);
      }

      // Delete attendance records
      await query(`
        DELETE FROM attendance_records WHERE student_id IN (
          SELECT id FROM students WHERE user_id = $1
        )
      `, [userId]);

      // Finally delete the user
      await query(`
        DELETE FROM users WHERE id = $1
      `, [userId]);

      await query('COMMIT');

      res.json({
        success: true,
        message: 'Account deleted successfully'
      });

    } catch (error) {
      await query('ROLLBACK');
      throw error;
    }

  } catch (error) {
    console.error('Account deletion error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Get current user info with tenant logo (for Teacher/Student dashboards)
router.get('/me', authenticateToken, async (req, res) => {
  try {
    const userId = req.user.id;
    const result = await query(`
      SELECT u.id, u.email, u.first_name, u.last_name, u.role, u.tenant_id,
             t.name as tenant_name, t.logo_url
      FROM users u
      LEFT JOIN tenants t ON u.tenant_id = t.id
      WHERE u.id = $1
    `, [userId]);

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    const user = result.rows[0];
    
    // Only include logo for teacher and student roles
    const responseData = {
      id: user.id,
      email: user.email,
      firstName: user.first_name,
      lastName: user.last_name,
      role: user.role,
      tenantId: user.tenant_id,
      tenantName: user.tenant_name
    };

    // Add logo only for teacher and student dashboards
    if (['teacher', 'student'].includes(user.role)) {
      responseData.logoUrl = user.logo_url;
    }

    res.json({
      success: true,
      user: responseData
    });
  } catch (error) {
    console.error('Get user info error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

module.exports = router; 