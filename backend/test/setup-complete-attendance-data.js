const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function setupCompleteAttendanceData() {
  console.log('🚀 Setting up Complete Attendance System Data...\n');
  
  try {
    // 1. Create a test school
    console.log('📚 Creating test school...');
    const schoolResult = await pool.query(`
      INSERT INTO schools (name, address, phone, email, principal_name, is_active)
      VALUES ('Smith High School', '123 Education Street', '+1-555-0123', 'admin@smithschool.edu', 'Dr. John Smith', true)
      ON CONFLICT (name) DO UPDATE SET is_active = true
      RETURNING id
    `);
    const schoolId = schoolResult.rows[0].id;
    console.log(`✅ School created/updated: ID ${schoolId}`);

    // 2. Create test teacher
    console.log('👨‍🏫 Creating test teacher...');
    const teacherResult = await pool.query(`
      INSERT INTO users (email, password, first_name, last_name, role, is_active, email_verified)
      VALUES ('teacher@smithschool.edu', '$2a$10$testpassword', 'Sarah', 'Johnson', 'teacher', true, true)
      ON CONFLICT (email) DO UPDATE SET is_active = true
      RETURNING id
    `);
    const teacherId = teacherResult.rows[0].id;
    console.log(`✅ Teacher created/updated: ID ${teacherId}`);

    // 3. Create test classes
    console.log('📖 Creating test classes...');
    const classes = [
      { name: 'Mathematics 101', grade_level: 9, academic_year: '2024-2025' },
      { name: 'Science 101', grade_level: 9, academic_year: '2024-2025' },
      { name: 'English 101', grade_level: 9, academic_year: '2024-2025' }
    ];

    const classIds = [];
    for (const cls of classes) {
      const classResult = await pool.query(`
        INSERT INTO classes (school_id, name, grade_level, academic_year, teacher_id, is_active)
        VALUES ($1, $2, $3, $4, $5, true)
        ON CONFLICT (school_id, name, academic_year) DO UPDATE SET is_active = true
        RETURNING id
      `, [schoolId, cls.name, cls.grade_level, cls.academic_year, teacherId]);
      classIds.push(classResult.rows[0].id);
      console.log(`✅ Class created: ${cls.name} (ID: ${classResult.rows[0].id})`);
    }

    // 4. Create test students
    console.log('👨‍🎓 Creating test students...');
    const students = [
      { first_name: 'Alice', last_name: 'Brown', email: 'alice.brown@student.edu' },
      { first_name: 'Bob', last_name: 'Wilson', email: 'bob.wilson@student.edu' },
      { first_name: 'Charlie', last_name: 'Davis', email: 'charlie.davis@student.edu' },
      { first_name: 'Diana', last_name: 'Miller', email: 'diana.miller@student.edu' },
      { first_name: 'Eve', last_name: 'Garcia', email: 'eve.garcia@student.edu' }
    ];

    const studentIds = [];
    for (const student of students) {
      const studentResult = await pool.query(`
        INSERT INTO users (email, password, first_name, last_name, role, is_active, email_verified)
        VALUES ($1, '$2a$10$testpassword', $2, $3, 'student', true, true)
        ON CONFLICT (email) DO UPDATE SET is_active = true
        RETURNING id
      `, [student.email, student.first_name, student.last_name]);
      studentIds.push(studentResult.rows[0].id);
      console.log(`✅ Student created: ${student.first_name} ${student.last_name} (ID: ${studentResult.rows[0].id})`);
    }

    // 5. Assign students to classes (all students to all classes for testing)
    console.log('🔗 Assigning students to classes...');
    for (const classId of classIds) {
      for (const studentId of studentIds) {
        await pool.query(`
          INSERT INTO class_students (class_id, student_id, is_active)
          VALUES ($1, $2, true)
          ON CONFLICT (class_id, student_id) DO UPDATE SET is_active = true
        `, [classId, studentId]);
      }
    }
    console.log(`✅ Assigned ${studentIds.length} students to ${classIds.length} classes`);

    // 6. Create sample attendance sessions and records
    console.log('📅 Creating sample attendance data...');
    const currentDate = new Date();
    
    // Create sessions for the last 7 days
    for (let i = 6; i >= 0; i--) {
      const sessionDate = new Date(currentDate);
      sessionDate.setDate(currentDate.getDate() - i);
      const dateString = sessionDate.toISOString().split('T')[0];
      
      // Skip weekends
      if (sessionDate.getDay() === 0 || sessionDate.getDay() === 6) {
        continue;
      }

      for (const classId of classIds) {
        // Create attendance session
        const sessionResult = await pool.query(`
          INSERT INTO attendance_sessions (class_id, teacher_id, session_date, session_time, session_type, status)
          VALUES ($1, $2, $3, $4, 'regular', 'completed')
          RETURNING session_id
        `, [classId, teacherId, dateString, '09:00:00']);
        
        const sessionId = sessionResult.rows[0].session_id;
        
        // Create attendance records for each student
        for (const studentId of studentIds) {
          // Create realistic attendance patterns (90% present, 5% absent, 5% late)
          const random = Math.random();
          let status, arrivalTime;
          
          if (random < 0.90) {
            status = 'present';
            arrivalTime = '08:55:00'; // 5 minutes early
          } else if (random < 0.95) {
            status = 'late';
            arrivalTime = '09:15:00'; // 15 minutes late
          } else {
            status = 'absent';
            arrivalTime = null;
          }
          
          await pool.query(`
            INSERT INTO attendance_records (session_id, student_id, status, arrival_time, marked_by)
            VALUES ($1, $2, $3, $4, $5)
          `, [sessionId, studentId, status, arrivalTime, teacherId]);
        }
      }
    }
    console.log('✅ Sample attendance data created successfully!');

    // 7. Display summary
    console.log('\n📊 SETUP SUMMARY:');
    console.log(`🏫 School: Smith High School (ID: ${schoolId})`);
    console.log(`👨‍🏫 Teacher: Sarah Johnson (ID: ${teacherId})`);
    console.log(`📚 Classes: ${classIds.length} classes created`);
    console.log(`👨‍🎓 Students: ${studentIds.length} students created`);
    console.log(`📅 Attendance: Sample data for last 7 days created`);
    
    console.log('\n🎉 Complete attendance system setup finished!');
    console.log('\n📝 Login Credentials:');
    console.log('👨‍🏫 Teacher: teacher@smithschool.edu / password');
    console.log('👨‍🎓 Students: alice.brown@student.edu / password (and others)');
    
  } catch (error) {
    console.error('❌ Error setting up attendance data:', error);
  } finally {
    await pool.end();
  }
}

// Run the setup
setupCompleteAttendanceData();
