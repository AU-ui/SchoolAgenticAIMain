const { Pool } = require('pg');
require('dotenv').config();

// Use the same database configuration as the backend
const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
  max: 20,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
  ssl: process.env.NODE_ENV === 'production' ? { rejectUnauthorized: false } : false
});

async function checkDatabase() {
  try {
    console.log('🔍 Checking database data...');
    console.log('📊 Database config:', {
      host: process.env.DB_HOST || 'localhost',
      port: process.env.DB_PORT || 5432,
      database: process.env.DB_NAME || 'edtech_platform',
      user: process.env.DB_USER || 'postgres'
    });
    
    // Check all users
    const users = await pool.query(`
      SELECT id, email, first_name, last_name, role 
      FROM users 
      ORDER BY id
    `);
    console.log('👥 All users:', users.rows);
    
    // Check all classes
    const classes = await pool.query(`
      SELECT id, name, teacher_id, grade_level, academic_year
      FROM classes 
      ORDER BY id
    `);
    console.log('📚 All classes:', classes.rows);
    
    // Check if teacher 5 exists
    const teacher5 = await pool.query(`
      SELECT id, email, first_name, last_name 
      FROM users 
      WHERE id = 5
    `);
    console.log('👨‍🏫 Teacher 5:', teacher5.rows[0] || 'Not found');
    
    // Check classes for teacher 5
    const teacher5Classes = await pool.query(`
      SELECT id, name, teacher_id, grade_level
      FROM classes 
      WHERE teacher_id = 5
    `);
    console.log('📚 Classes for teacher 5:', teacher5Classes.rows);
    
    // Check if we need to update classes to assign to teacher 5
    if (teacher5Classes.rows.length === 0 && classes.rows.length > 0) {
      console.log('⚠️ No classes assigned to teacher 5. Updating...');
      
      // Update first 3 classes to teacher 5
      const updateResult = await pool.query(`
        UPDATE classes 
        SET teacher_id = 5 
        WHERE id IN (1, 2, 3)
      `);
      console.log('✅ Updated classes for teacher 5');
      
      // Verify the update
      const updatedClasses = await pool.query(`
        SELECT id, name, teacher_id, grade_level
        FROM classes 
        WHERE teacher_id = 5
      `);
      console.log('📚 Updated classes for teacher 5:', updatedClasses.rows);
    }
    
  } catch (error) {
    console.error('❌ Error:', error.message);
  } finally {
    await pool.end();
  }
}

checkDatabase();

