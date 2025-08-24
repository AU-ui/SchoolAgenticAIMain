// ============================================================================
// SIMPLE AUTHENTICATION SERVICE WITH EMAIL VERIFICATION
// ============================================================================

const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { pool } = require('../src/config/database');
const { sendVerificationEmail } = require('../src/services/emailService');

class SimpleAuthService {
  constructor() {
    this.JWT_SECRET = process.env.JWT_SECRET || 'smart-attendance-secret-key-2024';
    this.ACCESS_TOKEN_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '1h';
    this.REFRESH_TOKEN_EXPIRES_IN = '7d';
  }

  // Generate access token (short-lived)
  generateAccessToken(user) {
    return jwt.sign(
      { 
        id: user.id, 
        email: user.email, 
        role: user.role,
        type: 'access'
      },
      this.JWT_SECRET,
      { expiresIn: this.ACCESS_TOKEN_EXPIRES_IN }
    );
  }

  // Generate refresh token (long-lived)
  generateRefreshToken(user) {
    return jwt.sign(
      { 
        id: user.id, 
        email: user.email,
        type: 'refresh'
      },
      this.JWT_SECRET,
      { expiresIn: this.REFRESH_TOKEN_EXPIRES_IN }
    );
  }

  // Generate both tokens
  generateTokens(user) {
    return {
      accessToken: this.generateAccessToken(user),
      refreshToken: this.generateRefreshToken(user)
    };
  }

  // Verify JWT token
  verifyToken(token) {
    try {
      return jwt.verify(token, this.JWT_SECRET);
    } catch (error) {
      return null;
    }
  }

  // Refresh access token using refresh token
  async refreshAccessToken(refreshToken) {
    try {
      const decoded = this.verifyToken(refreshToken);
      
      if (!decoded || decoded.type !== 'refresh') {
        throw new Error('Invalid refresh token');
      }

      // Get user from database
      const result = await pool.query(
        'SELECT id, email, first_name, last_name, role FROM users WHERE id = $1',
        [decoded.id]
      );

      if (result.rows.length === 0) {
        throw new Error('User not found');
      }

      const user = result.rows[0];
      const newAccessToken = this.generateAccessToken(user);

      return {
        success: true,
        accessToken: newAccessToken,
        user: {
          id: user.id,
          email: user.email,
          firstName: user.first_name,
          lastName: user.last_name,
          role: user.role
        }
      };

    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  }

  // Signup with email verification
  async signup(userData) {
    try {
      const { email, password, firstName, lastName, role, phoneNumber } = userData;
      
      // Check if user already exists
      const existingUser = await pool.query(
        'SELECT id FROM users WHERE email = $1',
        [email]
      );

      if (existingUser.rows.length > 0) {
        throw new Error('User already exists');
      }

      // Hash password
      const hashedPassword = await bcrypt.hash(password, 10);

      // Create user with email_verified = false
      const result = await pool.query(
        `INSERT INTO users (email, password, first_name, last_name, role, phone, email_verified) 
         VALUES ($1, $2, $3, $4, $5, $6, false) 
         RETURNING id, email, first_name, last_name, role`,
        [email, hashedPassword, firstName, lastName, role, phoneNumber || null]
      );

      const user = result.rows[0];

      // Send verification email
      const frontendUrl = process.env.FRONTEND_URL || 'http://localhost:3000';
      const verificationLink = `${frontendUrl}/verify-email?email=${encodeURIComponent(email)}`;
      
      console.log('📧 Sending verification email to:', email);
      const emailResult = await sendVerificationEmail(
        email, 
        `${firstName} ${lastName}`, 
        verificationLink
      );

      if (!emailResult.success) {
        console.error('❌ Failed to send verification email:', emailResult.error);
        // Still create user but log the email failure
      } else {
        console.log('✅ Verification email sent successfully');
      }

      return {
        success: true,
        message: 'Account created successfully! Please check your email for verification link.',
        user: {
          id: user.id,
          email: user.email,
          firstName: user.first_name,
          lastName: user.last_name,
          role: user.role,
          emailVerified: false
        },
        requiresVerification: true
      };

    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  }

  // Login with email verification check
  async login(email, password) {
    try {
      // Find user
      const result = await pool.query(
        'SELECT * FROM users WHERE email = $1',
        [email]
      );

      if (result.rows.length === 0) {
        throw new Error('Invalid credentials');
      }

      const user = result.rows[0];

      // Check password
      const isValidPassword = await bcrypt.compare(password, user.password);
      if (!isValidPassword) {
        throw new Error('Invalid credentials');
      }

      // Check if email is verified
      if (!user.email_verified) {
        throw new Error('Please verify your email before logging in. Check your inbox for the verification link.');
      }

      // Generate token (using the old format)
      const token = jwt.sign(
        { 
          id: user.id, 
          email: user.email, 
          role: user.role 
        },
        this.JWT_SECRET,
        { expiresIn: '24h' }
      );

      return {
        success: true,
        message: 'Login successful',
        user: {
          id: user.id,
          email: user.email,
          firstName: user.first_name,
          lastName: user.last_name,
          role: user.role,
          emailVerified: user.email_verified
        },
        token: token
      };

    } catch (error) {
      return {
        success: false,
        message: error.message
      };
    }
  }
}

module.exports = new SimpleAuthService();
