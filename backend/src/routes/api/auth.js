const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { query } = require('../../config/database');
const { sendEmail } = require('../../services/emailService');
const { 
  authenticateToken, 
  requireRole, 
  validateAdminPassword,
  requireAdminAccess 
} = require('../../middleware/auth');
const crypto = require('crypto');

const router = express.Router();

// Rate limiting for login attempts
const loginAttempts = new Map();
const MAX_LOGIN_ATTEMPTS = 5;
const LOCKOUT_DURATION = 15 * 60 * 1000; // 15 minutes

const checkRateLimit = (email) => {
  const attempts = loginAttempts.get(email);
  if (!attempts) return true;
  
  if (attempts.count >= MAX_LOGIN_ATTEMPTS) {
    if (Date.now() - attempts.timestamp < LOCKOUT_DURATION) {
      return false;
    } else {
      loginAttempts.delete(email);
      return true;
    }
  }
  return true;
};

const recordLoginAttempt = (email, success) => {
  if (success) {
    loginAttempts.delete(email);
    return;
  }
  
  const attempts = loginAttempts.get(email) || { count: 0, timestamp: Date.now() };
  attempts.count++;
  attempts.timestamp = Date.now();
  loginAttempts.set(email, attempts);
};

// In-memory store for reset tokens (replace with DB in production)
const passwordResetTokens = new Map();
const PASSWORD_RESET_TOKEN_EXPIRY = 1000 * 60 * 15; // 15 minutes
const MAX_RESET_ATTEMPTS = 5;
const resetAttempts = new Map();

// Enhanced account lockout system
const accountLockout = new Map();
const ACCOUNT_LOCKOUT_DURATION = 30 * 60 * 1000; // 30 minutes

const checkAccountLockout = (email) => {
  const lockout = accountLockout.get(email);
  if (lockout && Date.now() < lockout.until) {
    return false;
  }
  return true;
};

const setAccountLockout = (email) => {
  accountLockout.set(email, {
    until: Date.now() + ACCOUNT_LOCKOUT_DURATION,
    attempts: 0
  });
};

const clearAccountLockout = (email) => {
  accountLockout.delete(email);
};

// Helper: Validate strong password
function isStrongPassword(password) {
  return typeof password === 'string' && password.length >= 8 && /[A-Z]/.test(password) && /[a-z]/.test(password) && /[0-9]/.test(password);
}

// Request password reset (ALL ROLES - enhanced security)
router.post('/request-password-reset', async (req, res) => {
  const { email } = req.body;
  if (!email) return res.status(400).json({ success: false, message: 'Email required.' });

  // Rate limit
  const attempts = resetAttempts.get(email) || { count: 0, timestamp: Date.now() };
  if (attempts.count >= MAX_RESET_ATTEMPTS && Date.now() - attempts.timestamp < 15 * 60 * 1000) {
    return res.status(429).json({ success: false, message: 'Too many reset attempts. Try again later.' });
  }

  try {
    const userResult = await query('SELECT id, email, role, first_name FROM users WHERE email = $1', [email]);
    if (userResult.rows.length === 0) {
      // Always respond with success to avoid user enumeration
      return res.json({ success: true, message: 'If your account is eligible, a reset link will be sent.' });
    }
    const user = userResult.rows[0];
    
    // Allow password reset for ALL roles
    // Generate token
    const token = crypto.randomBytes(32).toString('hex');
    const expires = Date.now() + PASSWORD_RESET_TOKEN_EXPIRY;
    passwordResetTokens.set(token, { userId: user.id, email: user.email, expires });
    
    // Send email
    const resetUrl = `${process.env.FRONTEND_URL || 'http://localhost:3000'}/reset-password?token=${token}`;
    await sendEmail(user.email, 'custom', {
      subject: 'Password Reset Request - EdTech Platform',
      html: `<p>Hello ${user.first_name || user.email},</p><p>You requested a password reset. <a href="${resetUrl}">Click here to reset your password</a>. This link expires in 15 minutes.</p>`,
      text: `Hello ${user.first_name || user.email},\nYou requested a password reset. Use this link: ${resetUrl} (expires in 15 minutes).`
    });
    
    // Log attempt
    resetAttempts.set(email, { count: attempts.count + 1, timestamp: Date.now() });
    console.log(`[AUDIT] Password reset requested for ${email} (role: ${user.role})`);
    return res.json({ success: true, message: 'If your account is eligible, a reset link will be sent.' });
  } catch (err) {
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// Reset password (ALL ROLES - enhanced security)
router.post('/reset-password', async (req, res) => {
  const { token, newPassword } = req.body;
  if (!token || !newPassword) return res.status(400).json({ success: false, message: 'Token and new password required.' });
  
  // Enhanced password validation for admin/superadmin
  const tokenData = passwordResetTokens.get(token);
  if (!tokenData || Date.now() > tokenData.expires) {
    return res.status(400).json({ success: false, message: 'Invalid or expired token.' });
  }
  
  try {
    const userResult = await query('SELECT id, role FROM users WHERE id = $1', [tokenData.userId]);
    if (userResult.rows.length === 0) {
      return res.status(400).json({ success: false, message: 'Invalid token.' });
    }
    const user = userResult.rows[0];
    
    // Enhanced password validation based on role
    if (['admin', 'superadmin'].includes(user.role)) {
      if (!validateAdminPassword(newPassword)) {
        return res.status(400).json({
          success: false,
          message: 'Password must be at least 12 characters long and contain uppercase, lowercase, numbers, and special characters'
        });
      }
    } else {
      // Basic password validation for other roles
      if (!isStrongPassword(newPassword)) {
        return res.status(400).json({
          success: false,
          message: 'Password must be at least 8 characters, include uppercase, lowercase, and a number.'
        });
      }
    }
    
    const hashed = await bcrypt.hash(newPassword, 12);
    await query('UPDATE users SET password = $1 WHERE id = $2', [hashed, user.id]);
    passwordResetTokens.delete(token);
    console.log(`[AUDIT] Password reset completed for user ${user.id} (role: ${user.role})`);
    return res.json({ success: true, message: 'Password has been reset.' });
  } catch (err) {
    return res.status(500).json({ success: false, message: 'Server error.' });
  }
});

// Token refresh endpoint
router.post('/refresh-token', authenticateToken, async (req, res) => {
  try {
    const newToken = jwt.sign(
      { userId: req.user.id },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );
    
    res.json({
      success: true,
      token: newToken
    });
  } catch (error) {
    console.error('Token refresh error:', error);
    res.status(500).json({
      success: false,
      message: 'Token refresh failed'
    });
  }
});

// Enhanced login with account lockout
router.post('/login', async (req, res) => {
  try {
    const { email, password, step, verificationCode } = req.body;

    // Check account lockout first
    if (!checkAccountLockout(email)) {
      return res.status(429).json({
        success: false,
        message: 'Account temporarily locked due to too many failed attempts. Please try again later.'
      });
    }

    // Rate limiting check
    if (!checkRateLimit(email)) {
      return res.status(429).json({
        success: false,
        message: 'Too many login attempts. Please try again in 15 minutes.'
      });
    }

    if (step === 'verify') {
      // Step 2: Verify email code
      const userResult = await query(
        'SELECT id, email, role, tenant_id, verification_code, verification_expires FROM users WHERE email = $1',
        [email]
      );

      if (userResult.rows.length === 0) {
        return res.status(401).json({
          success: false,
          message: 'Invalid verification attempt'
        });
      }

      const user = userResult.rows[0];
      
      if (user.verification_code !== verificationCode || 
          new Date() > new Date(user.verification_expires)) {
        recordLoginAttempt(email, false);
        return res.status(401).json({
          success: false,
          message: 'Invalid or expired verification code'
        });
      }

      // Clear verification code and account lockout
      await query(
        'UPDATE users SET verification_code = NULL, verification_expires = NULL WHERE id = $1',
        [user.id]
      );
      clearAccountLockout(email);

      // Generate JWT token
      const token = jwt.sign(
        { userId: user.id },
        process.env.JWT_SECRET,
        { expiresIn: '24h' }
      );

      recordLoginAttempt(email, true);
      
      return res.json({
        success: true,
        message: 'Login successful',
        token,
        user: {
          id: user.id,
          email: user.email,
          role: user.role,
          tenantId: user.tenant_id
        }
      });
    }

    // Step 1: Verify credentials and send verification code
    const userResult = await query(
      'SELECT id, email, password, role, tenant_id, is_active, email_verified FROM users WHERE email = $1',
      [email]
    );

    if (userResult.rows.length === 0) {
      recordLoginAttempt(email, false);
      setAccountLockout(email);
      return res.status(401).json({
        success: false,
        message: 'Invalid credentials'
      });
    }

    const user = userResult.rows[0];

    if (!user.is_active) {
      recordLoginAttempt(email, false);
      setAccountLockout(email);
      return res.status(401).json({
        success: false,
        message: 'Account is deactivated'
      });
    }

    const isValidPassword = await bcrypt.compare(password, user.password);
    if (!isValidPassword) {
      recordLoginAttempt(email, false);
      setAccountLockout(email);
      return res.status(401).json({
        success: false,
        message: 'Invalid credentials'
      });
    }

    // Clear account lockout on successful password verification
    clearAccountLockout(email);

    // Development mode: Skip email verification if email service is not configured
    const isDevelopmentMode = process.env.NODE_ENV === 'development' && !process.env.EMAIL_HOST;
    
    if (isDevelopmentMode) {
      // Generate JWT token directly without email verification
      const token = jwt.sign(
        { userId: user.id },
        process.env.JWT_SECRET,
        { expiresIn: '24h' }
      );

      recordLoginAttempt(email, true);
      
      return res.json({
        success: true,
        message: 'Login successful (Development Mode - Email verification bypassed)',
        token,
        user: {
          id: user.id,
          email: user.email,
          role: user.role,
          tenantId: user.tenant_id
        }
      });
    }

    // Check if email is verified
    if (!user.email_verified) {
      // Generate verification code for multi-step auth
      const loginVerificationCode = Math.floor(100000 + Math.random() * 900000).toString();
      const loginExpiresAt = new Date(Date.now() + 10 * 60 * 1000); // 10 minutes

      await query(
        'UPDATE users SET verification_code = $1, verification_expires = $2 WHERE id = $3',
        [loginVerificationCode, loginExpiresAt, user.id]
      );

      // Send verification email
      await sendEmail(user.email, 'verification', {
        userName: user.first_name || user.email.split('@')[0],
        code: loginVerificationCode
      });

      recordLoginAttempt(email, true);

      return res.json({
        success: true,
        message: 'Verification code sent to your email',
        requiresVerification: true
      });
    }

    // Email is verified, allow login
    const token = jwt.sign(
      { userId: user.id },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );

    recordLoginAttempt(email, true);

    return res.json({
      success: true,
      message: 'Login successful',
      token,
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
        tenantId: user.tenant_id
      }
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Enhanced signup with complex password validation
router.post('/signup', async (req, res) => {
  try {
    const { email, password, role, schoolCode, firstName, lastName, tenantId } = req.body;

    // Validate school code if provided
    if (schoolCode) {
      const schoolCodeResult = await query(
        'SELECT tenant_id, max_uses, current_uses, expires_at FROM school_codes WHERE code = $1 AND is_active = true',
        [schoolCode]
      );

      if (schoolCodeResult.rows.length === 0) {
        return res.status(400).json({
          success: false,
          message: 'Invalid school code'
        });
      }

      const codeData = schoolCodeResult.rows[0];
      
      if (codeData.current_uses >= codeData.max_uses) {
        return res.status(400).json({
          success: false,
          message: 'School code usage limit reached'
        });
      }

      if (codeData.expires_at && new Date() > new Date(codeData.expires_at)) {
        return res.status(400).json({
          success: false,
          message: 'School code has expired'
        });
      }
    }

    // Enhanced password validation for admin/superadmin
    if (['admin', 'superadmin'].includes(role)) {
      if (!validateAdminPassword(password)) {
        return res.status(400).json({
          success: false,
          message: 'Password must be at least 12 characters long and contain uppercase, lowercase, numbers, and special characters'
        });
      }
    } else {
      // Basic password validation for other roles
      if (password.length < 8) {
        return res.status(400).json({
          success: false,
          message: 'Password must be at least 8 characters long'
        });
      }
    }

    // Check if user already exists
    const existingUser = await query(
      'SELECT id FROM users WHERE email = $1',
      [email]
    );

    if (existingUser.rows.length > 0) {
      return res.status(400).json({
        success: false,
        message: 'User already exists'
      });
    }

    // Hash password
    const hashedPassword = await bcrypt.hash(password, 12);

    // Determine tenant ID
    let finalTenantId = null;
    if (schoolCode) {
      const schoolCodeResult = await query(
        'SELECT tenant_id FROM school_codes WHERE code = $1',
        [schoolCode]
      );
      finalTenantId = schoolCodeResult.rows[0].tenant_id;
    } else if (tenantId) {
      // Validate that the tenant exists
      const tenantResult = await query(
        'SELECT id FROM tenants WHERE id = $1',
        [parseInt(tenantId)]
      );
      
      if (tenantResult.rows.length === 0) {
        return res.status(400).json({
          success: false,
          message: 'Invalid school/organization selected'
        });
      }
      
      finalTenantId = parseInt(tenantId);
    } else if (role === 'superadmin') {
      finalTenantId = null; // Superadmin doesn't belong to any tenant
    }

    // Create user
    const newUser = await query(
      `INSERT INTO users (email, password, role, tenant_id, first_name, last_name, is_active, email_verified, requires_approval) 
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) RETURNING id, email, role, tenant_id`,
      [email, hashedPassword, role, finalTenantId, firstName, lastName, true, false, role === 'superadmin' ? false : true]
    );

    // Update school code usage if applicable
    if (schoolCode) {
      await query(
        'UPDATE school_codes SET current_uses = current_uses + 1 WHERE code = $1',
        [schoolCode]
      );
    }

    // Send email verification for new user registration
    const signupVerificationCode = Math.floor(100000 + Math.random() * 900000).toString();
    const signupExpiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24 hours

    await query(
      'UPDATE users SET verification_code = $1, verification_expires = $2 WHERE id = $3',
      [signupVerificationCode, signupExpiresAt, newUser.rows[0].id]
    );

    // Send verification email
    await sendEmail(email, 'verification', {
      userName: firstName || email.split('@')[0],
      code: signupVerificationCode
    });

    res.status(201).json({
      success: true,
      message: 'User created successfully. Please check your email for verification.',
      requiresVerification: true,
      verificationCode: signupVerificationCode
    });

  } catch (error) {
    console.error('Signup error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Verify email endpoint
router.post('/verify-email', async (req, res) => {
  try {
    const { email, verificationCode } = req.body;

    const userResult = await query(
      'SELECT id, verification_code, verification_expires FROM users WHERE email = $1',
      [email]
    );

    if (userResult.rows.length === 0) {
      console.log(`[VERIFY-EMAIL] User not found for email: ${email}`);
      return res.status(400).json({
        success: false,
        message: 'User not found'
      });
    }

    const user = userResult.rows[0];
    console.log(`[VERIFY-EMAIL] Attempting verification for user ID: ${user.id}, email: ${email}`);

    if (user.verification_code !== verificationCode) {
      console.log(`[VERIFY-EMAIL] Invalid code for user ID: ${user.id}, email: ${email}`);
      return res.status(400).json({
        success: false,
        message: 'Invalid verification code'
      });
    }

    if (new Date() > new Date(user.verification_expires)) {
      console.log(`[VERIFY-EMAIL] Code expired for user ID: ${user.id}, email: ${email}`);
      return res.status(400).json({
        success: false,
        message: 'Verification code has expired'
      });
    }

    // Mark email as verified and clear verification code
    const updateResult = await query(
      'UPDATE users SET email_verified = true, verification_code = NULL, verification_expires = NULL WHERE id = $1',
      [user.id]
    );
    console.log(`[VERIFY-EMAIL] Updated user ID: ${user.id}, email_verified set to true. Update result:`, updateResult.rowCount);

    // Double-check that email_verified is now true
    const verifyCheck = await query('SELECT email_verified FROM users WHERE id = $1', [user.id]);
    if (!verifyCheck.rows[0] || verifyCheck.rows[0].email_verified !== true) {
      console.warn(`[VERIFY-EMAIL] Verification update failed for user ID: ${user.id}, email: ${email}`);
      return res.status(500).json({
        success: false,
        message: 'Verification failed. Please try again or contact support.'
      });
    }

    res.json({
      success: true,
      message: 'Email verified successfully'
    });

  } catch (error) {
    console.error('Email verification error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Get current user info
router.get('/me', authenticateToken, async (req, res) => {
  try {
    const userResult = await query(
      'SELECT id, email, role, tenant_id, first_name, last_name, email_verified FROM users WHERE id = $1',
      [req.user.id]
    );

    if (userResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }

    const user = userResult.rows[0];

    res.json({
      success: true,
      user: {
        id: user.id,
        email: user.email,
        role: user.role,
        tenantId: user.tenant_id,
        firstName: user.first_name,
        lastName: user.last_name,
        emailVerified: user.email_verified
      }
    });

  } catch (error) {
    console.error('Get user error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// Logout endpoint (client-side token removal)
router.post('/logout', authenticateToken, (req, res) => {
  res.json({
    success: true,
    message: 'Logged out successfully'
  });
});

// Check if email is eligible for password reset (ALL ROLES)
router.get('/is-admin-email', async (req, res) => {
  const { email } = req.query;
  if (!email) return res.json({ eligible: false });
  try {
    const userResult = await query('SELECT role FROM users WHERE email = $1', [email]);
    if (userResult.rows.length > 0) {
      // All roles are now eligible for password reset
      return res.json({ eligible: true });
    }
    return res.json({ eligible: false });
  } catch {
    return res.json({ eligible: false });
  }
});

module.exports = router;