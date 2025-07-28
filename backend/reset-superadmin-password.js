const bcrypt = require('bcrypt');
const { query } = require('./src/config/database');

async function resetSuperadminPassword() {
  try {
    const newPassword = 'admin123';
    const saltRounds = 10;
    const hashedPassword = await bcrypt.hash(newPassword, saltRounds);
    
    const updateQuery = `
      UPDATE users 
      SET password_hash = $1, updated_at = NOW()
      WHERE role = 'superadmin'
    `;
    
    const result = await query(updateQuery, [hashedPassword]);
    
    if (result.rowCount > 0) {
      console.log('✅ Superadmin password reset successfully!');
      console.log('📧 Email: admin@school.com (or existing superadmin email)');
      console.log('🔑 New Password: ' + newPassword);
    } else {
      console.log('❌ No superadmin found to reset password');
    }
    
  } catch (error) {
    console.error('❌ Error resetting password:', error);
  }
}

resetSuperadminPassword(); 