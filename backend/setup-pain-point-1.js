const { Pool } = require('pg');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function setupPainPoint1() {
  const client = await pool.connect();
  
  try {
    console.log('🚀 Setting up Pain Point #1 database tables...');

    // Read and execute the integration SQL
    const sqlPath = path.join(__dirname, 'database', 'pain_point_1_integration.sql');
    const sqlContent = fs.readFileSync(sqlPath, 'utf8');
    
    await client.query(sqlContent);
    
    console.log('✅ Pain Point #1 database tables created successfully!');
    console.log('\n📋 Created tables:');
    console.log('- attendance_sessions');
    console.log('- attendance_records');
    console.log('- teacher_tasks');
    console.log('- classroom_resources');
    console.log('- resource_bookings');
    console.log('- assignments');
    console.log('- student_grades');
    console.log('- class_schedules');
    console.log('- report_templates');
    console.log('- ml_insights');
    console.log('- substitute_requests');
    
    console.log('\n🎉 Pain Point #1 database setup completed!');
    console.log('You can now use all teacher features.');

  } catch (error) {
    console.error('❌ Pain Point #1 setup failed:', error);
    throw error;
  } finally {
    client.release();
  }
}

setupPainPoint1()
  .then(() => {
    console.log('🎉 Setup completed!');
    process.exit(0);
  })
  .catch((error) => {
    console.error('💥 Setup failed:', error);
    process.exit(1);
  }); 