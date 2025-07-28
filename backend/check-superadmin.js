const { query } = require('./src/config/database');

async function checkSuperadmin() {
  try {
    const result = await query(`
      SELECT id, email, first_name, last_name, role, status 
      FROM users 
      WHERE role = 'superadmin'
    `);
    
    console.log('Existing Superadmin Users:');
    result.rows.forEach(user => {
      console.log(`- ${user.first_name} ${user.last_name} (${user.email}) - Status: ${user.status}`);
    });
    
    if (result.rows.length === 0) {
      console.log('No superadmin found. Creating one...');
    }
  } catch (error) {
    console.error('Error checking superadmin:', error);
  }
}

checkSuperadmin(); 