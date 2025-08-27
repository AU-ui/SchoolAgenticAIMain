const { query, testConnection } = require('./src/config/database');

async function setupQRTables() {
  try {
    console.log('🔍 Checking database connection...');
    const isConnected = await testConnection();
    
    if (!isConnected) {
      console.error('❌ Database connection failed!');
      process.exit(1);
    }
    
    console.log('🚀 Starting QR Code Tables Setup...\n');
    
    // Step 1: Create qr_attendance_sessions table
    console.log('📋 Step 1: Creating qr_attendance_sessions table...');
    await query(`
      CREATE TABLE IF NOT EXISTS qr_attendance_sessions (
        id SERIAL PRIMARY KEY,
        class_id INTEGER NOT NULL,
        teacher_id INTEGER NOT NULL,
        session_date DATE NOT NULL,
        session_time TIME NOT NULL,
        qr_data JSONB NOT NULL,
        expiry_time TIMESTAMP NOT NULL,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        CONSTRAINT fk_qr_sessions_class FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
        CONSTRAINT fk_qr_sessions_teacher FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE,
        CONSTRAINT unique_qr_session UNIQUE (class_id, session_date, session_time)
      )
    `);
    console.log('✅ qr_attendance_sessions table created successfully\n');
    
    // Step 2: Create qr_code_scans table
    console.log('📋 Step 2: Creating qr_code_scans table...');
    await query(`
      CREATE TABLE IF NOT EXISTS qr_code_scans (
        id SERIAL PRIMARY KEY,
        qr_session_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        scanned_by INTEGER NOT NULL,
        scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        device_info JSONB,
        location_info JSONB,
        scan_result VARCHAR(50) NOT NULL,
        
        CONSTRAINT fk_qr_scans_session FOREIGN KEY (qr_session_id) REFERENCES qr_attendance_sessions(id) ON DELETE CASCADE,
        CONSTRAINT fk_qr_scans_student FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
        CONSTRAINT fk_qr_scans_scanned_by FOREIGN KEY (scanned_by) REFERENCES users(id) ON DELETE CASCADE
      )
    `);
    console.log('✅ qr_code_scans table created successfully\n');
    
    // Step 3: Create qr_attendance_analytics table
    console.log('📋 Step 3: Creating qr_attendance_analytics table...');
    await query(`
      CREATE TABLE IF NOT EXISTS qr_attendance_analytics (
        analytics_id SERIAL PRIMARY KEY,
        qr_session_id INTEGER NOT NULL,
        class_id INTEGER NOT NULL,
        total_scans INTEGER DEFAULT 0,
        successful_scans INTEGER DEFAULT 0,
        failed_scans INTEGER DEFAULT 0,
        duplicate_scans INTEGER DEFAULT 0,
        average_scan_time DECIMAL(5,2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        CONSTRAINT fk_qr_analytics_session FOREIGN KEY (qr_session_id) REFERENCES qr_attendance_sessions(id) ON DELETE CASCADE,
        CONSTRAINT fk_qr_analytics_class FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
      )
    `);
    console.log('✅ qr_attendance_analytics table created successfully\n');
    
    // Step 4: Create indexes
    console.log('📋 Step 4: Creating performance indexes...');
    await query('CREATE INDEX IF NOT EXISTS idx_qr_sessions_class_date ON qr_attendance_sessions(class_id, session_date)');
    await query('CREATE INDEX IF NOT EXISTS idx_qr_sessions_teacher ON qr_attendance_sessions(teacher_id)');
    await query('CREATE INDEX IF NOT EXISTS idx_qr_sessions_expiry ON qr_attendance_sessions(expiry_time)');
    await query('CREATE INDEX IF NOT EXISTS idx_qr_scans_session ON qr_code_scans(qr_session_id)');
    await query('CREATE INDEX IF NOT EXISTS idx_qr_scans_student ON qr_code_scans(student_id)');
    await query('CREATE INDEX IF NOT EXISTS idx_qr_scans_timestamp ON qr_code_scans(scan_timestamp)');
    console.log('✅ Performance indexes created successfully\n');
    
    // Step 5: Add comments
    console.log('📋 Step 5: Adding table comments...');
    await query("COMMENT ON TABLE qr_attendance_sessions IS 'QR code sessions for attendance tracking'");
    await query("COMMENT ON TABLE qr_code_scans IS 'Audit trail of QR code scans'");
    await query("COMMENT ON TABLE qr_attendance_analytics IS 'Analytics for QR code attendance usage'");
    console.log('✅ Table comments added successfully\n');
    
    // Step 6: Create utility function
    console.log('📋 Step 6: Creating utility functions...');
    await query(`
      CREATE OR REPLACE FUNCTION cleanup_expired_qr_sessions()
      RETURNS void AS $$
      BEGIN
        UPDATE qr_attendance_sessions 
        SET is_active = false 
        WHERE expiry_time < NOW() AND is_active = true;
      END;
      $$ LANGUAGE plpgsql
    `);
    console.log('✅ Utility functions created successfully\n');
    
    // Step 7: Create trigger for updated_at
    console.log('📋 Step 7: Creating triggers...');
    await query(`
      CREATE OR REPLACE FUNCTION update_qr_sessions_updated_at()
      RETURNS TRIGGER AS $$
      BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
      END;
      $$ LANGUAGE plpgsql
    `);
    
    await query(`
      DROP TRIGGER IF EXISTS trigger_qr_sessions_updated_at ON qr_attendance_sessions
    `);
    
    await query(`
      CREATE TRIGGER trigger_qr_sessions_updated_at
        BEFORE UPDATE ON qr_attendance_sessions
        FOR EACH ROW
        EXECUTE FUNCTION update_qr_sessions_updated_at()
    `);
    console.log('✅ Triggers created successfully\n');
    
    // Step 8: Create views
    console.log('📋 Step 8: Creating views...');
    await query(`
      CREATE OR REPLACE VIEW active_qr_sessions AS
      SELECT 
        qs.id,
        qs.class_id,
        c.name as class_name,
        qs.teacher_id,
        u.first_name || ' ' || u.last_name as teacher_name,
        qs.session_date,
        qs.session_time,
        qs.expiry_time,
        qs.is_active,
        CASE 
          WHEN qs.expiry_time > NOW() THEN 'active'
          ELSE 'expired'
        END as status
      FROM qr_attendance_sessions qs
      JOIN classes c ON qs.class_id = c.id
      JOIN users u ON qs.teacher_id = u.id
      WHERE qs.is_active = true
    `);
    console.log('✅ Views created successfully\n');
    
    console.log('🎉 QR Code Tables Setup Completed Successfully!');
    
    // Verify tables
    console.log('\n🔍 Verifying created tables...');
    const tables = await query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      AND table_name LIKE 'qr_%'
      ORDER BY table_name
    `);
    
    console.log('📊 Created QR tables:');
    tables.rows.forEach(row => {
      console.log(`  ✅ ${row.table_name}`);
    });
    
    console.log('\n🚀 QR Code Attendance System is ready!');
    
  } catch (error) {
    console.error('❌ Setup failed:', error);
    process.exit(1);
  }
}

// Run the setup
setupQRTables();
