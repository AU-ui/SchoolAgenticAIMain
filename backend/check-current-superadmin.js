const { query } = require('./src/config/database');

async function checkCurrentSuperadmin() {
  try {
    console.log('🔍 Checking for existing superadmin users...\n');
    
    const result = await query(`
      SELECT 
        id, 
        email, 
        first_name, 
        last_name, 
        role, 
        status,
        email_verified,
        created_at
      FROM users 
      WHERE role = 'superadmin' OR role = 'admin'
      ORDER BY role DESC, created_at ASC
    `);
    
    if (result.rows.length === 0) {
      console.log('❌ No superadmin or admin users found!');
      console.log('�� You need to create a superadmin account.');
    } else {
      console.log('✅ Found existing admin users:');
      console.log('=====================================');
      
      result.rows.forEach((user, index) => {
        console.log(`${index + 1}. ${user.first_name} ${user.last_name}`);
        console.log(`   📧 Email: ${user.email}`);
        console.log(`   👤 Role: ${user.role}`);
        console.log(`   📊 Status: ${user.status}`);
        console.log(`   ✅ Email Verified: ${user.email_verified}`);
        console.log(`   📅 Created: ${user.created_at}`);
        console.log('-------------------------------------');
      });
    }
    
  } catch (error) {
    console.error('❌ Error checking superadmin:', error);
  }
}

checkCurrentSuperadmin(); 