const express = require('express');
const { query } = require('../../config/database');
const { 
  authenticateToken, 
  requireAdminAccess, 
  requireRole, 
  requireTenantAccess 
} = require('../../middleware/auth');

const router = express.Router();

// Get all tenants (superadmin only)
router.get('/', authenticateToken, requireAdminAccess, async (req, res) => {
  try {
    const result = await query('SELECT * FROM tenants ORDER BY name');
    res.json({
      success: true,
      tenants: result.rows
    });
  } catch (error) {
    console.error('Error fetching tenants:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Get specific tenant
router.get('/:tenantId', authenticateToken, requireTenantAccess, async (req, res) => {
  try {
    const { tenantId } = req.params;
    const result = await query('SELECT * FROM tenants WHERE id = $1', [tenantId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Tenant not found'
      });
    }

    res.json({
      success: true,
      tenant: result.rows[0]
    });
  } catch (error) {
    console.error('Error fetching tenant:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Create new tenant (superadmin only)
router.post('/', authenticateToken, requireAdminAccess, async (req, res) => {
  try {
    const { name, domain, settings } = req.body;
    
    if (!name) {
      return res.status(400).json({
        success: false,
        message: 'Tenant name is required'
      });
    }

    const result = await query(
      'INSERT INTO tenants (name, domain, settings) VALUES ($1, $2, $3) RETURNING *',
      [name, domain, settings || {}]
    );

    res.status(201).json({
      success: true,
      tenant: result.rows[0]
    });
  } catch (error) {
    console.error('Error creating tenant:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Update tenant (superadmin only)
router.put('/:tenantId', authenticateToken, requireAdminAccess, async (req, res) => {
  try {
    const { tenantId } = req.params;
    const { name, domain, settings } = req.body;

    const result = await query(
      'UPDATE tenants SET name = $1, domain = $2, settings = $3 WHERE id = $4 RETURNING *',
      [name, domain, settings, tenantId]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Tenant not found'
      });
    }

    res.json({
      success: true,
      tenant: result.rows[0]
    });
  } catch (error) {
    console.error('Error updating tenant:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Delete tenant (superadmin only)
router.delete('/:tenantId', authenticateToken, requireAdminAccess, async (req, res) => {
  try {
    const { tenantId } = req.params;
    
    // Check if tenant has users
    const usersResult = await query('SELECT COUNT(*) FROM users WHERE tenant_id = $1', [tenantId]);
    if (parseInt(usersResult.rows[0].count) > 0) {
      return res.status(400).json({
        success: false,
        message: 'Cannot delete tenant with existing users'
      });
    }

    const result = await query('DELETE FROM tenants WHERE id = $1 RETURNING *', [tenantId]);
    
    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Tenant not found'
      });
    }

    res.json({
      success: true,
      message: 'Tenant deleted successfully'
    });
  } catch (error) {
    console.error('Error deleting tenant:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Get users for a specific tenant
router.get('/:tenantId/users', authenticateToken, requireTenantAccess, async (req, res) => {
  try {
    const { tenantId } = req.params;
    const result = await query(
      'SELECT id, email, role, first_name, last_name, is_active, email_verified, requires_approval FROM users WHERE tenant_id = $1 ORDER BY created_at DESC',
      [tenantId]
    );

    res.json({
      success: true,
      users: result.rows
    });
  } catch (error) {
    console.error('Error fetching tenant users:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

module.exports = router; 