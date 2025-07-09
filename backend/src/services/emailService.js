const nodemailer = require('nodemailer');
require('dotenv').config();

// Email configuration
const emailConfig = {
  host: process.env.EMAIL_HOST || 'smtp.gmail.com',
  port: process.env.EMAIL_PORT || 587,
  secure: false, // true for 465, false for other ports
  auth: {
    user: process.env.EMAIL_USER || 'your-email@gmail.com',
    pass: process.env.EMAIL_PASSWORD || 'your-app-password'
  }
};

// Create transporter
const transporter = nodemailer.createTransport(emailConfig);

// Verify transporter connection
const verifyConnection = async () => {
  try {
    await transporter.verify();
    console.log('✅ Email service connected successfully');
    return true;
  } catch (error) {
    console.error('❌ Email service connection failed:', error.message);
    return false;
  }
};

// Email templates
const emailTemplates = {
  verification: (userName, verificationCode) => ({
    subject: 'Verification Code - EdTech Platform',
    html: `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Verification Code</title>
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
          .container { max-width: 600px; margin: 0 auto; padding: 20px; }
          .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
          .content { background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }
          .code { background: #e1e5e9; padding: 20px; border-radius: 8px; text-align: center; font-size: 24px; font-weight: bold; letter-spacing: 4px; margin: 20px 0; }
          .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>🎓 EdTech Platform</h1>
            <p>Your verification code</p>
          </div>
          <div class="content">
            <h2>Hello ${userName}!</h2>
            <p>Here is your verification code to complete your login or registration:</p>
            <div class="code">${verificationCode}</div>
            <p>This code will expire in 10 minutes. If you didn't request this code, please ignore this email.</p>
          </div>
          <div class="footer">
            <p>© 2024 EdTech Platform. All rights reserved.</p>
          </div>
        </div>
      </body>
      </html>
    `,
    text: `
      Hello ${userName}!
      
      Here is your verification code to complete your login or registration:
      
      ${verificationCode}
      
      This code will expire in 10 minutes. If you didn't request this code, please ignore this email.
      
      © 2024 EdTech Platform. All rights reserved.
    `
  }),

  welcome: (userName, loginUrl) => ({
    subject: 'Welcome to EdTech Platform!',
    html: `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to EdTech Platform</title>
        <style>
          body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
          .container { max-width: 600px; margin: 0 auto; padding: 20px; }
          .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
          .content { background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }
          .button { display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 8px; font-weight: bold; margin: 20px 0; }
          .footer { text-align: center; margin-top: 30px; color: #666; font-size: 14px; }
        </style>
      </head>
      <body>
        <div class="container">
          <div class="header">
            <h1>🎓 EdTech Platform</h1>
            <p>Your account is now active!</p>
          </div>
          <div class="content">
            <h2>Welcome ${userName}!</h2>
            <p>🎉 Congratulations! Your email has been successfully verified and your EdTech Platform account is now active.</p>
            
            <p>You can now access all the features of our platform:</p>
            <ul>
              <li>📚 Smart Learning Management</li>
              <li>👨‍🏫 Teacher Tools & Resources</li>
              <li>👨‍👩‍👧‍👦 Parent Communication</li>
              <li>📊 Progress Tracking</li>
              <li>🎯 AI-Powered Insights</li>
            </ul>
            
            <div style="text-align: center;">
              <a href="${loginUrl}" class="button">Login to Your Account</a>
            </div>
            
            <p>If you have any questions or need assistance, please don't hesitate to contact our support team.</p>
          </div>
          <div class="footer">
            <p>© 2024 EdTech Platform. All rights reserved.</p>
          </div>
        </div>
      </body>
      </html>
    `,
    text: `
      Welcome ${userName}!
      
      🎉 Congratulations! Your email has been successfully verified and your EdTech Platform account is now active.
      
      You can now access all the features of our platform. Login here: ${loginUrl}
      
      If you have any questions or need assistance, please don't hesitate to contact our support team.
      
      © 2024 EdTech Platform. All rights reserved.
    `
  })
};

// Send email function
const sendEmail = async (to, template, data) => {
  try {
    let emailContent;
    if (template === 'verification') {
      emailContent = emailTemplates[template](data.userName, data.code);
    } else if (template === 'welcome') {
      emailContent = emailTemplates[template](data.userName, data.url);
    } else {
      // Handle custom email format
      const mailOptions = {
        from: `"EdTech Platform" <${emailConfig.auth.user}>`,
        to: to,
        subject: data.subject,
        html: data.html,
        text: data.text
      };
      
      const result = await transporter.sendMail(mailOptions);
      console.log('✅ Email sent successfully:', result.messageId);
      return { success: true, messageId: result.messageId };
    }
    
    const mailOptions = {
      from: `"EdTech Platform" <${emailConfig.auth.user}>`,
      to: to,
      subject: emailContent.subject,
      html: emailContent.html,
      text: emailContent.text
    };

    const result = await transporter.sendMail(mailOptions);
    console.log('✅ Email sent successfully:', result.messageId);
    return { success: true, messageId: result.messageId };
  } catch (error) {
    console.error('❌ Email sending failed:', error);
    return { success: false, error: error.message };
  }
};

// Send verification email
const sendVerificationEmail = async (userEmail, userName, verificationLink) => {
  return await sendEmail(userEmail, 'verification', {
    userName,
    code: verificationLink
  });
};

// Send welcome email
const sendWelcomeEmail = async (userEmail, userName) => {
  const loginUrl = `${process.env.FRONTEND_URL || 'http://localhost:3000'}/login`;
  
  return await sendEmail(userEmail, 'welcome', {
    userName,
    url: loginUrl
  });
};

module.exports = {
  verifyConnection,
  sendEmail,
  sendVerificationEmail,
  sendWelcomeEmail
}; 