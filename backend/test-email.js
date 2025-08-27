const emailService = require('./src/services/emailService');

console.log('📧 Testing Email Configuration');
console.log('==============================\n');

const testEmail = async () => {
  try {
    // Test email configuration
    console.log('🔍 Checking email configuration...');
    
    // Test connection
    const isConnected = await emailService.verifyConnection();
    
    if (!isConnected) {
      console.log('❌ Email service connection failed!');
      console.log('\n📋 Troubleshooting:');
      console.log('1. Check your .env file has correct email settings');
      console.log('2. For Gmail: Use App Password, not regular password');
      console.log('3. Enable 2-Factor Authentication on your Google account');
      console.log('4. Generate App Password: Google Account → Security → App passwords');
      return;
    }
    
    console.log('✅ Email service connected successfully!');
    
    // Test sending email
    console.log('\n📤 Sending test email...');
    
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
              <h2>Hello!</h2>
              <p>This is a test email to verify the email configuration is working properly.</p>
              <p><strong>Timestamp:</strong> ${new Date().toLocaleString()}</p>
              <p><strong>Status:</strong> ✅ Email service is working!</p>
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
        
        Hello!
        
        This is a test email to verify the email configuration is working properly.
        
        Timestamp: ${new Date().toLocaleString()}
        Status: ✅ Email service is working!
        
        © 2024 EdTech Platform. All rights reserved.
      `
    };
    
    // Get email from environment or use default
    const testEmailAddress = process.env.EMAIL_USER || 'test@example.com';
    
    const result = await emailService.sendEmail(testEmailAddress, 'custom', testEmailTemplate);
    
    if (result.success) {
      console.log('✅ Test email sent successfully!');
      console.log(`📧 Message ID: ${result.messageId}`);
      console.log(`📬 Sent to: ${testEmailAddress}`);
      console.log('\n🎉 Email configuration is working perfectly!');
    } else {
      console.log('❌ Failed to send test email');
      console.log(`Error: ${result.error}`);
    }
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
    console.log('\n📋 Common issues:');
    console.log('1. Check your .env file exists and has correct email settings');
    console.log('2. For Gmail: Use App Password, not regular password');
    console.log('3. Make sure 2-Factor Authentication is enabled');
    console.log('4. Check your internet connection');
  }
};

// Run test
testEmail();
