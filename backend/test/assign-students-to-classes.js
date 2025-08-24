const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function assignStudentsToClasses() {
  console.log('📝 Assigning Students to Classes...\n');
  
  try {
    // 1. Get all classes
    const classes = await pool.query(`
      SELECT id, name, grade_level, school_id 
      FROM classes 
      WHERE is_active = true 
      ORDER BY grade_level, name
    `);
    
    console.log(`✅ Found ${classes.rows.length} classes`);
    
    // 2. Get all students without class assignments
    const unassignedStudents = await pool.query(`
      SELECT s.id, s.user_id, u.first_name, u.last_name, u.email
      FROM students s
      JOIN users u ON s.user_id = u.id
      WHERE s.class_id IS NULL AND s.is_active = true
      ORDER BY u.first_name, u.last_name
    `);
    
    console.log(`✅ Found ${unassignedStudents.rows.length} unassigned students`);
    
    if (unassignedStudents.rows.length === 0) {
      console.log('✅ All students are already assigned to classes');
      return;
    }
    
    // 3. Assign students to classes based on grade level or distribute evenly
    let classIndex = 0;
    
    for (const student of unassignedStudents.rows) {
      const targetClass = classes.rows[classIndex % classes.rows.length];
      
      await pool.query(`
        UPDATE students 
        SET class_id = $1, updated_at = NOW()
        WHERE id = $2
      `, [targetClass.id, student.id]);
      
      console.log(`✅ Assigned ${student.first_name} ${student.last_name} to ${targetClass.name} (Grade ${targetClass.grade_level})`);
      
      classIndex++;
    }
    
    console.log(`\n🎉 Successfully assigned ${unassignedStudents.rows.length} students to classes`);
    
    // 4. Show final distribution
    console.log('\n📊 Final Class Distribution:');
    const finalDistribution = await pool.query(`
      SELECT 
        c.name as class_name,
        c.grade_level,
        COUNT(s.id) as student_count,
        STRING_AGG(u.first_name || ' ' || u.last_name, ', ') as students
      FROM classes c
      LEFT JOIN students s ON c.id = s.class_id AND s.is_active = true
      LEFT JOIN users u ON s.user_id = u.id
      WHERE c.is_active = true
      GROUP BY c.id, c.name, c.grade_level
      ORDER BY c.grade_level, c.name
    `);
    
    finalDistribution.rows.forEach(cls => {
      console.log(`  ${cls.class_name} (Grade ${cls.grade_level}): ${cls.student_count} students`);
    });
    
  } catch (error) {
    console.error('❌ Error assigning students to classes:', error);
  } finally {
    await pool.end();
  }
}

assignStudentsToClasses();