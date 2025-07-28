const { query } = require('./src/config/database');

async function findSuperadmin() {
  try {
    console.log('🔍 Searching for SUPERADMIN credentials...\n');
    
    // Check for superadmin users specifically
    const superadminQuery = `
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
      WHERE role = 'superadmin'
      ORDER BY created_at ASC
    `;
    
    const result = await query(superadminQuery);
    
    if (result.rows.length === 0) {
      console.log('❌ No SUPERADMIN found in database!');
      console.log(' Creating a new superadmin account...');
      
      // Create superadmin
      await createSuperadmin();
    } else {
      console.log('✅ Found SUPERADMIN users:');
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
      
      console.log('\n🎯 SUPERADMIN CREDENTIALS:');
      console.log('=====================================');
      console.log(`📧 Email: ${result.rows[0].email}`);
      console.log('🔑 Password: (check below for default password)');
      console.log('=====================================');
    }
    
    // Check all users to see what exists
    const allUsersQuery = `
      SELECT 
        email, 
        first_name, 
        last_name, 
        role, 
        status
      FROM users 
      ORDER BY role, created_at
    `;
    
    const allUsersResult = await query(allUsersQuery);
    
    console.log('\n📊 All Users in Database:');
    console.log('=====================================');
    allUsersResult.rows.forEach(user => {
      console.log(`${user.role.toUpperCase()}: ${user.email} (${user.first_name} ${user.last_name})`);
    });
    
  } catch (error) {
    console.error('❌ Error finding superadmin:', error);
  }
}

async function createSuperadmin() {
  try {
    const bcrypt = require('bcrypt');
    const { v4: uuidv4 } = require('uuid');
    
    const superadminData = {
      email: 'superadmin@school.com',
      password: 'superadmin123',
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
    
    console.log('✅ SUPERADMIN created successfully!');
    console.log('=====================================');
    console.log('📧 Email: ' + superadminData.email);
    console.log('🔑 Password: ' + superadminData.password);
    console.log('👤 Role: ' + superadminData.role);
    console.log('=====================================');
    
  } catch (error) {
    console.error('❌ Error creating superadmin:', error);
  }
}

findSuperadmin(); 