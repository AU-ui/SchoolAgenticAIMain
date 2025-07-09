const { query } = require('./src/config/database');

async function setupDevelopmentMode() {
  try {
    console.log('🔧 Setting up development mode...');
    
    // Update superadmin to be email verified and active
    await query(
      'UPDATE users SET email_verified = true, is_active = true, requires_approval = false WHERE email = $1 AND role = $2',
      ['superadmin@edtech.com', 'superadmin']
    );
    
    console.log('✅ Development mode setup completed!');
    console.log('\n📋 Login Credentials:');
    console.log('📧 Email: superadmin@edtech.com');
    console.log('🔑 Password: SuperAdmin123!');
    console.log('👤 Role: superadmin');
    console.log('\n🚀 You can now log in directly without email verification!');
    console.log('\n⚠️  Note: This is development mode. Email verification is bypassed.');
    
  } catch (error) {
    console.error('❌ Error setting up development mode:', error);
  } finally {
    process.exit(0);
  }
}

// Run the script
setupDevelopmentMode(); 