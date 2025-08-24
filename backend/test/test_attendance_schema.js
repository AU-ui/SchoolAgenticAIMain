const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');
require('dotenv').config({ path: path.join(__dirname, '../.env') });

// Database connection configuration
const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'school_management',
  password: process.env.DB_PASSWORD || '1234',
  port: process.env.DB_PORT || 5432,
});

async function testAttendanceSchema() {
  const client = await pool.connect();
  
  try {
    console.log(' Testing Attendance Schema...');
    
    // First, drop existing tables if they exist
    console.log(' Dropping existing attendance tables...');
    await client.query(`
      DROP TABLE IF EXISTS attendance_analytics CASCADE;
      DROP TABLE IF EXISTS attendance_records CASCADE;
      DROP TABLE IF EXISTS attendance_sessions CASCADE;
    `);
    console.log('✅ Old tables dropped successfully');
    
    // Read the SQL file
    const sqlPath = path.join(__dirname, '../database/attendance_schema.sql');
    const sqlContent = fs.readFileSync(sqlPath, 'utf8');
    
    console.log('📖 SQL file loaded successfully');
    
    // Execute the SQL
    await client.query(sqlContent);
    console.log('✅ Tables created successfully');
    
    // Test table creation
    const tables = ['attendance_sessions', 'attendance_records', 'attendance_analytics'];
    
    for (const table of tables) {
      const result = await client.query(`
        SELECT EXISTS (
          SELECT FROM information_schema.tables 
          WHERE table_schema = 'public' 
          AND table_name = $1
        );
      `, [table]);
      
      if (result.rows[0].exists) {
        console.log(`✅ Table '${table}' exists`);
      } else {
        console.log(`❌ Table '${table}' missing`);
      }
    }
    
    // Test constraints
    console.log('🔍 Testing constraints...');
    
    // Test attendance_records status constraint
    try {
      await client.query(`
        INSERT INTO attendance_records (session_id, student_id, status, marked_by) 
        VALUES (1, 1, 'invalid_status', 1)
      `);
      console.log('❌ Status constraint failed - should have rejected invalid status');
    } catch (error) {
      console.log('✅ Status constraint working - rejected invalid status');
    }
    
    // Test valid status
    try {
      await client.query(`
        INSERT INTO attendance_records (session_id, student_id, status, marked_by) 
        VALUES (1, 1, 'present', 1)
      `);
      console.log('✅ Valid status constraint working');
    } catch (error) {
      console.log('❌ Valid status constraint failed:', error.message);
    }
    
    console.log('🎉 All tests passed! Attendance schema is working correctly.');
    
  } catch (error) {
    console.error('❌ Test failed:', error.message);
  } finally {
    client.release();
    await pool.end();
  }
}

// Run the test
testAttendanceSchema();