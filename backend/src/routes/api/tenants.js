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

// Create new tenant or school (superadmin only)
router.post('/', authenticateToken, requireAdminAccess, async (req, res) => {
  try {
    const { name, domain, address, phone, email, tenantId, newTenantName } = req.body;
    let finalTenantId;
    let createdTenant = null;

    // 1. If newTenantName is provided, create a new tenant (group)
    if (newTenantName) {
      const tenantResult = await query(
        'INSERT INTO tenants (name, domain) VALUES ($1, $2) RETURNING *',
        [newTenantName, domain || null]
      );
      finalTenantId = tenantResult.rows[0].id;
      createdTenant = tenantResult.rows[0];
    } else if (tenantId) {
      // 2. If tenantId is provided, use existing tenant
      finalTenantId = tenantId;
    } else {
      // 3. Solo school: create a new tenant with the same name as the school
      const tenantResult = await query(
        'INSERT INTO tenants (name, domain) VALUES ($1, $2) RETURNING *',
        [name, domain || null]
      );
      finalTenantId = tenantResult.rows[0].id;
      createdTenant = tenantResult.rows[0];
    }

    // Always create a new school under the determined tenant
    const schoolResult = await query(
      'INSERT INTO schools (tenant_id, name, address, phone, email) VALUES ($1, $2, $3, $4, $5) RETURNING *',
      [finalTenantId, name, address || null, phone || null, email || null]
    );

    res.status(201).json({
      success: true,
      tenant: createdTenant,
      school: schoolResult.rows[0]
    });
  } catch (error) {
    console.error('Error creating tenant/school:', error);
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