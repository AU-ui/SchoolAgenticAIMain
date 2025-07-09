const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

// Database configuration
const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
};

async function resetDatabase() {
  console.log('🔄 Starting database reset...');
  
  const pool = new Pool(dbConfig);
  
  try {
    // Drop all tables if they exist
    console.log('🗑️  Dropping existing tables...');
    
    const dropTablesSQL = `
      DROP TABLE IF EXISTS parent_students CASCADE;
      DROP TABLE IF EXISTS teachers CASCADE;
      DROP TABLE IF EXISTS parents CASCADE;
      DROP TABLE IF EXISTS students CASCADE;
      DROP TABLE IF EXISTS classes CASCADE;
      DROP TABLE IF EXISTS schools CASCADE;
      DROP TABLE IF EXISTS user_sessions CASCADE;
      DROP TABLE IF EXISTS users CASCADE;
      DROP TABLE IF EXISTS tenants CASCADE;
    `;
    
    await pool.query(dropTablesSQL);
    console.log('✅ Existing tables dropped');
    
    // Drop triggers and functions
    console.log('🧹 Cleaning up triggers and functions...');
    await pool.query('DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;');
    console.log('✅ Triggers and functions cleaned');
    
    // Read and execute schema file
    const schemaPath = path.join(__dirname, 'schema.sql');
    const schemaSQL = fs.readFileSync(schemaPath, 'utf8');
    
    console.log('📋 Executing database schema...');
    await pool.query(schemaSQL);
    console.log('✅ Database schema executed successfully');
    
    console.log('🎉 Database reset completed successfully!');
    console.log('\n📊 Sample data created:');
    console.log('- Demo School District (tenant)');
    console.log('- Super Admin user (superadmin@edtech.com)');
    console.log('- Demo Elementary School');
    console.log('\n🔑 Default superadmin password: admin123');
    
  } catch (error) {
    console.error('❌ Error resetting database:', error.message);
    throw error;
  } finally {
    await pool.end();
  }
}

// Run reset if this file is executed directly
if (require.main === module) {
  resetDatabase()
    .then(() => {
      console.log('✅ Database reset completed');
      process.exit(0);
    })
    .catch((error) => {
      console.error('❌ Database reset failed:', error);
      process.exit(1);
    });
}

module.exports = { resetDatabase }; 