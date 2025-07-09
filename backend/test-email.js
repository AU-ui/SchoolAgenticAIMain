const { verifyConnection, sendVerificationEmail, sendWelcomeEmail } = require('./src/services/emailService');
require('dotenv').config();

async function testEmailService() {
  console.log('🧪 Testing Email Service...\n');

  // Test 1: Verify connection
  console.log('1. Testing email connection...');
  const connectionResult = await verifyConnection();
  
  if (!connectionResult) {
    console.error('❌ Email connection failed. Please check your configuration.');
    console.log('\n📋 Required environment variables:');
    console.log('- EMAIL_HOST (e.g., smtp.gmail.com)');
    console.log('- EMAIL_PORT (e.g., 587)');
    console.log('- EMAIL_USER (your email address)');
    console.log('- EMAIL_PASSWORD (your app password)');
    console.log('\n📖 See EMAIL_SETUP.md for detailed setup instructions.');
    return;
  }

  console.log('✅ Email connection successful!\n');

  // Test 2: Send verification email
  console.log('2. Testing verification email...');
  const testEmail = process.env.TEST_EMAIL || 'test@example.com';
  const verificationToken = 'test-verification-token-123';
  
  const verificationResult = await sendVerificationEmail(
    testEmail, 
    'Test User', 
    verificationToken
  );

  if (verificationResult.success) {
    console.log('✅ Verification email sent successfully!');
    console.log(`📧 Sent to: ${testEmail}`);
    console.log(`🆔 Message ID: ${verificationResult.messageId}`);
  } else {
    console.error('❌ Verification email failed:', verificationResult.error);
  }

  console.log('\n3. Testing welcome email...');
  
  const welcomeResult = await sendWelcomeEmail(testEmail, 'Test User');

  if (welcomeResult.success) {
    console.log('✅ Welcome email sent successfully!');
    console.log(`📧 Sent to: ${testEmail}`);
    console.log(`🆔 Message ID: ${welcomeResult.messageId}`);
  } else {
    console.error('❌ Welcome email failed:', welcomeResult.error);
  }

  console.log('\n🎉 Email service test completed!');
  console.log('\n📝 Next steps:');
  console.log('1. Check your email inbox (and spam folder)');
  console.log('2. Verify the emails look correct');
  console.log('3. Test the verification link in your frontend');
}

// Run the test
testEmailService().catch(error => {
  console.error('❌ Test failed with error:', error);
  process.exit(1);
}); 