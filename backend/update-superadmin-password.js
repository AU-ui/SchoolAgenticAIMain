const bcrypt = require('bcryptjs');
const { query } = require('./src/config/database');

async function updateSuperadminPassword() {
  try {
    console.log('🔐 Updating superadmin password...');
    
    // Hash the new password
    const password = 'SuperAdmin123!';
    const hashedPassword = await bcrypt.hash(password, 12);
    
    // Update the superadmin password
    const result = await query(
      'UPDATE users SET password = $1 WHERE email = $2 AND role = $3 RETURNING id, email, role',
      [hashedPassword, 'superadmin@edtech.com', 'superadmin']
    );
    
    if (result.rows.length > 0) {
      console.log('✅ Superadmin password updated successfully!');
      console.log('📧 Email: superadmin@edtech.com');
      console.log('🔑 Password: SuperAdmin123!');
      console.log('👤 Role: superadmin');
    } else {
      console.log('❌ Superadmin user not found. Creating new superadmin...');
      
      // Create new superadmin user
      const newSuperadmin = await query(
        `INSERT INTO users (email, password, first_name, last_name, role, tenant_id, email_verified, is_active) 
         VALUES ($1, $2, $3, $4, $5, $6, $7, $8) RETURNING id, email, role`,
        ['superadmin@edtech.com', hashedPassword, 'Super', 'Admin', 'superadmin', 1, true, true]
      );
      
      console.log('✅ New superadmin created successfully!');
      console.log('📧 Email: superadmin@edtech.com');
      console.log('🔑 Password: SuperAdmin123!');
      console.log('👤 Role: superadmin');
    }
    
  } catch (error) {
    console.error('❌ Error updating superadmin password:', error);
  } finally {
    process.exit(0);
  }
}

// Run the script
updateSuperadminPassword(); 