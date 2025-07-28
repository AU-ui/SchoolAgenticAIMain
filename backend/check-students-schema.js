const { query } = require('./src/config/database');

async function checkStudentsSchema() {
  try {
    console.log('🔍 Checking students table schema...\n');
    
    // Get column information
    const columnsResult = await query(`
      SELECT column_name, data_type, is_nullable
      FROM information_schema.columns 
      WHERE table_name = 'students' 
      ORDER BY ordinal_position
    `);
    
    console.log('📋 Students table columns:');
    columnsResult.rows.forEach(col => {
      console.log(`  - ${col.column_name} (${col.data_type}, nullable: ${col.is_nullable})`);
    });
    
    // Check if students exist
    const studentsCount = await query('SELECT COUNT(*) as count FROM students');
    console.log(`\n📊 Total students: ${studentsCount.rows[0].count}`);
    
    // Check sample student data
    if (studentsCount.rows[0].count > 0) {
      const sampleStudent = await query(`
        SELECT s.*, u.first_name, u.last_name, u.email
        FROM students s
        JOIN users u ON s.user_id = u.id
        LIMIT 1
      `);
      
      console.log('\n👤 Sample student data:');
      console.log(JSON.stringify(sampleStudent.rows[0], null, 2));
    }
    
    // Test the exact query that's failing
    console.log('\n🧪 Testing the failing query...');
    try {
      const testQuery = await query(`
        SELECT 
          s.id,
          s.student_id as student_code,
          u.first_name,
          u.last_name,
          u.email,
          s.emergency_contact,
          s.emergency_phone
        FROM students s
        JOIN users u ON s.user_id = u.id
        WHERE s.class_id = 1 AND s.is_active = true
        ORDER BY u.first_name, u.last_name
      `);
      
      console.log(`✅ Query successful! Found ${testQuery.rows.length} students for class 1`);
      if (testQuery.rows.length > 0) {
        console.log('Sample result:', JSON.stringify(testQuery.rows[0], null, 2));
      }
    } catch (error) {
      console.log('❌ Query failed:', error.message);
    }
    
  } catch (error) {
    console.error('❌ Error checking schema:', error);
  } finally {
    process.exit(0);
  }
}

checkStudentsSchema(); 