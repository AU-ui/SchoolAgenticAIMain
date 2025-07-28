const bcrypt = require('bcrypt');
const { query } = require('./src/config/database');
const { v4: uuidv4 } = require('uuid');

async function createSuperadmin() {
  try {
    // Check if superadmin already exists
    const existingSuperadmin = await query(`
      SELECT id FROM users WHERE role = 'superadmin'
    `);
    
    if (existingSuperadmin.rows.length > 0) {
      console.log('Superadmin already exists!');
      return;
    }
    
    // Create superadmin credentials
    const superadminData = {
      email: 'superadmin@school.com',
      password: 'SuperAdmin@2024',
      first_name: 'Super',
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
    console.log('📧 Email:', superadminData.email);
    console.log('🔑 Password:', superadminData.password);
    console.log('⚠️  Please change the password after first login!');
    
  } catch (error) {
    console.error('Error creating superadmin:', error);
  }
}

createSuperadmin(); 