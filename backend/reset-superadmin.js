const bcrypt = require('bcrypt');
const { query } = require('./src/config/database');

async function resetSuperadminPassword() {
  try {
    const newPassword = 'superadmin123';
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
      console.log('🔑 New Password: ' + newPassword);
      
      // Get the email
      const emailQuery = `SELECT email FROM users WHERE role = 'superadmin' LIMIT 1`;
      const emailResult = await query(emailQuery);
      if (emailResult.rows.length > 0) {
        console.log('📧 Email: ' + emailResult.rows[0].email);
      }
    } else {
      console.log('❌ No superadmin found to reset password');
    }
    
  } catch (error) {
    console.error('❌ Error resetting password:', error);
  }
}

resetSuperadminPassword(); 