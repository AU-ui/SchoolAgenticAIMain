const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');

// Import database connection
const { query } = require('../../config/database');

// Import email service
const { sendEmail } = require('../../services/emailService');

// Utility function to normalize email addresses
const normalizeEmail = (email) => {
  if (!email) return email;
  
  // Convert to lowercase and trim whitespace
  let normalized = email.toLowerCase().trim();
  
  // Handle plus addressing - ensure plus sign is preserved
  // Gmail and many other providers support plus addressing (e.g., user+tag@gmail.com)
  // We should preserve the plus sign as it's a valid email feature
  
  // URL decode if the email was URL-encoded
  try {
    normalized = decodeURIComponent(normalized);
  } catch (e) {
    // If decodeURIComponent fails, use the original
    console.log('Email decode failed, using original:', normalized);
  }
  
  return normalized;
};

// Import simple auth service
const simpleAuthService = require('../../../services/simpleAuthService');

// LOGIN ENDPOINT - WITH REAL DATABASE
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({
        success: false,
        message: 'Email and password are required'
      });
    }

    // Use simple auth service
    const result = await simpleAuthService.login(email, password);

    if (result.success) {
      res.json(result);
    } else {
      res.status(401).json(result);
    }

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// SIGNUP ENDPOINT - WITH EMAIL SENDING
router.post('/signup', async (req, res) => {
  try {
    const { email, password, firstName, lastName, role, phoneNumber } = req.body;

    // Validate required fields
    if (!email || !password || !firstName || !lastName || !role) {
      return res.status(400).json({
        success: false,
        message: 'All required fields must be provided'
      });
    }

    // Use simple auth service
    const result = await simpleAuthService.signup({
      email,
      password,
      firstName,
      lastName,
      role,
      phoneNumber
    });

    if (result.success) {
      res.status(201).json(result);
    } else {
      res.status(400).json(result);
    }

  } catch (error) {
    console.error('Signup error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// EMAIL VERIFICATION ENDPOINT - SIMPLE
router.post('/verify-email', async (req, res) => {
  try {
    const { email } = req.body;
    console.log('�� EMAIL VERIFICATION REQUEST:', email);
    console.log('📧 EMAIL TYPE:', typeof email);
    console.log('📧 EMAIL LENGTH:', email ? email.length : 0);
    
    // Normalize email
    const normalizedEmail = normalizeEmail(email);
    console.log('📧 NORMALIZED EMAIL:', normalizedEmail);

    // Find user by email in database
    console.log('🔍 Searching for user with email:', normalizedEmail);
    const userResult = await query(
      'SELECT id, email_verified FROM users WHERE email = $1',
      [normalizedEmail]
    );
    const user = userResult.rows[0];
    console.log('🔍 Database query result:', user ? `Found user ID: ${user.id}` : 'No user found');
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }
    
    // Mark email as verified
    if (!user.email_verified) {
      await query(
        'UPDATE users SET email_verified = true WHERE id = $1',
        [user.id]
      );
      console.log('✅ EMAIL VERIFIED:', normalizedEmail);
    } else {
      console.log('✅ EMAIL ALREADY VERIFIED:', normalizedEmail);
    }
    
    res.json({
      success: true,
      message: 'Email verified successfully. You can now login.',
      user: {
        id: user.id,
        email: normalizedEmail,
        emailVerified: true
      }
    });
  } catch (error) {
    console.error('❌ VERIFICATION ERROR:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
});

// TOKEN REFRESH ENDPOINT
router.post('/refresh-token', async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken) {
      return res.status(400).json({
        success: false,
        message: 'Refresh token is required'
      });
    }

    // Use simple auth service for token refresh
    const result = await simpleAuthService.refreshAccessToken(refreshToken);

    if (result.success) {
      res.json({
        success: true,
        message: 'Token refreshed successfully',
        data: {
          accessToken: result.accessToken,
          user: result.user
        }
      });
    } else {
      res.status(401).json({
        success: false,
        message: result.message || 'Token refresh failed'
      });
    }

  } catch (error) {
    console.error('Token refresh error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// GET USER INFO ENDPOINT - WITH REAL JWT TOKENS
router.get('/me', (req, res) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'No token provided'
      });
    }

    // Verify JWT token
    const jwtSecret = process.env.JWT_SECRET || 'your-super-secret-jwt-key-here-make-it-long-and-random';
    const decoded = jwt.verify(token, jwtSecret);
    
    // Find user by ID from token
    const userResult = query(
      'SELECT id, first_name, last_name, email, role, tenant_id, email_verified, status FROM users WHERE id = $1',
      [decoded.userId]
    );
    const user = (userResult.rows[0]);
    
    if (!user) {
      return res.status(401).json({
        success: false,
        message: 'Invalid token'
      });
    }
    
    res.json({
      success: true,
      user: {
        id: user.id,
        name: `${user.first_name} ${user.last_name}`,
        firstName: user.first_name,
        lastName: user.last_name,
        email: user.email,
        role: user.role,
        tenantId: user.tenant_id,
        emailVerified: user.email_verified,
        status: user.status
      }
    });
  } catch (error) {
    console.error('❌ GET USER ERROR:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
});

// TEMPORARY: Reset database endpoint (remove after use)
router.post('/reset-database', async (req, res) => {
  try {
    // Delete all users
    const result = await query('DELETE FROM users');
    
    // Reset sequence
    await query('ALTER SEQUENCE users_id_seq RESTART WITH 1');
    
    res.json({
      success: true,
      message: `Database reset successful. Deleted ${result.rowCount} users.`
    });
  } catch (error) {
    console.error('Reset database error:', error);
    res.status(500).json({
      success: false,
      message: 'Database reset failed'
    });
  }
});

module.exports = router;