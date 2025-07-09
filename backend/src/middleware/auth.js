const jwt = require('jsonwebtoken');
const { query } = require('../config/database');

// Enhanced password validation for admin/superadmin
const validateAdminPassword = (password) => {
  const minLength = 12;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
  const noCommonPasswords = !['admin123', 'password', '123456', 'admin', 'superadmin'].includes(password.toLowerCase());
  
  return password.length >= minLength && 
         hasUpperCase && hasLowerCase && hasNumbers && 
         hasSpecialChar && noCommonPasswords;
};

// IP whitelist check (configurable via environment variables)
const isIPAllowed = (ip) => {
  const allowedIPs = process.env.ADMIN_ALLOWED_IPS ? 
    process.env.ADMIN_ALLOWED_IPS.split(',') : 
    ['127.0.0.1', '::1', 'localhost']; // Default to localhost
  
  return allowedIPs.includes(ip) || allowedIPs.includes('*'); // '*' allows all IPs
};

// Business hours check (configurable)
const isBusinessHours = () => {
  const now = new Date();
  const hour = now.getHours();
  const day = now.getDay(); // 0 = Sunday, 1 = Monday, etc.
  
  // Default: Monday-Friday, 8 AM - 6 PM
  const businessHoursEnabled = process.env.BUSINESS_HOURS_ENABLED === 'true';
  if (!businessHoursEnabled) return true;
  
  const startHour = parseInt(process.env.BUSINESS_START_HOUR) || 8;
  const endHour = parseInt(process.env.BUSINESS_END_HOUR) || 18;
  const workDays = process.env.BUSINESS_DAYS ? 
    process.env.BUSINESS_DAYS.split(',').map(d => parseInt(d)) : 
    [1, 2, 3, 4, 5]; // Monday-Friday
  
  return workDays.includes(day) && hour >= startHour && hour < endHour;
};

// Middleware to verify JWT token
const authenticateToken = async (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return res.status(401).json({ 
      success: false, 
      message: 'Access token required' 
    });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    
    // Get user from database to ensure they still exist and are active
    const userResult = await query(
      'SELECT id, email, role, tenant_id, is_active FROM users WHERE id = $1',
      [decoded.userId]
    );

    if (userResult.rows.length === 0) {
      return res.status(401).json({ 
        success: false, 
        message: 'User not found' 
      });
    }

    const user = userResult.rows[0];
    
    if (!user.is_active) {
      return res.status(401).json({ 
        success: false, 
        message: 'User account is deactivated' 
      });
    }

    // Add user info to request object
    req.user = {
      id: user.id,
      email: user.email,
      role: user.role,
      tenantId: user.tenant_id
    };

    next();
  } catch (error) {
    console.error('Token verification error:', error);
    return res.status(403).json({ 
      success: false, 
      message: 'Invalid or expired token' 
    });
  }
};

// Enhanced middleware for admin/superadmin routes
const requireAdminAccess = async (req, res, next) => {
  if (!req.user) {
    return res.status(401).json({ 
      success: false, 
      message: 'Authentication required' 
    });
  }

  const userRole = req.user.role;
  if (!['admin', 'superadmin'].includes(userRole)) {
    return res.status(403).json({ 
      success: false, 
      message: 'Admin access required' 
    });
  }

  // IP whitelist check
  const clientIP = req.ip || req.connection.remoteAddress;
  if (!isIPAllowed(clientIP)) {
    return res.status(403).json({ 
      success: false, 
      message: 'Access denied from this location' 
    });
  }

  // Business hours check
  if (!isBusinessHours()) {
    return res.status(403).json({ 
      success: false, 
      message: 'Admin access only during business hours' 
    });
  }

  next();
};

// Middleware to check if user has required role
const requireRole = (roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ 
        success: false, 
        message: 'Authentication required' 
      });
    }

    const userRole = req.user.role;
    const allowedRoles = Array.isArray(roles) ? roles : [roles];

    if (!allowedRoles.includes(userRole)) {
      return res.status(403).json({ 
        success: false, 
        message: 'Insufficient permissions' 
      });
    }

    next();
  };
};

// Middleware to ensure user belongs to the specified tenant
const requireTenantAccess = async (req, res, next) => {
  const { tenantId } = req.params;
  
  if (!req.user) {
    return res.status(401).json({ 
      success: false, 
      message: 'Authentication required' 
    });
  }

  // Superadmin can access all tenants
  if (req.user.role === 'superadmin') {
    return next();
  }

  // Check if user belongs to the specified tenant
  if (req.user.tenantId !== parseInt(tenantId)) {
    return res.status(403).json({ 
      success: false, 
      message: 'Access denied to this tenant' 
    });
  }

  next();
};

module.exports = {
  authenticateToken,
  requireRole,
  requireTenantAccess,
  requireAdminAccess,
  validateAdminPassword,
  isIPAllowed,
  isBusinessHours
}; 