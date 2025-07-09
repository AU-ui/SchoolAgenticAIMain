const { query } = require('./src/config/database');

async function checkAndFixDatabaseSchema() {
  try {
    console.log('🔍 Checking database schema...');
    
    // Check if password_hash column exists
    const checkPasswordHash = await query(`
      SELECT column_name 
      FROM information_schema.columns 
      WHERE table_name = 'users' AND column_name = 'password_hash'
    `);
    
    // Check if password column exists
    const checkPassword = await query(`
      SELECT column_name 
      FROM information_schema.columns 
      WHERE table_name = 'users' AND column_name = 'password'
    `);
    
    if (checkPasswordHash.rows.length > 0 && checkPassword.rows.length === 0) {
      console.log('🔄 Found password_hash column, renaming to password...');
      
      // Rename password_hash to password
      await query('ALTER TABLE users RENAME COLUMN password_hash TO password');
      console.log('✅ Column renamed successfully!');
    } else if (checkPassword.rows.length > 0) {
      console.log('✅ Password column already exists');
    } else {
      console.log('❌ Neither password_hash nor password column found');
      return;
    }
    
    // Check for other missing columns
    const requiredColumns = [
      'verification_code',
      'verification_expires', 
      'requires_approval'
    ];
    
    for (const column of requiredColumns) {
      const checkColumn = await query(`
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = $1
      `, [column]);
      
      if (checkColumn.rows.length === 0) {
        console.log(`❌ Missing column: ${column}`);
      } else {
        console.log(`✅ Column exists: ${column}`);
      }
    }
    
    // Check school_codes table
    const checkSchoolCodes = await query(`
      SELECT column_name 
      FROM information_schema.columns 
      WHERE table_name = 'school_codes' AND column_name = 'current_uses'
    `);
    
    if (checkSchoolCodes.rows.length === 0) {
      console.log('🔄 Updating school_codes table...');
      try {
        await query('ALTER TABLE school_codes RENAME COLUMN uses TO current_uses');
        console.log('✅ School codes table updated');
      } catch (error) {
        console.log('ℹ️ School codes table already updated or different structure');
      }
    }
    
    console.log('✅ Database schema check completed!');
    
  } catch (error) {
    console.error('❌ Error checking database schema:', error);
  } finally {
    process.exit(0);
  }
}

// Run the script
checkAndFixDatabaseSchema(); 