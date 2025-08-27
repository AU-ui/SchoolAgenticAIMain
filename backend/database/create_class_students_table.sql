-- ============================================================================
-- CLASS STUDENTS RELATIONSHIP TABLE
-- ============================================================================
-- Establishes many-to-many relationship between classes and students
-- ============================================================================

-- Create class_students table
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

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_class_students_class_id ON class_students(class_id);
CREATE INDEX IF NOT EXISTS idx_class_students_student_id ON class_students(student_id);
CREATE INDEX IF NOT EXISTS idx_class_students_active ON class_students(is_active);

-- Add comments for documentation
COMMENT ON TABLE class_students IS 'Many-to-many relationship between classes and students';
COMMENT ON COLUMN class_students.is_active IS 'Whether the student is currently enrolled in this class';
