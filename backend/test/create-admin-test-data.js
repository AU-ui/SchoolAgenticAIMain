const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function createAdminTestData() {
  console.log('📝 Creating Admin Dashboard Test Data...\n');
  
  try {
    // 1. Get or create a test school
    let schoolId;
    const existingSchool = await pool.query(`
      SELECT id FROM schools WHERE name LIKE '%Smith%' LIMIT 1
    `);
    
    if (existingSchool.rows.length > 0) {
      schoolId = existingSchool.rows[0].id;
      console.log(`✅ Using existing school ID: ${schoolId}`);
    } else {
      // Create a test school
      const newSchool = await pool.query(`
        INSERT INTO schools (tenant_id, name, address, phone, email, is_active)
        VALUES (1, 'W H Smith School', '123 Smith Street', '+1-555-0123', 'admin@smithschool.edu', true)
        RETURNING id
      `);
      schoolId = newSchool.rows[0].id;
      console.log(`✅ Created new school ID: ${schoolId}`);
    }
    
    // 2. Get or create test classes
    const classes = await pool.query(`
      SELECT id, name, grade_level FROM classes 
      WHERE school_id = $1 AND is_active = true
    `, [schoolId]);
    
    if (classes.rows.length === 0) {
      console.log('❌ No classes found for this school!');
      return;
    }
    
    console.log(`✅ Found ${classes.rows.length} classes`);
    
    // 3. Get students for each class
    for (const cls of classes.rows) {
      console.log(`\n📚 Processing class: ${cls.name} (Grade ${cls.grade_level})`);
      
      const students = await pool.query(`
        SELECT s.id, s.user_id, u.first_name, u.last_name 
        FROM students s 
        JOIN users u ON s.user_id = u.id 
        WHERE s.class_id = $1 AND s.is_active = true
      `, [cls.id]);
      
      console.log(`✅ Found ${students.rows.length} students in this class`);
      
      if (students.rows.length === 0) {
        console.log('⚠️  No students in this class, skipping...');
        continue;
      }
      
      // 4. Create attendance sessions for the current month
      const currentDate = new Date();
      const currentMonth = currentDate.getMonth() + 1;
      const currentYear = currentDate.getFullYear();
      
      // Get the first day of the current month
      const firstDay = new Date(currentYear, currentMonth - 1, 1);
      const lastDay = new Date(currentYear, currentMonth, 0);
      
      console.log(`📅 Creating attendance data for ${currentMonth}/${currentYear}`);
      
      // Create attendance sessions for each school day
      for (let day = 1; day <= lastDay.getDate(); day++) {
        const date = new Date(currentYear, currentMonth - 1, day);
        
        // Skip weekends (0 = Sunday, 6 = Saturday)
        if (date.getDay() === 0 || date.getDay() === 6) {
          continue;
        }
        
        const dateString = date.toISOString().split('T')[0];
        const sessionId = `session_${cls.id}_${dateString}`;
        
        // Create attendance session
        await pool.query(`
          INSERT INTO attendance_sessions (id, class_id, created_at, expires_at, is_active) 
          VALUES ($1, $2, $3, $4, true)
          ON CONFLICT (id) DO NOTHING
        `, [sessionId, cls.id, dateString, new Date(date.getTime() + 86400000)]);
        
        // Create attendance records for each student
        for (const student of students.rows) {
          // Create realistic attendance patterns
          let status;
          const random = Math.random();
          
          // 85% present, 10% absent, 5% late
          if (random > 0.15) {
            status = 'present';
          } else if (random > 0.05) {
            status = 'absent';
          } else {
            status = 'late';
          }
          
          // Add some variation based on student
          if (student.first_name === 'Sarah' || student.first_name === 'Emma') {
            // These students have better attendance
            if (random > 0.05) status = 'present';
            else if (random > 0.02) status = 'late';
            else status = 'absent';
          }
          
          await pool.query(`
            INSERT INTO attendance_records (class_id, student_id, session_id, status, date, created_at) 
            VALUES ($1, $2, $3, $4, $5, NOW())
            ON CONFLICT DO NOTHING
          `, [cls.id, student.id, sessionId, status, dateString]);
        }
      }
      
      console.log(`✅ Created attendance data for ${students.rows.length} students in ${cls.name}`);
    }
    
    console.log('\n🎉 Admin dashboard test data created successfully!');
    console.log('You can now test the admin dashboard with real attendance data.');
    
  } catch (error) {
    console.error('❌ Error creating test data:', error);
  } finally {
    await pool.end();
  }
}

createAdminTestData();
