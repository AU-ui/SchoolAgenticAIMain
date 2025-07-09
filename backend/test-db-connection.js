const { Pool } = require('pg');
require('dotenv').config();

console.log('🔍 Testing PostgreSQL connection...\n');

// Display current configuration (without password)
console.log('📋 Current configuration:');
console.log(`Host: ${process.env.DB_HOST || 'localhost'}`);
console.log(`Port: ${process.env.DB_PORT || 5432}`);
console.log(`Database: ${process.env.DB_NAME || 'edtech_platform'}`);
console.log(`User: ${process.env.DB_USER || 'postgres'}`);
console.log(`Password: ${process.env.DB_PASSWORD ? '***SET***' : '***NOT SET***'}\n`);

// Database configuration
const dbConfig = {
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: 'postgres', // Connect to default postgres database first
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
};

console.log('🔌 Attempting to connect to PostgreSQL...');

const pool = new Pool(dbConfig);

pool.on('error', (err) => {
  console.error('❌ Unexpected error on idle client', err);
  process.exit(-1);
});

async function testConnection() {
  try {
    const client = await pool.connect();
    console.log('✅ Successfully connected to PostgreSQL!');
    
    // Test basic query
    const result = await client.query('SELECT version()');
    console.log('📊 PostgreSQL version:', result.rows[0].version);
    
    // Check if our target database exists
    const dbCheck = await client.query(
      "SELECT 1 FROM pg_database WHERE datname = $1",
      [process.env.DB_NAME || 'edtech_platform']
    );
    
    if (dbCheck.rows.length > 0) {
      console.log(`✅ Database '${process.env.DB_NAME || 'edtech_platform'}' exists`);
    } else {
      console.log(`⚠️  Database '${process.env.DB_NAME || 'edtech_platform'}' does not exist`);
      console.log('💡 Run "npm run db:setup" to create it');
    }
    
    client.release();
    await pool.end();
    
    console.log('\n🎉 Connection test completed successfully!');
    return true;
    
  } catch (error) {
    console.error('\n❌ Connection failed with error:');
    console.error('Error code:', error.code);
    console.error('Error message:', error.message);
    
    if (error.code === '28P01') {
      console.log('\n💡 This is a password authentication error.');
      console.log('Please check:');
      console.log('1. Your DB_PASSWORD in .env file');
      console.log('2. That the password matches your PostgreSQL user password');
      console.log('3. That the DB_USER is correct');
    } else if (error.code === 'ECONNREFUSED') {
      console.log('\n💡 PostgreSQL server is not running or not accessible.');
      console.log('Please start PostgreSQL service.');
    } else if (error.code === 'ENOTFOUND') {
      console.log('\n💡 Cannot find PostgreSQL server.');
      console.log('Please check your DB_HOST setting.');
    }
    
    await pool.end();
    return false;
  }
}

// Run the test
testConnection()
  .then((success) => {
    process.exit(success ? 0 : 1);
  })
  .catch((error) => {
    console.error('❌ Test failed:', error);
    process.exit(1);
  }); 