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

async function setupDatabase() {
  console.log('🚀 Starting database setup...');
  
  // First, connect to PostgreSQL without specifying a database
  const postgresConfig = { ...dbConfig, database: 'postgres' };
  const postgresPool = new Pool(postgresConfig);
  
  try {
    // Check if database exists, if not create it
    const dbExists = await postgresPool.query(
      "SELECT 1 FROM pg_database WHERE datname = $1",
      [dbConfig.database]
    );
    
    if (dbExists.rows.length === 0) {
      console.log(`📦 Creating database: ${dbConfig.database}`);
      await postgresPool.query(`CREATE DATABASE ${dbConfig.database}`);
      console.log('✅ Database created successfully');
    } else {
      console.log(`✅ Database ${dbConfig.database} already exists`);
    }
  } catch (error) {
    console.error('❌ Error creating database:', error.message);
    throw error;
  } finally {
    await postgresPool.end();
  }
  
  // Now connect to the specific database
  const pool = new Pool(dbConfig);
  
  try {
    // Read and execute schema file
    const schemaPath = path.join(__dirname, 'schema.sql');
    const schemaSQL = fs.readFileSync(schemaPath, 'utf8');
    
    console.log('📋 Executing database schema...');
    await pool.query(schemaSQL);
    console.log('✅ Database schema executed successfully');
    
    console.log('🎉 Database setup completed successfully!');
    console.log('\n📊 Sample data created:');
    console.log('- Demo School District (tenant)');
    console.log('- Super Admin user (superadmin@edtech.com)');
    console.log('- Demo Elementary School');
    console.log('\n🔑 Default superadmin password: admin123');
    
  } catch (error) {
    console.error('❌ Error setting up database:', error.message);
    throw error;
  } finally {
    await pool.end();
  }
}

// Run setup if this file is executed directly
if (require.main === module) {
  setupDatabase()
    .then(() => {
      console.log('✅ Database setup completed');
      process.exit(0);
    })
    .catch((error) => {
      console.error('❌ Database setup failed:', error);
      process.exit(1);
    });
}

module.exports = { setupDatabase }; 