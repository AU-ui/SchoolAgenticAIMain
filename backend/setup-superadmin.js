const bcrypt = require('bcrypt');
const { query } = require('./src/config/database');
const { v4: uuidv4 } = require('uuid');

async function setupSuperadmin() {
  try {
    console.log('🚀 Setting up superadmin account...\n');
    
    // Check if superadmin already exists
    const existingSuperadmin = await query(`
      SELECT id, email FROM users WHERE role = 'superadmin'
    `);
    
    if (existingSuperadmin.rows.length > 0) {
      console.log('⚠️  Superadmin already exists!');
      console.log('📧 Existing superadmin email:', existingSuperadmin.rows[0].email);
      return;
    }
    
    // Create new superadmin with simple credentials
    const superadminData = {
      email: 'admin@school.com',
      password: 'admin123',
      first_name: 'School',
      last_name: 'Admin',
      role: 'superadmin',
      status: 'active'
    };
    
    // Hash password
    const saltRounds = 10;
    const hashedPassword = await bcrypt.hash(superadminData.password, saltRounds);
    
    // Insert superadmin
    const insertQuery = `
      INSERT INTO users (
        id, email, password_hash, first_name, last_name, 
        role, status, email_verified, created_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW())
    `;
    
    await query(insertQuery, [
      uuidv4(),
      superadminData.email,
      hashedPassword,
      superadminData.first_name,
      superadminData.last_name,
      superadminData.role,
      superadminData.status,
      true
    ]);
    
    console.log('✅ Superadmin created successfully!');
    console.log('=====================================');
    console.log('📧 Email: ' + superadminData.email);
    console.log('🔑 Password: ' + superadminData.password);
    console.log('👤 Role: ' + superadminData.role);
    console.log('📊 Status: ' + superadminData.status);
    console.log('=====================================');
    console.log('🎯 You can now login with these credentials!');
    
  } catch (error) {
    console.error('❌ Error creating superadmin:', error);
  }
}

setupSuperadmin(); 