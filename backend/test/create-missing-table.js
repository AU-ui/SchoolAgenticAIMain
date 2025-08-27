const { Pool } = require('pg');
require('dotenv').config();

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: process.env.DB_PORT || 5432,
  database: process.env.DB_NAME || 'edtech_platform',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'your_password',
});

async function createMissingTable() {
  console.log('🔧 Creating Missing class_students Table...\n');
  
  try {
    // Create class_students table
    const createTableQuery = `
      CREATE TABLE IF NOT EXISTS class_students (
        id SERIAL PRIMARY KEY,
        class_id INTEGER NOT NULL,
        student_id INTEGER NOT NULL,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        
        -- Foreign key constraints
        CONSTRAINT fk_class_students_class FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
        CONSTRAINT fk_class_students_student FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
        
        -- Unique constraint to prevent duplicate assignments
        CONSTRAINT unique_class_student UNIQUE (class_id, student_id)
      );
    `;
    
    await pool.query(createTableQuery);
    console.log('✅ class_students table created successfully!');
    
    // Create indexes for performance
    const indexQueries = [
      'CREATE INDEX IF NOT EXISTS idx_class_students_class_id ON class_students(class_id);',
      'CREATE INDEX IF NOT EXISTS idx_class_students_student_id ON class_students(student_id);',
      'CREATE INDEX IF NOT EXISTS idx_class_students_active ON class_students(is_active);'
    ];
    
    for (const indexQuery of indexQueries) {
      await pool.query(indexQuery);
    }
    console.log('✅ Indexes created successfully!');
    
    // Verify table creation
    const verifyResult = await pool.query(`
      SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'class_students'
      );
    `);
    
    if (verifyResult.rows[0].exists) {
      console.log('✅ Table verification successful!');
    } else {
      console.log('❌ Table verification failed!');
    }
    
  } catch (error) {
    console.error('❌ Error creating table:', error);
  } finally {
    await pool.end();
  }
}

createMissingTable();
