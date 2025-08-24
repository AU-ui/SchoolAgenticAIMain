const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function diagnoseClass35() {
  console.log('🔍 Diagnosing Class 35 Issue...\n');
  
  try {
    const classId = 35;
    const teacherId = 116; // Anil Upadhyay
    const date = '2025-08-21';
    
    // Test 1: Check if class exists
    console.log('✅ Test 1: Check if class 35 exists');
    const classCheck = await pool.query(`
      SELECT id, name, teacher_id, is_active 
      FROM classes 
      WHERE id = $1
    `, [classId]);
    
    if (classCheck.rows.length === 0) {
      console.log('❌ Class 35 does not exist');
      return;
    }
    
    const classData = classCheck.rows[0];
    console.log(`   Class: ${classData.name} (ID: ${classData.id})`);
    console.log(`   Teacher ID: ${classData.teacher_id}`);
    console.log(`   Active: ${classData.is_active}`);
    
    // Test 2: Check if teacher owns this class
    console.log('\n✅ Test 2: Check teacher ownership');
    if (classData.teacher_id !== teacherId) {
      console.log(`❌ Teacher ${teacherId} does not own class ${classId}`);
      console.log(`   Class is owned by teacher ${classData.teacher_id}`);
      return;
    }
    console.log('✅ Teacher owns this class');
    
    // Test 3: Check if students exist in this class
    console.log('\n✅ Test 3: Check students in class');
    const studentsCheck = await pool.query(`
      SELECT COUNT(*) as count
      FROM students 
      WHERE class_id = $1 AND is_active = true
    `, [classId]);
    
    const studentCount = studentsCheck.rows[0].count;
    console.log(`   Students in class: ${studentCount}`);
    
    if (studentCount === 0) {
      console.log('❌ No students in this class');
      return;
    }
    
    // Test 4: Test the exact query that's failing
    console.log('\n✅ Test 4: Test the exact query');
    const testQuery = `
      SELECT 
        s.id,
        s.student_id as student_code,
        CONCAT(u.first_name, ' ', u.last_name) as name,
        u.email,
        u.profile_picture_url as photo_url,
        COALESCE(ar.status, 'not_marked') as attendance_status,
        ar.notes,
        ar.created_at as marked_at
      FROM students s
      JOIN users u ON s.user_id = u.id
      LEFT JOIN attendance_records ar ON s.id = ar.student_id 
        AND ar.class_id = $1 
        AND DATE(ar.created_at) = $2
      WHERE s.class_id = $1 AND s.is_active = true
      ORDER BY u.first_name, u.last_name
    `;
    
    try {
      const studentsResult = await pool.query(testQuery, [classId, date]);
      console.log(`✅ Query successful! Found ${studentsResult.rows.length} students:`);
      
      studentsResult.rows.forEach((student, index) => {
        console.log(`   ${index + 1}. ${student.name} (${student.email}) - ${student.attendance_status}`);
      });
      
    } catch (queryError) {
      console.error('❌ Query failed:', queryError.message);
      console.error('   Error details:', queryError);
    }
    
    // Test 5: Check attendance_records table structure
    console.log('\n✅ Test 5: Check attendance_records structure');
    const attendanceStructure = await pool.query(`
      SELECT column_name, data_type, is_nullable 
      FROM information_schema.columns 
      WHERE table_name = 'attendance_records' 
      ORDER BY ordinal_position
    `);
    
    console.log('   Attendance records columns:');
    attendanceStructure.rows.forEach(col => {
      console.log(`   - ${col.column_name}: ${col.data_type} (nullable: ${col.is_nullable})`);
    });
    
  } catch (error) {
    console.error('❌ Diagnosis failed:', error);
  } finally {
    await pool.end();
  }
}

diagnoseClass35();
