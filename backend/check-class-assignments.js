const { query } = require('./src/config/database');

async function checkClassAssignments() {
  try {
    console.log('🔍 Checking class assignments...\n');
    
    // Check which classes have students
    const classAssignments = await query(`
      SELECT 
        c.id as class_id,
        c.name as class_name,
        c.teacher_id,
        COUNT(s.id) as student_count
      FROM classes c
      LEFT JOIN students s ON c.id = s.class_id AND s.is_active = true
      WHERE c.is_active = true
      GROUP BY c.id, c.name, c.teacher_id
      ORDER BY c.id
    `);
    
    console.log('📚 Classes with student counts:');
    classAssignments.rows.forEach(cls => {
      console.log(`  - Class ${cls.class_id}: ${cls.class_name} (Teacher: ${cls.teacher_id}) - ${cls.student_count} students`);
    });
    
    // Check unassigned students
    const unassignedStudents = await query(`
      SELECT COUNT(*) as count
      FROM students s
      WHERE s.class_id IS NULL AND s.is_active = true
    `);
    
    console.log(`\n⚠️  Unassigned students: ${unassignedStudents.rows[0].count}`);
    
    // Show teacher's classes
    const teacherClasses = await query(`
      SELECT 
        c.id,
        c.name,
        c.teacher_id,
        COUNT(s.id) as student_count
      FROM classes c
      LEFT JOIN students s ON c.id = s.class_id AND s.is_active = true
      WHERE c.teacher_id = 26 AND c.is_active = true
      GROUP BY c.id, c.name, c.teacher_id
      ORDER BY c.id
    `);
    
    console.log('\n👨‍🏫 Teacher 26 classes:');
    teacherClasses.rows.forEach(cls => {
      console.log(`  - Class ${cls.id}: ${cls.name} - ${cls.student_count} students`);
    });
    
  } catch (error) {
    console.error('❌ Error checking class assignments:', error);
  } finally {
    process.exit(0);
  }
}

checkClassAssignments(); 