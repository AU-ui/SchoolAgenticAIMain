const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function diagnoseTeacherClasses() {
  console.log('�� Diagnosing Teacher Dashboard Classes Issue...\n');
  
  try {
    // Test 1: Check database connection
    console.log('✅ Test 1: Database Connection');
    const dbTest = await pool.query('SELECT NOW()');
    console.log('   Database connected:', dbTest.rows[0].now);
    
    // Test 2: Check users table structure
    console.log('\n✅ Test 2: Users Table Structure');
    const usersStructure = await pool.query(`
      SELECT column_name, data_type, is_nullable 
      FROM information_schema.columns 
      WHERE table_name = 'users' 
      ORDER BY ordinal_position
    `);
    console.log('   Users table columns:');
    usersStructure.rows.forEach(col => {
      console.log(`   - ${col.column_name}: ${col.data_type} (nullable: ${col.is_nullable})`);
    });
    
    // Test 3: Check classes table structure (FIXED - removed subject column)
    console.log('\n✅ Test 3: Classes Table Structure');
    const classesStructure = await pool.query(`
      SELECT column_name, data_type, is_nullable 
      FROM information_schema.columns 
      WHERE table_name = 'classes' 
      ORDER BY ordinal_position
    `);
    console.log('   Classes table columns:');
    classesStructure.rows.forEach(col => {
      console.log(`   - ${col.column_name}: ${col.data_type} (nullable: ${col.is_nullable})`);
    });
    
    // Test 4: Check if teachers exist
    console.log('\n✅ Test 4: Teachers in Database');
    const teachers = await pool.query(`
      SELECT id, first_name, last_name, email, role 
      FROM users 
      WHERE role = 'teacher' 
      LIMIT 10
    `);
    console.log(`   Found ${teachers.rows.length} teachers:`);
    teachers.rows.forEach(teacher => {
      console.log(`   - ID: ${teacher.id}, Name: ${teacher.first_name} ${teacher.last_name}, Email: ${teacher.email}`);
    });
    
    // Test 5: Check if classes exist (FIXED - removed subject column)
    console.log('\n✅ Test 5: Classes in Database');
    const classes = await pool.query(`
      SELECT id, name, teacher_id, grade_level, academic_year, is_active 
      FROM classes 
      LIMIT 10
    `);
    console.log(`   Found ${classes.rows.length} classes:`);
    classes.rows.forEach(cls => {
      console.log(`   - ID: ${cls.id}, Name: ${cls.name}, Teacher ID: ${cls.teacher_id}, Grade: ${cls.grade_level}, Active: ${cls.is_active}`);
    });
    
    // Test 6: Check teacher-class relationships
    console.log('\n✅ Test 6: Teacher-Class Relationships');
    const teacherClasses = await pool.query(`
      SELECT 
        u.id as teacher_id,
        u.first_name,
        u.last_name,
        c.id as class_id,
        c.name as class_name,
        c.grade_level,
        c.is_active
      FROM users u
      LEFT JOIN classes c ON u.id = c.teacher_id
      WHERE u.role = 'teacher'
      ORDER BY u.first_name, c.name
    `);
    console.log('   Teacher-Class relationships:');
    teacherClasses.rows.forEach(rel => {
      if (rel.class_id) {
        console.log(`   - ${rel.first_name} ${rel.last_name} (${rel.teacher_id}) -> ${rel.class_name} Grade ${rel.grade_level} (${rel.class_id}) [Active: ${rel.is_active}]`);
      } else {
        console.log(`   - ${rel.first_name} ${rel.last_name} (${rel.teacher_id}) -> NO CLASSES ASSIGNED`);
      }
    });
    
    // Test 7: Check API endpoint directly
    console.log('\n✅ Test 7: Testing API Endpoint');
    try {
      const response = await fetch('http://localhost:5000/api/teacher/classes', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        }
      });
      console.log(`   API Response Status: ${response.status}`);
      if (response.ok) {
        const data = await response.json();
        console.log(`   API Response: ${JSON.stringify(data, null, 2)}`);
      } else {
        const errorText = await response.text();
        console.log(`   API Error: ${errorText}`);
      }
    } catch (error) {
      console.log(`   API Error: ${error.message}`);
    }
    
    // Test 8: Check for common issues
    console.log('\n✅ Test 8: Common Issues Check');
    
    // Check if classes have teacher_id
    const classesWithoutTeacher = await pool.query(`
      SELECT COUNT(*) as count 
      FROM classes 
      WHERE teacher_id IS NULL
    `);
    console.log(`   Classes without teacher_id: ${classesWithoutTeacher.rows[0].count}`);
    
    // Check if classes are inactive
    const inactiveClasses = await pool.query(`
      SELECT COUNT(*) as count 
      FROM classes 
      WHERE is_active = false
    `);
    console.log(`   Inactive classes: ${inactiveClasses.rows[0].count}`);
    
    // Check if teachers exist but have no classes
    const teachersWithoutClasses = await pool.query(`
      SELECT COUNT(*) as count 
      FROM users u
      LEFT JOIN classes c ON u.id = c.teacher_id
      WHERE u.role = 'teacher' AND c.id IS NULL
    `);
    console.log(`   Teachers without classes: ${teachersWithoutClasses.rows[0].count}`);
    
    console.log('\n DIAGNOSIS SUMMARY:');
    console.log('1. Check if teachers exist in the database');
    console.log('2. Check if classes are assigned to teachers');
    console.log('3. Check if classes are marked as active');
    console.log('4. Check if the API endpoint is working');
    console.log('5. Check if authentication is working');
    
  } catch (error) {
    console.error('❌ Diagnosis failed:', error);
  } finally {
    await pool.end();
  }
}

diagnoseTeacherClasses();
