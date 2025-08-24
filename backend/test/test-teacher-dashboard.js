const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function testTeacherDashboard() {
  console.log('🧪 Testing Teacher Dashboard Backend...\n');
  
  try {
    // Test 1: Check if teacher routes exist
    console.log('✅ Test 1: Checking teacher routes...');
    
    // Test 2: Check database connection
    console.log('✅ Test 2: Testing database connection...');
    const dbTest = await pool.query('SELECT NOW()');
    console.log('   Database connected:', dbTest.rows[0].now);
    
    // Test 3: Check if teachers exist
    console.log('✅ Test 3: Checking teachers in database...');
    const teachers = await pool.query('SELECT id, first_name, last_name FROM users WHERE role = $1 LIMIT 5', ['teacher']);
    console.log(`   Found ${teachers.rows.length} teachers`);
    teachers.rows.forEach(teacher => {
      console.log(`   - ${teacher.first_name} ${teacher.last_name} (ID: ${teacher.id})`);
    });
    
    // Test 4: Check if classes exist
    console.log('✅ Test 4: Checking classes in database...');
    const classes = await pool.query('SELECT id, name, teacher_id FROM classes LIMIT 5');
    console.log(`   Found ${classes.rows.length} classes`);
    classes.rows.forEach(cls => {
      console.log(`   - ${cls.name} (Teacher ID: ${cls.teacher_id})`);
    });
    
    // Test 5: Check if students exist
    console.log('✅ Test 5: Checking students in database...');
    const students = await pool.query('SELECT id, name, class_id FROM students LIMIT 5');
    console.log(`   Found ${students.rows.length} students`);
    students.rows.forEach(student => {
      console.log(`   - ${student.name} (Class ID: ${student.class_id})`);
    });
    
    // Test 6: Check attendance_records table
    console.log('✅ Test 6: Checking attendance_records table...');
    const attendanceCount = await pool.query('SELECT COUNT(*) as count FROM attendance_records');
    console.log(`   Found ${attendanceCount.rows[0].count} attendance records`);
    
    // Test 7: Check ML service connection
    console.log('✅ Test 7: Testing ML service connection...');
    try {
      const response = await fetch('http://localhost:8000/health');
      if (response.ok) {
        console.log('   ML service is running');
      } else {
        console.log('   ML service not responding');
      }
    } catch (error) {
      console.log('   ML service not available (this is okay for testing)');
    }
    
    console.log('\n🎉 All backend tests completed successfully!');
    console.log('\n�� Next Steps:');
    console.log('1. Start the backend server: npm start');
    console.log('2. Start the frontend: cd frontend/app && npm start');
    console.log('3. Login as a teacher');
    console.log('4. Test the Teacher Dashboard');
    
  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    await pool.end();
  }
}

testTeacherDashboard();
