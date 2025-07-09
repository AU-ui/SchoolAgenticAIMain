const { testConnection, query } = require('../src/config/database');

async function testDatabaseConnection() {
  console.log('🔍 Testing database connection...\n');
  
  try {
    // Test basic connection
    const isConnected = await testConnection();
    if (!isConnected) {
      console.log('❌ Database connection failed');
      return false;
    }
    
    console.log('✅ Database connection successful\n');
    
    // Test basic queries
    console.log('📊 Testing basic queries...');
    
    // Test tenants table
    const tenantsResult = await query('SELECT COUNT(*) as count FROM tenants');
    console.log(`✅ Tenants table: ${tenantsResult.rows[0].count} records`);
    
    // Test users table
    const usersResult = await query('SELECT COUNT(*) as count FROM users');
    console.log(`✅ Users table: ${usersResult.rows[0].count} records`);
    
    // Test schools table
    const schoolsResult = await query('SELECT COUNT(*) as count FROM schools');
    console.log(`✅ Schools table: ${schoolsResult.rows[0].count} records`);
    
    // Test sample data
    console.log('\n👥 Sample data check:');
    const sampleUser = await query(
      'SELECT email, role, first_name, last_name FROM users WHERE email = $1',
      ['superadmin@edtech.com']
    );
    
    if (sampleUser.rows.length > 0) {
      const user = sampleUser.rows[0];
      console.log(`✅ Superadmin user found: ${user.first_name} ${user.last_name} (${user.email})`);
    } else {
      console.log('⚠️  Superadmin user not found - run db:setup first');
    }
    
    // Test tenant data
    const sampleTenant = await query(
      'SELECT name, domain FROM tenants WHERE id = 1'
    );
    
    if (sampleTenant.rows.length > 0) {
      const tenant = sampleTenant.rows[0];
      console.log(`✅ Sample tenant found: ${tenant.name} (${tenant.domain})`);
    } else {
      console.log('⚠️  Sample tenant not found - run db:setup first');
    }
    
    console.log('\n🎉 Database connection test completed successfully!');
    console.log('🚀 Backend is ready to start');
    
    return true;
    
  } catch (error) {
    console.error('❌ Database test failed:', error.message);
    console.log('\n💡 Troubleshooting tips:');
    console.log('1. Make sure PostgreSQL is running');
    console.log('2. Check your database credentials in config.env');
    console.log('3. Run "npm run db:setup" to initialize the database');
    console.log('4. Ensure the database "edtech_platform" exists');
    
    return false;
  }
}

// Run test if this file is executed directly
if (require.main === module) {
  testDatabaseConnection()
    .then((success) => {
      process.exit(success ? 0 : 1);
    })
    .catch((error) => {
      console.error('❌ Test failed:', error);
      process.exit(1);
    });
}

module.exports = { testDatabaseConnection }; 