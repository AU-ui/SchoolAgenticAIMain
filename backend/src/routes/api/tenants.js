const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const { query } = require('../../config/database');
const { 
  authenticateToken, 
  requireAdminAccess, 
  requireRole, 
  requireTenantAccess 
} = require('../../middleware/auth');

const router = express.Router();

// Configure multer for logo uploads
const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    const uploadDir = 'uploads/logos';
    // Create directory if it doesn't exist
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir, { recursive: true });
    }
    cb(null, uploadDir);
  },
  filename: function (req, file, cb) {
    // Generate unique filename with timestamp
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, 'logo-' + uniqueSuffix + path.extname(file.originalname));
  }
});

const upload = multer({
  storage: storage,
  limits: {
    fileSize: 5 * 1024 * 1024 // 5MB limit
  },
  fileFilter: function (req, file, cb) {
    // Check file type
    if (file.mimetype.startsWith('image/')) {
      cb(null, true);
    } else {
      cb(new Error('Only image files are allowed!'), false);
    }
  }
});

// Get all tenants (superadmin only)
router.get('/', authenticateToken, requireAdminAccess, async (req, res) => {
  try {
    const result = await query('SELECT * FROM tenants ORDER BY name');
    res.json({
      success: true,
      tenants: result.rows.map(tenant => ({
        ...tenant,
        logoUrl: tenant.logo_url // Expose in camelCase for frontend
      }))
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

    const tenant = result.rows[0];
    res.json({
      success: true,
      tenant: {
        ...tenant,
        logoUrl: tenant.logo_url // Expose in camelCase for frontend
      }
    });
  } catch (error) {
    console.error('Error fetching tenant:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Create new tenant or school with logo upload (superadmin only)
router.post('/', authenticateToken, requireAdminAccess, upload.single('logo'), async (req, res) => {
  try {
    const { name, domain, address, phone, email, tenantId, newTenantName } = req.body;
    let finalTenantId;
    let createdTenant = null;
    let logoUrl = null;

    // Handle logo upload
    if (req.file) {
      logoUrl = `/uploads/logos/${req.file.filename}`;
    }

    // 1. If newTenantName is provided, create a new tenant (group)
    if (newTenantName) {
      const tenantResult = await query(
        'INSERT INTO tenants (name, domain, logo_url) VALUES ($1, $2, $3) RETURNING *',
        [newTenantName, domain || null, logoUrl]
      );
      finalTenantId = tenantResult.rows[0].id;
      createdTenant = tenantResult.rows[0];
    } else if (tenantId) {
      // 2. If tenantId is provided, use existing tenant
      finalTenantId = tenantId;
      // Update existing tenant with logo if provided
      if (logoUrl) {
        await query(
          'UPDATE tenants SET logo_url = $1 WHERE id = $2',
          [logoUrl, tenantId]
        );
      }
    } else {
      // 3. Solo school: create a new tenant with the same name as the school
      const tenantResult = await query(
        'INSERT INTO tenants (name, domain, logo_url) VALUES ($1, $2, $3) RETURNING *',
        [name, domain || null, logoUrl]
      );
      finalTenantId = tenantResult.rows[0].id;
      createdTenant = tenantResult.rows[0];
    }

    // Create the school
    const schoolResult = await query(
      'INSERT INTO schools (tenant_id, name, address, phone, email) VALUES ($1, $2, $3, $4, $5) RETURNING *',
      [finalTenantId, name, address || null, phone || null, email || null]
    );

    res.status(201).json({
      success: true,
      tenant: createdTenant ? {
        ...createdTenant,
        logoUrl: createdTenant.logo_url
      } : null,
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

// Update tenant with logo (superadmin only)
router.put('/:tenantId', authenticateToken, requireAdminAccess, upload.single('logo'), async (req, res) => {
  try {
    const { tenantId } = req.params;
    const { name, domain, settings } = req.body;
    let logoUrl = null;

    // Handle logo upload
    if (req.file) {
      logoUrl = `/uploads/logos/${req.file.filename}`;
    }

    let updateQuery = 'UPDATE tenants SET name = $1, domain = $2, settings = $3';
    let params = [name, domain, settings];

    if (logoUrl) {
      updateQuery += ', logo_url = $4';
      params.push(logoUrl);
    }

    updateQuery += ' WHERE id = $' + (params.length + 1) + ' RETURNING *';
    params.push(tenantId);

    const result = await query(updateQuery, params);

    if (result.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'Tenant not found'
      });
    }

    const tenant = result.rows[0];
    res.json({
      success: true,
      tenant: {
        ...tenant,
        logoUrl: tenant.logo_url
      }
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