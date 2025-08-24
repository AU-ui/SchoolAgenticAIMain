const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function verifyAdminDashboard() {
  console.log('🔍 Verifying Admin Dashboard Functionality...\n');
  
  try {
    // 1. Check if we have schools
    const schools = await pool.query('SELECT id, name FROM schools WHERE is_active = true');
    console.log(`✅ Schools available: ${schools.rows.length}`);
    schools.rows.forEach(school => {
      console.log(`   - ${school.name} (ID: ${school.id})`);
    });
    
    if (schools.rows.length === 0) {
      console.log('❌ No schools found!');
      return;
    }
    
    const testSchool = schools.rows[0];
    
    // 2. Check if we have classes for this school
    const classes = await pool.query(`
      SELECT id, name, grade_level 
      FROM classes 
      WHERE school_id = $1 AND is_active = true
    `, [testSchool.id]);
    
    console.log(`\n✅ Classes for ${testSchool.name}: ${classes.rows.length}`);
    classes.rows.forEach(cls => {
      console.log(`   - ${cls.name} (Grade ${cls.grade_level}, ID: ${cls.id})`);
    });
    
    if (classes.rows.length === 0) {
      console.log('❌ No classes found!');
      return;
    }
    
    const testClass = classes.rows[0];
    
    // 3. Check if we have students in this class
    const students = await pool.query(`
      SELECT s.id, u.first_name, u.last_name 
      FROM students s 
      JOIN users u ON s.user_id = u.id 
      WHERE s.class_id = $1 AND s.is_active = true
    `, [testClass.id]);
    
    console.log(`\n✅ Students in ${testClass.name}: ${students.rows.length}`);
    students.rows.forEach(student => {
      console.log(`   - ${student.first_name} ${student.last_name} (ID: ${student.id})`);
    });
    
    if (students.rows.length === 0) {
      console.log('❌ No students found!');
      return;
    }
    
    // 4. Check attendance data for July 2025
    const julyAttendance = await pool.query(`
      SELECT COUNT(*) as count 
      FROM attendance_records ar
      JOIN students st ON ar.student_id::text = st.id::text
      WHERE st.class_id = $1 
        AND EXTRACT(MONTH FROM ar.date) = 7 
        AND EXTRACT(YEAR FROM ar.date) = 2025
    `, [testClass.id]);
    
    console.log(`\n✅ July 2025 attendance records: ${julyAttendance.rows[0].count}`);
    
    // 5. Test the exact admin API query
    console.log('\n🧪 Testing Admin API Query...');
    
    const apiQuery = await pool.query(`
      SELECT 
        ar.student_id,
        ar.status,
        ar.date,
        s.first_name || ' ' || s.last_name as student_name
      FROM attendance_records ar
      JOIN students st ON ar.student_id::text = st.id::text
      JOIN users s ON st.user_id = s.id
      WHERE st.class_id = $1 
        AND EXTRACT(MONTH FROM ar.date) = 7 
        AND EXTRACT(YEAR FROM ar.date) = 2025
      ORDER BY ar.date, s.first_name, s.last_name
      LIMIT 5
    `, [testClass.id]);
    
    console.log(`✅ Admin API query returned ${apiQuery.rows.length} records`);
    
    if (apiQuery.rows.length > 0) {
      console.log('Sample records:');
      apiQuery.rows.forEach((record, index) => {
        console.log(`   ${index + 1}. ${record.student_name} - ${record.status} on ${record.date}`);
      });
    }
    
    // 6. Summary
    console.log('\n📊 SUMMARY:');
    console.log(`✅ Schools: ${schools.rows.length}`);
    console.log(`✅ Classes: ${classes.rows.length}`);
    console.log(`✅ Students: ${students.rows.length}`);
    console.log(`✅ July 2025 Attendance Records: ${julyAttendance.rows[0].count}`);
    console.log(`✅ API Query Working: ${apiQuery.rows.length > 0 ? 'YES' : 'NO'}`);
    
    if (apiQuery.rows.length > 0) {
      console.log('\n🎉 ADMIN DASHBOARD SHOULD BE WORKING!');
      console.log('📝 To test:');
      console.log(`   1. Go to admin dashboard`);
      console.log(`   2. Select school: ${testSchool.name}`);
      console.log(`   3. Select class: ${testClass.name}`);
      console.log(`   4. Select month: July`);
      console.log(`   5. Select year: 2025`);
      console.log(`   6. Attendance table should show data`);
    } else {
      console.log('\n❌ ADMIN DASHBOARD STILL HAS ISSUES');
      console.log('📝 Need to create more attendance data');
    }
    
  } catch (error) {
    console.error('❌ Verification failed:', error);
  } finally {
    await pool.end();
  }
}

verifyAdminDashboard();
