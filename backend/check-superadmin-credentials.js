const { query } = require('./src/config/database');

async function checkSuperadminCredentials() {
  try {
    console.log('🔍 Checking database for superadmin credentials...\n');
    
    // Check for superadmin users
    const superadminQuery = `
      SELECT 
        id, 
        email, 
        first_name, 
        last_name, 
        role, 
        status,
        email_verified,
        created_at,
        updated_at
      FROM users 
      WHERE role = 'superadmin'
      ORDER BY created_at ASC
    `;
    
    const superadminResult = await query(superadminQuery);
    
    if (superadminResult.rows.length === 0) {
      console.log('❌ No superadmin users found in database!');
      
      // Check for admin users
      const adminQuery = `
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
        WHERE role = 'admin'
        ORDER BY created_at ASC
      `;
      
      const adminResult = await query(adminQuery);
      
      if (adminResult.rows.length === 0) {
        console.log('❌ No admin users found either!');
        console.log('�� You need to create a superadmin account.');
      } else {
        console.log('⚠️  Found admin users (not superadmin):');
        adminResult.rows.forEach((user, index) => {
          console.log(`${index + 1}. ${user.first_name} ${user.last_name} (${user.email}) - Role: ${user.role}`);
        });
      }
    } else {
      console.log('✅ Found superadmin users:');
      console.log('=====================================');
      
      superadminResult.rows.forEach((user, index) => {
        console.log(`${index + 1}. ${user.first_name} ${user.last_name}`);
        console.log(`   📧 Email: ${user.email}`);
        console.log(`   👤 Role: ${user.role}`);
        console.log(`   📊 Status: ${user.status}`);
        console.log(`   ✅ Email Verified: ${user.email_verified}`);
        console.log(`   📅 Created: ${user.created_at}`);
        if (user.updated_at) {
          console.log(`   🔄 Updated: ${user.updated_at}`);
        }
        console.log('-------------------------------------');
      });
    }
    
    // Check total users count
    const totalUsersQuery = `
      SELECT 
        role,
        COUNT(*) as count
      FROM users 
      GROUP BY role
      ORDER BY role
    `;
    
    const totalUsersResult = await query(totalUsersQuery);
    
    console.log('\n📊 Total Users by Role:');
    console.log('=====================================');
    totalUsersResult.rows.forEach(row => {
      console.log(`${row.role}: ${row.count} users`);
    });
    
  } catch (error) {
    console.error('❌ Error checking database:', error);
    console.error('Error details:', error.message);
  }
}

checkSuperadminCredentials(); 