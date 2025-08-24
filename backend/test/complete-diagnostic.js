const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function completeDiagnostic() {
  console.log('🔍 Complete Admin Dashboard Diagnostic...\n');
  
  try {
    // 1. Check all data
    console.log('📊 Current Data Status:');
    
    const schools = await pool.query('SELECT COUNT(*) FROM schools WHERE is_active = true');
    const classes = await pool.query('SELECT COUNT(*) FROM classes WHERE is_active = true');
    const students = await pool.query('SELECT COUNT(*) FROM students WHERE is_active = true');
    const sessions = await pool.query('SELECT COUNT(*) FROM attendance_sessions');
    const records = await pool.query('SELECT COUNT(*) FROM attendance_records');
    
    console.log(`✅ Schools: ${schools.rows[0].count}`);
    console.log(`✅ Classes: ${classes.rows[0].count}`);
    console.log(`✅ Students: ${students.rows[0].count}`);
    console.log(`✅ Sessions: ${sessions.rows[0].count}`);
    console.log(`✅ Records: ${records.rows[0].count}`);
    
    // 2. Get a specific school and class to test
    const testData = await pool.query(`
      SELECT 
        s.id as school_id,
        s.name as school_name,
        c.id as class_id,
        c.name as class_name,
        st.id as student_id,
        u.first_name,
        u.last_name
      FROM schools s
      JOIN classes c ON s.id = c.school_id
      JOIN students st ON c.id = st.class_id
      JOIN users u ON st.user_id = u.id
      WHERE s.is_active = true AND c.is_active = true AND st.is_active = true
      LIMIT 1
    `);
    
    if (testData.rows.length === 0) {
      console.log('\n❌ No complete data chain found!');
      return;
    }
    
    const test = testData.rows[0];
    console.log(`\n🎯 Test Data: ${test.first_name} ${test.last_name} in ${test.class_name} at ${test.school_name}`);
    
    // 3. Check attendance records for this specific student
    const studentRecords = await pool.query(`
      SELECT COUNT(*) as count 
      FROM attendance_records 
      WHERE student_id::text = $1
    `, [test.student_id.toString()]);
    
    console.log(`\n�� Attendance records for ${test.first_name}: ${studentRecords.rows[0].count}`);
    
    if (studentRecords.rows[0].count > 0) {
      const sampleRecords = await pool.query(`
        SELECT date, status FROM attendance_records 
        WHERE student_id::text = $1
        ORDER BY date DESC
        LIMIT 5
      `, [test.student_id.toString()]);
      
      console.log('Recent attendance dates:');
      sampleRecords.rows.forEach(record => {
        console.log(`  - ${record.date}: ${record.status}`);
      });
    }
    
    // 4. Test the exact admin API query
    console.log('\n🧪 Testing Admin API Query...');
    
    // Test with August 2025 (since we know data exists for August)
    const augustQuery = await pool.query(`
      SELECT 
        ar.student_id,
        ar.status,
        ar.date,
        s.first_name || ' ' || s.last_name as student_name
      FROM attendance_records ar
      JOIN students st ON ar.student_id::text = st.id::text
      JOIN users s ON st.user_id = s.id
      WHERE st.class_id = $1 
        AND EXTRACT(MONTH FROM ar.date) = 8 
        AND EXTRACT(YEAR FROM ar.date) = 2025
      ORDER BY ar.date, s.first_name, s.last_name
    `, [test.class_id]);
    
    console.log(`✅ August 2025 query returned: ${augustQuery.rows.length} records`);
    
    // Test with July 2025
    const julyQuery = await pool.query(`
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
    `, [test.class_id]);
    
    console.log(`✅ July 2025 query returned: ${julyQuery.rows.length} records`);
    
    // 5. Test without date filter
    const allQuery = await pool.query(`
      SELECT 
        ar.student_id,
        ar.status,
        ar.date,
        s.first_name || ' ' || s.last_name as student_name
      FROM attendance_records ar
      JOIN students st ON ar.student_id::text = st.id::text
      JOIN users s ON st.user_id = s.id
      WHERE st.class_id = $1
      ORDER BY ar.date DESC
      LIMIT 5
    `, [test.class_id]);
    
    console.log(`✅ All records query returned: ${allQuery.rows.length} records`);
    
    // 6. Summary and recommendations
    console.log('\n�� DIAGNOSTIC SUMMARY:');
    console.log(`✅ School: ${test.school_name} (ID: ${test.school_id})`);
    console.log(`✅ Class: ${test.class_name} (ID: ${test.class_id})`);
    console.log(`✅ Student: ${test.first_name} ${test.last_name} (ID: ${test.student_id})`);
    console.log(`✅ Student Records: ${studentRecords.rows[0].count}`);
    console.log(`✅ August 2025 API Query: ${augustQuery.rows.length} records`);
    console.log(`✅ July 2025 API Query: ${julyQuery.rows.length} records`);
    console.log(`✅ All Records API Query: ${allQuery.rows.length} records`);
    
    if (augustQuery.rows.length > 0) {
      console.log('\n🎉 ADMIN DASHBOARD SHOULD WORK WITH AUGUST 2025!');
      console.log('📝 To test:');
      console.log(`   1. Go to admin dashboard`);
      console.log(`   2. Select school: ${test.school_name}`);
      console.log(`   3. Select class: ${test.class_name}`);
      console.log(`   4. Select month: August (8)`);
      console.log(`   5. Select year: 2025`);
      console.log(`   6. Attendance table should show data`);
    } else if (allQuery.rows.length > 0) {
      console.log('\n🔍 ISSUE: API query works but date filtering fails');
      console.log('�� Need to check date format in attendance_records');
    } else {
      console.log('\n❌ ISSUE: No data found for this class');
      console.log('📝 Need to create attendance data for this class');
    }
    
  } catch (error) {
    console.error('❌ Diagnostic failed:', error);
  } finally {
    await pool.end();
  }
}

completeDiagnostic();
