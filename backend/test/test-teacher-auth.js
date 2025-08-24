const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function testTeacherAuth() {
  console.log('🔐 Testing Teacher Authentication...\n');
  
  try {
    // Step 1: Get a valid teacher
    console.log('✅ Step 1: Getting a valid teacher...');
    const teacher = await pool.query(`
      SELECT id, first_name, last_name, email, role 
      FROM users 
      WHERE role = 'teacher' AND is_active = true 
      LIMIT 1
    `);
    
    if (teacher.rows.length === 0) {
      console.log('❌ No active teachers found');
      return;
    }
    
    const teacherData = teacher.rows[0];
    console.log(`   Found teacher: ${teacherData.first_name} ${teacherData.last_name} (ID: ${teacherData.id})`);
    
    // Step 2: Check teacher's classes
    console.log('\n✅ Step 2: Checking teacher classes...');
    const teacherClasses = await pool.query(`
      SELECT id, name, grade_level, academic_year, is_active
      FROM classes 
      WHERE teacher_id = $1 AND is_active = true
      ORDER BY name
    `, [teacherData.id]);
    
    console.log(`   Teacher has ${teacherClasses.rows.length} classes:`);
    teacherClasses.rows.forEach(cls => {
      console.log(`   - ${cls.name} (Grade ${cls.grade_level})`);
    });
    
    // Step 3: Test the API endpoint with proper authentication
    console.log('\n✅ Step 3: Testing API endpoint...');
    console.log('   To test the API, you need to:');
    console.log('   1. Login as a teacher in the frontend');
    console.log('   2. Check the browser console for the token');
    console.log('   3. Use that token to test the API');
    
    console.log('\n📋 Test Credentials:');
    console.log(`   Email: ${teacherData.email}`);
    console.log(`   Teacher ID: ${teacherData.id}`);
    console.log(`   Role: ${teacherData.role}`);
    
    console.log('\n�� Manual Test Steps:');
    console.log('   1. Go to frontend and login with teacher credentials');
    console.log('   2. Open browser developer tools (F12)');
    console.log('   3. Go to Application/Storage tab');
    console.log('   4. Check localStorage for "token"');
    console.log('   5. Copy the token and test the API manually');
    
    console.log('\n�� API Test Command (replace YOUR_TOKEN):');
    console.log('   curl -X GET http://localhost:5000/api/teacher/classes \\');
    console.log('     -H "Authorization: Bearer YOUR_TOKEN" \\');
    console.log('     -H "Content-Type: application/json"');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    await pool.end();
  }
}

testTeacherAuth();
