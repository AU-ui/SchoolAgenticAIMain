const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function checkMissingTables() {
  console.log('🔍 Checking Database Tables Status...\n');
  
  try {
    // List of required tables for attendance system
    const requiredTables = [
      'users',
      'schools', 
      'classes',
      'class_students',
      'attendance_sessions',
      'attendance_records',
      'attendance_analytics'
    ];
    
    const existingTables = [];
    const missingTables = [];
    
    for (const tableName of requiredTables) {
      try {
        const result = await pool.query(`
          SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = $1
          );
        `, [tableName]);
        
        if (result.rows[0].exists) {
          existingTables.push(tableName);
          console.log(`✅ ${tableName} - EXISTS`);
        } else {
          missingTables.push(tableName);
          console.log(`❌ ${tableName} - MISSING`);
        }
      } catch (error) {
        missingTables.push(tableName);
        console.log(`❌ ${tableName} - ERROR: ${error.message}`);
      }
    }
    
    console.log('\n📊 SUMMARY:');
    console.log(`✅ Existing Tables: ${existingTables.length}`);
    console.log(`❌ Missing Tables: ${missingTables.length}`);
    
    if (missingTables.length > 0) {
      console.log('\n🔧 Missing Tables:');
      missingTables.forEach(table => console.log(`   - ${table}`));
    }
    
    // Check data in existing tables
    console.log('\n📋 Data Check:');
    for (const tableName of existingTables) {
      try {
        const result = await pool.query(`SELECT COUNT(*) as count FROM ${tableName}`);
        console.log(`   ${tableName}: ${result.rows[0].count} records`);
      } catch (error) {
        console.log(`   ${tableName}: ERROR - ${error.message}`);
      }
    }
    
  } catch (error) {
    console.error('❌ Error checking tables:', error);
  } finally {
    await pool.end();
  }
}

checkMissingTables();
