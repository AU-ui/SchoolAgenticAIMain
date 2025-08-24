const { pool } = require('./src/config/database');

async function resetDatabase() {
  try {
    console.log('🗑️  Starting database reset...');
    
    // Delete data in the correct order to avoid foreign key constraint violations
    console.log('📚 Deleting attendance records...');
    await pool.query('DELETE FROM attendance_records');
    
    console.log('📊 Deleting attendance sessions...');
    await pool.query('DELETE FROM attendance_sessions');
    
    console.log('📝 Deleting classes...');
    await pool.query('DELETE FROM classes');
    
    console.log('🏫 Deleting schools...');
    await pool.query('DELETE FROM schools');
    
    console.log('👥 Deleting users...');
    const result = await pool.query('DELETE FROM users');
    console.log(`✅ Deleted ${result.rowCount} users`);
    
    // Reset sequences - only the ones that exist
    console.log('🔄 Resetting sequences...');
    
    // Check and reset sequences that exist
    const sequences = [
      'users_id_seq',
      'classes_id_seq', 
      'schools_id_seq',
      'attendance_sessions_id_seq',
      'attendance_records_id_seq'
    ];
    
    for (const seqName of sequences) {
      try {
        await pool.query(`ALTER SEQUENCE ${seqName} RESTART WITH 1`);
        console.log(`✅ Reset sequence: ${seqName}`);
      } catch (seqError) {
        console.log(`⚠️  Sequence ${seqName} not found, skipping...`);
      }
    }
    
    console.log('🎉 Database reset completed successfully!');
    console.log('🗑️  All users, classes, schools, and related data have been deleted.');
    process.exit(0);
  } catch (error) {
    console.error('❌ Database reset failed:', error);
    console.error('Error details:', error.message);
    process.exit(1);
  }
}

resetDatabase();
