const fs = require('fs');
const path = require('path');
const { query, testConnection } = require('./src/config/database');

async function setupQRSchema() {
  try {
    console.log('🔍 Checking database connection...');
    const isConnected = await testConnection();
    
    if (!isConnected) {
      console.error('❌ Database connection failed!');
      process.exit(1);
    }
    
    console.log('📖 Reading QR attendance schema file...');
    const schemaPath = path.join(__dirname, 'database', 'qr_attendance_schema.sql');
    
    if (!fs.existsSync(schemaPath)) {
      console.error('❌ QR attendance schema file not found!');
      console.error('Expected path:', schemaPath);
      process.exit(1);
    }
    
    const sqlContent = fs.readFileSync(schemaPath, 'utf8');
    console.log('✅ Schema file loaded successfully');
    
    // Split SQL into individual statements
    const statements = sqlContent
      .split(';')
      .map(stmt => stmt.trim())
      .filter(stmt => stmt.length > 0 && !stmt.startsWith('--'));
    
    console.log(`📝 Found ${statements.length} SQL statements to execute`);
    
    // Execute each statement
    for (let i = 0; i < statements.length; i++) {
      const statement = statements[i];
      if (statement.trim()) {
        try {
          console.log(`🔄 Executing statement ${i + 1}/${statements.length}...`);
          await query(statement);
          console.log(`✅ Statement ${i + 1} executed successfully`);
        } catch (error) {
          console.error(`❌ Error in statement ${i + 1}:`, error.message);
          // Continue with other statements
        }
      }
    }
    
    console.log('🎉 QR Code Attendance Schema setup completed!');
    
    // Verify tables were created
    console.log('🔍 Verifying tables...');
    const tables = await query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      AND table_name LIKE 'qr_%'
      ORDER BY table_name
    `);
    
    console.log('📊 Created QR tables:');
    tables.rows.forEach(row => {
      console.log(`  - ${row.table_name}`);
    });
    
  } catch (error) {
    console.error('❌ Setup failed:', error);
    process.exit(1);
  }
}

// Run the setup
setupQRSchema();
