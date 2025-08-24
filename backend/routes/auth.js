const express = require('express');
const router = express.Router();
const jwt = require('jsonwebtoken');

// Mock user data with email verification status
const users = [
  { id: 1, email: 'teacher@school.com', password: 'password123', role: 'teacher', name: 'John Teacher', firstName: 'John', emailVerified: true, tenantName: 'School AgenticAI' },
  { id: 2, email: 'student@school.com', password: 'password123', role: 'student', name: 'Jane Student', firstName: 'Jane', emailVerified: true, tenantName: 'School AgenticAI' },
  { id: 3, email: 'parent@school.com', password: 'password123', role: 'parent', name: 'Mike Parent', firstName: 'Mike', emailVerified: true, tenantName: 'School AgenticAI' },
  { id: 4, email: 'admin@school.com', password: 'password123', role: 'admin', name: 'Sarah Admin', firstName: 'Sarah', emailVerified: true, tenantName: 'School AgenticAI' }
];

// LOGIN ENDPOINT - FIXED WITH REAL JWT
router.post('/login', (req, res) => {
  try {
    const { email, password } = req.body;
    console.log(' LOGIN ATTEMPT:', { email, password });
    
    // Find user by email
    const user = users.find(u => u.email === email);
    console.log(' FOUND USER:', user ? user.email : 'NOT FOUND');
    
    if (!user) {
      console.log('❌ USER NOT FOUND');
      return res.status(401).json({
        success: false,
        message: 'Invalid email or password'
      });
    }
    
    // Check password
    if (user.password !== password) {
      console.log('❌ PASSWORD MISMATCH');
      return res.status(401).json({
        success: false,
        message: 'Invalid email or password'
      });
    }
    
    // Check if email is verified
    if (!user.emailVerified) {
      console.log('❌ EMAIL NOT VERIFIED');
      return res.status(401).json({
        success: false,
        message: 'Please verify your email before logging in'
      });
    }
    
    // Generate real JWT token
    const jwtSecret = process.env.JWT_SECRET || 'your-super-secret-jwt-key-here-make-it-long-and-random';
    const token = jwt.sign(
      { 
        userId: user.id, 
        email: user.email, 
        role: user.role,
        tenantId: 1 // Mock tenant ID
      }, 
      jwtSecret, 
      { expiresIn: process.env.JWT_EXPIRES_IN || '24h' }
    );
    
    console.log('✅ LOGIN SUCCESSFUL:', user.email, 'Role:', user.role);
    
    // Return successful login response
    res.json({
      success: true,
      token: token,
      user: {
        id: user.id,
        name: user.name,
        firstName: user.firstName,
        email: user.email,
        role: user.role,
        tenantName: user.tenantName,
        emailVerified: user.emailVerified
      }
    });
    
  } catch (error) {
    console.error('❌ LOGIN ERROR:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
});

// SIGNUP ENDPOINT
router.post('/signup', (req, res) => {
  try {
    const { firstName, lastName, email, phoneNumber, password, role } = req.body;
    console.log('📝 SIGNUP ATTEMPT:', { firstName, lastName, email, phoneNumber, role });
    
    // Check if email already exists
    const existingUser = users.find(u => u.email === email);
    if (existingUser) {
      return res.status(400).json({
        success: false,
        message: 'Email already registered'
      });
    }
    
    // Create new user (email not verified yet)
    const newUser = {
      id: Date.now(),
      firstName,
      lastName,
      email,
      phoneNumber,
      password,
      role: role || 'teacher',
      name: `${firstName} ${lastName}`,
      emailVerified: false,
      tenantName: 'School AgenticAI'
    };
    
    // Add to users array
    users.push(newUser);
    
    console.log('✅ USER CREATED:', newUser.email, 'Verification required');
    
    res.json({
      success: true,
      message: 'Account created successfully. Please check your email to verify your account.',
      user: {
        id: newUser.id,
        email: newUser.email,
        emailVerified: false
      }
    });
  } catch (error) {
    console.error('❌ SIGNUP ERROR:', error);
    res.status(500).json({
      success: false,
      message: 'Server error'
    });
  }
});

// EMAIL VERIFICATION ENDPOINT
router.post('/verify-email', (req, res) => {
  try {
    const { email } = req.body;
    console.log(' EMAIL VERIFICATION:', email);
    
    // Find user by email
    const user = users.find(u => u.email === email);
    
    if (!user) {
      return res.status(404).json({
        success: false,
        message: 'User not found'
      });
    }
    
    // Mark email as verified
    user.emailVerified = true;
    
    console.log('✅ EMAIL VERIFIED:', email);
    
    res.json({
      success: true,
      message: 'Email verified successfully. You can now login.',
      user: {
        id: user.id,
        email: user.email,
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

// GET USER INFO ENDPOINT
router.get('/me', (req, res) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({
        success: false,
        message: 'No token provided'
      });
    }
    
    // Extract user ID from mock token
    const userId = token.replace('mock-jwt-token-', '');
    const user = users.find(u => u.id == userId);
    
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
        name: user.name,
        firstName: user.firstName,
        email: user.email,
        role: user.role,
        tenantName: user.tenantName,
        emailVerified: user.emailVerified
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

module.exports = router;
