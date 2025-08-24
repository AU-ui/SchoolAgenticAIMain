const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function diagnoseAdminDashboard() {
  console.log('🔍 Diagnosing Admin Dashboard Attendance Issue...\n');
  
  try {
    // 1. Check current data in key tables
    console.log('📊 Checking current data...');
    
    const schoolsCount = await pool.query('SELECT COUNT(*) FROM schools');
    const classesCount = await pool.query('SELECT COUNT(*) FROM classes');
    const studentsCount = await pool.query('SELECT COUNT(*) FROM students');
    const attendanceCount = await pool.query('SELECT COUNT(*) FROM attendance_records');
    
    console.log(`- Schools: ${schoolsCount.rows[0].count}`);
    console.log(`- Classes: ${classesCount.rows[0].count}`);
    console.log(`- Students: ${studentsCount.rows[0].count}`);
    console.log(`- Attendance Records: ${attendanceCount.rows[0].count}\n`);
    
    // 2. Check attendance_records table structure
    console.log('📋 Checking attendance_records structure...');
    const columns = await pool.query(`
      SELECT column_name, data_type 
      FROM information_schema.columns 
      WHERE table_name = 'attendance_records' 
      ORDER BY ordinal_position
    `);
    
    console.log('Attendance records columns:');
    columns.rows.forEach(col => {
      console.log(`  - ${col.column_name}: ${col.data_type}`);
    });
    console.log();
    
    // 3. Check students table structure
    console.log('📋 Checking students table structure...');
    const studentColumns = await pool.query(`
      SELECT column_name, data_type 
      FROM information_schema.columns 
      WHERE table_name = 'students' 
      ORDER BY ordinal_position
    `);
    
    console.log('Students table columns:');
    studentColumns.rows.forEach(col => {
      console.log(`  - ${col.column_name}: ${col.data_type}`);
    });
    console.log();
    
    // 4. Check sample data relationships
    console.log('🔗 Checking data relationships...');
    
    // Get a sample school and its classes
    const sampleSchool = await pool.query(`
      SELECT s.id, s.name, s.tenant_id 
      FROM schools s 
      WHERE s.is_active = true 
      LIMIT 1
    `);
    
    if (sampleSchool.rows.length === 0) {
      console.log('❌ No active schools found!');
      return;
    }
    
    const school = sampleSchool.rows[0];
    console.log(`✅ Found school: ${school.name} (ID: ${school.id})`);
    
    // Get classes for this school
    const classes = await pool.query(`
      SELECT c.id, c.name, c.grade_level 
      FROM classes c 
      WHERE c.school_id = $1 AND c.is_active = true
    `, [school.id]);
    
    console.log(`✅ Found ${classes.rows.length} classes for this school`);
    
    if (classes.rows.length === 0) {
      console.log('❌ No classes found for this school!');
      return;
    }
    
    const sampleClass = classes.rows[0];
    console.log(`✅ Sample class: ${sampleClass.name} (ID: ${sampleClass.id})`);
    
    // Get students for this class
    const students = await pool.query(`
      SELECT s.id, s.user_id, u.first_name, u.last_name 
      FROM students s 
      JOIN users u ON s.user_id = u.id 
      WHERE s.class_id = $1 AND s.is_active = true
    `, [sampleClass.id]);
    
    console.log(`✅ Found ${students.rows.length} students in this class`);
    
    if (students.rows.length === 0) {
      console.log('❌ No students found in this class!');
      return;
    }
    
    // 5. Check if attendance data exists (FIXED: Handle UUID vs integer mismatch)
    console.log('\n📅 Checking attendance data...');
    const currentMonth = new Date().getMonth() + 1;
    const currentYear = new Date().getFullYear();
    
    // Check if attendance_records uses UUID or integer for student_id
    const attendanceData = await pool.query(`
      SELECT COUNT(*) as count 
      FROM attendance_records ar
      JOIN students st ON ar.student_id::text = st.id::text
      WHERE st.class_id = $1 
        AND EXTRACT(MONTH FROM ar.date) = $2 
        AND EXTRACT(YEAR FROM ar.date) = $3
    `, [sampleClass.id, currentMonth, currentYear]);
    
    console.log(`✅ Attendance records for ${currentMonth}/${currentYear}: ${attendanceData.rows[0].count}`);
    
    // 6. Test the exact query from the admin API (FIXED: Handle UUID vs integer mismatch)
    console.log('\n🧪 Testing admin API query...');
    try {
      const testQuery = await pool.query(`
        SELECT 
          ar.student_id,
          ar.status,
          ar.date,
          ar.session_id,
          s.first_name || ' ' || s.last_name as student_name,
          u.first_name || ' ' || u.last_name as teacher_name
        FROM attendance_records ar
        JOIN students st ON ar.student_id::text = st.id::text
        JOIN users s ON st.user_id = s.id
        JOIN classes c ON st.class_id = c.id
        LEFT JOIN users u ON c.teacher_id = u.id
        WHERE st.class_id = $1 
          AND EXTRACT(MONTH FROM ar.date) = $2 
          AND EXTRACT(YEAR FROM ar.date) = $3
        ORDER BY ar.date, s.first_name, s.last_name
      `, [sampleClass.id, currentMonth, currentYear]);
      
      console.log(`✅ Admin API query returned ${testQuery.rows.length} records`);
      
      if (testQuery.rows.length > 0) {
        console.log('Sample record:', testQuery.rows[0]);
      }
      
    } catch (error) {
      console.log('❌ Admin API query failed:', error.message);
    }
    
    // 7. Create test attendance data if none exists
    if (attendanceData.rows[0].count === 0) {
      console.log('\n📝 Creating test attendance data...');
      await createTestAttendanceData(pool, students.rows, sampleClass.id);
    }
    
  } catch (error) {
    console.error('❌ Diagnostic failed:', error);
  } finally {
    await pool.end();
  }
}

async function createTestAttendanceData(pool, students, classId) {
  try {
    // Create attendance sessions for the last 10 days
    const sessionIds = [];
    const today = new Date();
    
    for (let i = 9; i >= 0; i--) {
      const sessionDate = new Date(today);
      sessionDate.setDate(today.getDate() - i);
      
      const sessionId = `session_${Date.now()}_${i}`;
      const dateString = sessionDate.toISOString().split('T')[0];
      
      await pool.query(`
        INSERT INTO attendance_sessions (id, class_id, created_at, expires_at, is_active) 
        VALUES ($1, $2, $3, $4, true)
        ON CONFLICT (id) DO NOTHING
      `, [sessionId, classId, dateString, new Date(Date.now() + 86400000)]);
      
      sessionIds.push({ id: sessionId, date: dateString });
    }
    
    console.log(`✅ Created ${sessionIds.length} attendance sessions`);
    
    // Create attendance records for each student
    for (const student of students) {
      for (const session of sessionIds) {
        // Create varied attendance patterns
        let status;
        const random = Math.random();
        if (random > 0.8) {
          status = 'absent';
        } else if (random > 0.6) {
          status = 'late';
        } else {
          status = 'present';
        }
        
        await pool.query(`
          INSERT INTO attendance_records (class_id, student_id, session_id, status, date, created_at) 
          VALUES ($1, $2, $3, $4, $5, NOW())
          ON CONFLICT DO NOTHING
        `, [classId, student.id, session.id, status, session.date]);
      }
    }
    
    console.log(`✅ Created attendance records for ${students.length} students`);
    
  } catch (error) {
    console.error('❌ Error creating test data:', error);
  }
}

diagnoseAdminDashboard();
