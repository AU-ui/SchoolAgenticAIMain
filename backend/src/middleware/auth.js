const jwt = require('jsonwebtoken');
const simpleAuthService = require('../../services/simpleAuthService');

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
  try {
    const authHeader = req.headers['authorization'];
    console.log('Auth header:', authHeader); // Debug log
    
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN
    console.log('Extracted token:', token ? token.substring(0, 20) + '...' : 'No token'); // Debug log

    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'Access token required'
      });
    }

    // Verify token using simpleAuthService
    const decoded = simpleAuthService.verifyToken(token);
    console.log('Decoded token:', decoded); // Debug log
    
    if (!decoded) {
      return res.status(401).json({
        success: false,
        message: 'Invalid or expired token',
        code: 'TOKEN_EXPIRED'
      });
    }

    // Add user info to request
    req.user = {
      id: decoded.id,
      email: decoded.email,
      role: decoded.role
    };

    console.log('User authenticated:', req.user); // Debug log
    next();
  } catch (error) {
    console.error('Token verification error:', error);
    
    if (error.name === 'TokenExpiredError') {
      return res.status(401).json({
        success: false,
        message: 'Token expired',
        code: 'TOKEN_EXPIRED'
      });
    }
    
    res.status(401).json({
      success: false,
      message: 'Invalid token'
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