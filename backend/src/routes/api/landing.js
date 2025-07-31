const express = require('express');
const { query } = require('../../config/database');

const router = express.Router();

// @route   GET /api/landing/schools
// @desc    Get list of active schools for landing page
// @access  Public
router.get('/schools', async (req, res) => {
  try {
    const schools = await query(
      `SELECT t.id, t.name, t.domain, t.address, t.phone, t.email, t.logo_url,
              COUNT(DISTINCT s.id) as school_count,
              COUNT(DISTINCT u.id) as user_count
       FROM tenants t
       LEFT JOIN schools s ON t.id = s.tenant_id AND s.is_active = true
       LEFT JOIN users u ON t.id = u.tenant_id AND u.is_active = true
       WHERE t.is_active = true
       GROUP BY t.id, t.name, t.domain, t.address, t.phone, t.email, t.logo_url
       ORDER BY t.name ASC`
    );

    res.json({
      success: true,
      data: {
        schools: schools.rows.map(school => ({
          id: school.id,
          name: school.name,
          domain: school.domain,
          address: school.address,
          phone: school.phone,
          email: school.email,
          logoUrl: school.logo_url,
          schoolCount: parseInt(school.school_count),
          userCount: parseInt(school.user_count)
        }))
      }
    });

  } catch (error) {
    console.error('Get schools error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// @route   GET /api/landing/schools/:id
// @desc    Get specific school details for landing page
// @access  Public
router.get('/schools/:id', async (req, res) => {
  try {
    const { id } = req.params;

    const school = await query(
      `SELECT t.id, t.name, t.domain, t.address, t.phone, t.email, t.logo_url,
              COUNT(DISTINCT s.id) as school_count,
              COUNT(DISTINCT u.id) as user_count,
              COUNT(DISTINCT CASE WHEN u.role = 'teacher' THEN u.id END) as teacher_count,
              COUNT(DISTINCT CASE WHEN u.role = 'student' THEN u.id END) as student_count,
              COUNT(DISTINCT CASE WHEN u.role = 'parent' THEN u.id END) as parent_count
       FROM tenants t
       LEFT JOIN schools s ON t.id = s.tenant_id AND s.is_active = true
       LEFT JOIN users u ON t.id = u.tenant_id AND u.is_active = true
       WHERE t.id = $1 AND t.is_active = true
       GROUP BY t.id, t.name, t.domain, t.address, t.phone, t.email, t.logo_url`,
      [id]
    );

    if (school.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'School not found'
      });
    }

    const schoolData = school.rows[0];

    res.json({
      success: true,
      data: {
        school: {
          id: schoolData.id,
          name: schoolData.name,
          domain: schoolData.domain,
          address: schoolData.address,
          phone: schoolData.phone,
          email: schoolData.email,
          logoUrl: schoolData.logo_url,
          schoolCount: parseInt(schoolData.school_count),
          userCount: parseInt(schoolData.user_count),
          teacherCount: parseInt(schoolData.teacher_count),
          studentCount: parseInt(schoolData.student_count),
          parentCount: parseInt(schoolData.parent_count)
        }
      }
    });

  } catch (error) {
    console.error('Get school details error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// @route   POST /api/landing/contact
// @desc    Submit contact form from landing page
// @access  Public
router.post('/contact', async (req, res) => {
  try {
    const { name, email, phone, message, schoolId } = req.body;

    // Basic validation
    if (!name || !email || !message) {
      return res.status(400).json({
        success: false,
        message: 'Name, email, and message are required'
      });
    }

    // Store contact inquiry (you might want to create a contacts table)
    console.log('Contact inquiry received:', {
      name,
      email,
      phone,
      message,
      schoolId,
      timestamp: new Date().toISOString()
    });

    // Send email notification to admin
    const emailService = require('../../services/emailService');
    
    const contactEmailTemplate = {
      subject: 'New Contact Form Submission - EdTech Platform',
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>New Contact Form Submission</title>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
            .content { background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }
            .contact-details { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
            .contact-details h3 { margin-top: 0; color: #667eea; }
            .contact-details p { margin: 10px 0; }
            .message-box { background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 15px 0; border-left: 4px solid #667eea; }
            .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>📧 New Contact Form Submission</h1>
              <p>EdTech Platform</p>
            </div>
            <div class="content">
              <h2>Hello Admin!</h2>
              <p>A new contact form has been submitted on the EdTech Platform landing page.</p>
              
              <div class="contact-details">
                <h3>Contact Information</h3>
                <p><strong>Name:</strong> ${name}</p>
                <p><strong>Email:</strong> ${email}</p>
                ${phone ? `<p><strong>Phone:</strong> ${phone}</p>` : ''}
                ${schoolId ? `<p><strong>School ID:</strong> ${schoolId}</p>` : ''}
                <p><strong>Submitted:</strong> ${new Date().toLocaleString()}</p>
              </div>
              
              <div class="message-box">
                <h3>Message:</h3>
                <p>${message.replace(/\n/g, '<br>')}</p>
              </div>
              
              <p>Please respond to this inquiry as soon as possible.</p>
            </div>
            <div class="footer">
              <p>© 2024 EdTech Platform. All rights reserved.</p>
            </div>
          </div>
        </body>
        </html>
      `,
      text: `
        New Contact Form Submission - EdTech Platform
        
        Hello Admin!
        
        A new contact form has been submitted on the EdTech Platform landing page.
        
        Contact Information:
        Name: ${name}
        Email: ${email}
        ${phone ? `Phone: ${phone}` : ''}
        ${schoolId ? `School ID: ${schoolId}` : ''}
        Submitted: ${new Date().toLocaleString()}
        
        Message:
        ${message}
        
        Please respond to this inquiry as soon as possible.
        
        © 2024 EdTech Platform. All rights reserved.
      `
    };

    // Send email to admin
    try {
      const emailResult = await emailService.sendEmail('newanilupadhyay@gmail.com', 'custom', contactEmailTemplate);
      
      if (!emailResult.success) {
        console.error('Email sending failed:', emailResult.error);
        // Still return success to user, but log the email error
      } else {
        console.log('✅ Email sent successfully to newanilupadhyay@gmail.com');
      }
    } catch (emailError) {
      console.error('❌ Email service error:', emailError);
      // Log the contact data for manual review
      console.log('📧 Contact Form Data (Email failed):', {
        name,
        email,
        phone,
        message,
        timestamp: new Date().toISOString()
      });
    }

    res.json({
      success: true,
      message: 'Thank you for your message. We will get back to you soon!'
    });

  } catch (error) {
    console.error('Contact form error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// @route   GET /api/landing/stats
// @desc    Get platform statistics for landing page
// @access  Public
router.get('/stats', async (req, res) => {
  try {
    const stats = await query(
      `SELECT 
        COUNT(DISTINCT t.id) as total_schools,
        COUNT(DISTINCT u.id) as total_users,
        COUNT(DISTINCT CASE WHEN u.role = 'teacher' THEN u.id END) as total_teachers,
        COUNT(DISTINCT CASE WHEN u.role = 'student' THEN u.id END) as total_students,
        COUNT(DISTINCT CASE WHEN u.role = 'parent' THEN u.id END) as total_parents
       FROM tenants t
       LEFT JOIN users u ON t.id = u.tenant_id AND u.is_active = true
       WHERE t.is_active = true`
    );

    const platformStats = stats.rows[0];

    res.json({
      success: true,
      data: {
        stats: {
          totalSchools: parseInt(platformStats.total_schools),
          totalUsers: parseInt(platformStats.total_users),
          totalTeachers: parseInt(platformStats.total_teachers),
          totalStudents: parseInt(platformStats.total_students),
          totalParents: parseInt(platformStats.total_parents)
        }
      }
    });

  } catch (error) {
    console.error('Get stats error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// @route   GET /api/landing/tenant-logo/:schoolCode
// @desc    Get tenant logo by school code
// @access  Public
router.get('/tenant-logo/:schoolCode', async (req, res) => {
  try {
    const { schoolCode } = req.params;

    // Find tenant by school code
    const tenantResult = await query(
      `SELECT t.id, t.name, t.logo_url, t.domain
       FROM tenants t
       JOIN school_codes sc ON t.id = sc.tenant_id
       WHERE sc.code = $1 AND sc.is_active = true AND t.is_active = true
       LIMIT 1`,
      [schoolCode]
    );

    if (tenantResult.rows.length === 0) {
      return res.status(404).json({
        success: false,
        message: 'School not found or code is invalid'
      });
    }

    const tenant = tenantResult.rows[0];

    res.json({
      success: true,
      data: {
        tenantId: tenant.id,
        tenantName: tenant.name,
        logoUrl: tenant.logo_url,
        domain: tenant.domain
      }
    });

  } catch (error) {
    console.error('Get tenant logo error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error'
    });
  }
});

// @route   GET /api/landing/test-email
// @desc    Test email configuration
// @access  Public
router.get('/test-email', async (req, res) => {
  try {
    const emailService = require('../../services/emailService');
    
    // Test email template
    const testEmailTemplate = {
      subject: 'Test Email - EdTech Platform',
      html: `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <title>Test Email</title>
          <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
            .content { background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }
            .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
          </style>
        </head>
        <body>
          <div class="container">
            <div class="header">
              <h1>📧 Test Email</h1>
              <p>EdTech Platform</p>
            </div>
            <div class="content">
              <h2>Hello Admin!</h2>
              <p>This is a test email to verify the email configuration is working properly.</p>
              <p><strong>Timestamp:</strong> ${new Date().toLocaleString()}</p>
            </div>
            <div class="footer">
              <p>© 2024 EdTech Platform. All rights reserved.</p>
            </div>
          </div>
        </body>
        </html>
      `,
      text: `
        Test Email - EdTech Platform
        
        Hello Admin!
        
        This is a test email to verify the email configuration is working properly.
        
        Timestamp: ${new Date().toLocaleString()}
        
        © 2024 EdTech Platform. All rights reserved.
      `
    };

    // Send test email
    const emailResult = await emailService.sendEmail('newanilupadhyay@gmail.com', 'custom', testEmailTemplate);
    
    if (emailResult.success) {
      res.json({
        success: true,
        message: 'Test email sent successfully!',
        messageId: emailResult.messageId
      });
    } else {
      res.status(500).json({
        success: false,
        message: 'Failed to send test email',
        error: emailResult.error
      });
    }

  } catch (error) {
    console.error('Test email error:', error);
    res.status(500).json({
      success: false,
      message: 'Internal server error',
      error: error.message
    });
  }
});

module.exports = router; 