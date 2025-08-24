const { Pool } = require('pg');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function createJuly2025Data() {
  console.log('�� Creating July 2025 Data...\n');
  
  try {
    // Get a student with class
    const student = await pool.query(`
      SELECT 
        s.id as student_id,
        s.class_id,
        u.first_name,
        u.last_name,
        c.name as class_name
      FROM students s
      JOIN users u ON s.user_id = u.id
      JOIN classes c ON s.class_id = c.id
      WHERE s.is_active = true
      LIMIT 1
    `);
    
    if (student.rows.length === 0) {
      console.log('❌ No students found!');
      return;
    }
    
    const testStudent = student.rows[0];
    console.log(`✅ Using student: ${testStudent.first_name} ${testStudent.last_name} in ${testStudent.class_name}`);
    
    // Create July 2025 data (school days only)
    const julyDates = [
      '2025-07-01', '2025-07-02', '2025-07-03', '2025-07-07', '2025-07-08',
      '2025-07-09', '2025-07-10', '2025-07-11', '2025-07-14', '2025-07-15',
      '2025-07-16', '2025-07-17', '2025-07-18', '2025-07-21', '2025-07-22',
      '2025-07-23', '2025-07-24', '2025-07-25', '2025-07-28', '2025-07-29', '2025-07-30'
    ];
    
    console.log(`📅 Creating ${julyDates.length} attendance records for July 2025`);
    
    for (const dateString of julyDates) {
      const sessionId = uuidv4();
      
      // Create session
      await pool.query(`
        INSERT INTO attendance_sessions (id, created_at, is_active) 
        VALUES ($1, $2, true)
        ON CONFLICT (id) DO NOTHING
      `, [sessionId, dateString]);
      
      // Create attendance record
      await pool.query(`
        INSERT INTO attendance_records (class_id, student_id, session_id, status, date, created_at) 
        VALUES ($1, $2, $3, $4, $5, NOW())
        ON CONFLICT DO NOTHING
      `, [testStudent.class_id, testStudent.student_id.toString(), sessionId, 'present', dateString]);
    }
    
    console.log('✅ July 2025 data created successfully');
    
    // Verify
    const verification = await pool.query(`
      SELECT COUNT(*) as count 
      FROM attendance_records ar
      JOIN students st ON ar.student_id::text = st.id::text
      WHERE st.class_id = $1 
        AND EXTRACT(MONTH FROM ar.date) = 7 
        AND EXTRACT(YEAR FROM ar.date) = 2025
    `, [testStudent.class_id]);
    
    console.log(`✅ Verification: ${verification.rows[0].count} July 2025 records found`);
    
    if (verification.rows[0].count > 0) {
      console.log('\n�� SUCCESS! July 2025 data created.');
      console.log(' Now test the admin dashboard:');
      console.log(`   1. Select school with class: ${testStudent.class_name}`);
      console.log(`   2. Select month: July`);
      console.log(`   3. Select year: 2025`);
      console.log(`   4. Attendance table should show data for ${testStudent.first_name} ${testStudent.last_name}`);
    }
    
  } catch (error) {
    console.error('❌ Error creating July 2025 data:', error);
  } finally {
    await pool.end();
  }
}

createJuly2025Data();
