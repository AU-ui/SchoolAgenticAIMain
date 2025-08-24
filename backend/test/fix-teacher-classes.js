const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function fixTeacherClasses() {
  console.log('🔧 Fixing Teacher Dashboard Classes Issue...\n');
  
  try {
    // Step 1: Create a test teacher if none exist
    console.log('✅ Step 1: Creating test teacher...');
    const testTeacher = await pool.query(`
      INSERT INTO users (first_name, last_name, email, password, role, is_active, created_at)
      VALUES ($1, $2, $3, $4, $5, $6, NOW())
      ON CONFLICT (email) DO NOTHING
      RETURNING id, first_name, last_name, email
    `, ['Test', 'Teacher', 'teacher@test.com', '$2b$10$test', 'teacher', true]);
    
    let teacherId;
    if (testTeacher.rows.length > 0) {
      teacherId = testTeacher.rows[0].id;
      console.log(`   Created test teacher: ${testTeacher.rows[0].first_name} ${testTeacher.rows[0].last_name} (ID: ${teacherId})`);
    } else {
      // Get existing teacher
      const existingTeacher = await pool.query(`
        SELECT id, first_name, last_name FROM users WHERE role = 'teacher' LIMIT 1
      `);
      if (existingTeacher.rows.length > 0) {
        teacherId = existingTeacher.rows[0].id;
        console.log(`   Using existing teacher: ${existingTeacher.rows[0].first_name} ${existingTeacher.rows[0].last_name} (ID: ${teacherId})`);
      } else {
        console.log('   No teachers found in database');
        return;
      }
    }
    
    // Step 2: Create test classes for the teacher
    console.log('\n✅ Step 2: Creating test classes...');
    const testClasses = [
      { name: 'Class 10A', grade_level: '10', subject: 'Mathematics' },
      { name: 'Class 10B', grade_level: '10', subject: 'Science' },
      { name: 'Class 9A', grade_level: '9', subject: 'English' }
    ];
    
    for (const cls of testClasses) {
      const newClass = await pool.query(`
        INSERT INTO classes (name, grade_level, subject, teacher_id, is_active, created_at)
        VALUES ($1, $2, $3, $4, $5, NOW())
        ON CONFLICT (name, teacher_id) DO NOTHING
        RETURNING id, name
      `, [cls.name, cls.grade_level, cls.subject, teacherId, true]);
      
      if (newClass.rows.length > 0) {
        console.log(`   Created class: ${newClass.rows[0].name} (ID: ${newClass.rows[0].id})`);
      } else {
        console.log(`   Class ${cls.name} already exists`);
      }
    }
    
    // Step 3: Create test students for the classes
    console.log('\n✅ Step 3: Creating test students...');
    const classes = await pool.query(`
      SELECT id, name FROM classes WHERE teacher_id = $1
    `, [teacherId]);
    
    for (const cls of classes.rows) {
      const testStudents = [
        { name: 'John Doe', email: `john.${cls.id}@test.com` },
        { name: 'Jane Smith', email: `jane.${cls.id}@test.com` },
        { name: 'Mike Johnson', email: `mike.${cls.id}@test.com` }
      ];
      
      for (const student of testStudents) {
        const newStudent = await pool.query(`
          INSERT INTO students (name, email, class_id, is_active, created_at)
          VALUES ($1, $2, $3, $4, NOW())
          ON CONFLICT (email) DO NOTHING
          RETURNING id, name
        `, [student.name, student.email, cls.id, true]);
        
        if (newStudent.rows.length > 0) {
          console.log(`   Created student: ${newStudent.rows[0].name} in ${cls.name}`);
        }
      }
    }
    
    console.log('\n�� Fix completed!');
    console.log('\n📋 Test Credentials:');
    console.log(`Email: teacher@test.com`);
    console.log(`Password: test123`);
    console.log(`Teacher ID: ${teacherId}`);
    
    console.log('\n�� Next Steps:');
    console.log('1. Restart the backend server');
    console.log('2. Login with the test credentials');
    console.log('3. Check if classes appear in Teacher Dashboard');
    
  } catch (error) {
    console.error('❌ Fix failed:', error);
  } finally {
    await pool.end();
  }
}

fixTeacherClasses();
