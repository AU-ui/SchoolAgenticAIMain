const { Pool } = require('pg');
const bcrypt = require('bcryptjs');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function setupDatabase() {
  const client = await pool.connect();
  
  try {
    console.log('🚀 Starting database setup...');

    // Create superadmin user
    const superadminPassword = 'SuperAdmin@123456';
    const hashedSuperadminPassword = await bcrypt.hash(superadminPassword, 12);
    
    await client.query(`
      INSERT INTO users (email, password, role, first_name, last_name, is_active, email_verified, requires_approval, tenant_id)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
      ON CONFLICT (email) DO UPDATE SET 
        password = EXCLUDED.password,
        role = EXCLUDED.role,
        first_name = EXCLUDED.first_name,
        last_name = EXCLUDED.last_name,
        is_active = EXCLUDED.is_active,
        email_verified = EXCLUDED.email_verified,
        requires_approval = EXCLUDED.requires_approval
    `, [
      'anilupadhyay06@gmail.com',
      hashedSuperadminPassword,
      'superadmin',
      'Anil',
      'Upadhyay',
      true,
      true,
      false,
      null
    ]);

    // Create admin user
    const adminPassword = 'Admin@123456';
    const hashedAdminPassword = await bcrypt.hash(adminPassword, 12);
    
    await client.query(`
      INSERT INTO users (email, password, role, first_name, last_name, is_active, email_verified, requires_approval, tenant_id)
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
      ON CONFLICT (email) DO UPDATE SET 
        password = EXCLUDED.password,
        role = EXCLUDED.role,
        first_name = EXCLUDED.first_name,
        last_name = EXCLUDED.last_name,
        is_active = EXCLUDED.is_active,
        email_verified = EXCLUDED.email_verified,
        requires_approval = EXCLUDED.requires_approval
    `, [
      'anilupadhyay06@gmail.com',
      hashedAdminPassword,
      'admin',
      'Anil',
      'Upadhyay',
      true,
      true,
      false,
      1
    ]);

    console.log('✅ Database setup completed successfully!');
    console.log('\n📧 Test Accounts Created:');
    console.log('Superadmin: anilupadhyay06@gmail.com / SuperAdmin@123456');
    console.log('Admin: anilupadhyay06@gmail.com / Admin@123456');
    console.log('\n🔐 Password Reset Testing:');
    console.log('You can now test password reset functionality for both admin and superadmin roles');
    console.log('The forgot password link will be available for all user roles');

  } catch (error) {
    console.error('❌ Database setup failed:', error);
    throw error;
  } finally {
    client.release();
  }
}

setupDatabase()
  .then(() => {
    console.log('🎉 Setup completed!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('💥 Setup failed:', error);
    process.exit(1);
  }); 