-- ============================================================================
-- COMPLETE ATTENDANCE SYSTEM DATABASE SETUP
-- ============================================================================
-- Run this script in PostgreSQL to set up the complete attendance system
-- ============================================================================

-- Connect to database (run this in psql)
-- \c edtech_platform;

-- ============================================================================
-- 1. CREATE MISSING TABLES
-- ============================================================================

-- Create class_students table (if not exists)
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

-- ============================================================================
-- 2. CREATE TEST DATA
-- ============================================================================

-- Create test school
INSERT INTO schools (name, address, phone, email, principal_name, is_active)
VALUES ('Smith High School', '123 Education Street', '+1-555-0123', 'admin@smithschool.edu', 'Dr. John Smith', true)
ON CONFLICT (name) DO UPDATE SET is_active = true;

-- Get school ID
DO $$
DECLARE
    school_id INTEGER;
BEGIN
    SELECT id INTO school_id FROM schools WHERE name = 'Smith High School' LIMIT 1;
    
    -- Create test teacher
    INSERT INTO users (email, password, first_name, last_name, role, is_active, email_verified)
    VALUES ('teacher@smithschool.edu', '$2a$10$testpassword', 'Sarah', 'Johnson', 'teacher', true, true)
    ON CONFLICT (email) DO UPDATE SET is_active = true;
    
    -- Get teacher ID
    DECLARE
        teacher_id INTEGER;
    BEGIN
        SELECT id INTO teacher_id FROM users WHERE email = 'teacher@smithschool.edu' LIMIT 1;
        
        -- Create test classes
        INSERT INTO classes (school_id, name, grade_level, academic_year, teacher_id, is_active)
        VALUES 
            (school_id, 'Mathematics 101', 9, '2024-2025', teacher_id, true),
            (school_id, 'Science 101', 9, '2024-2025', teacher_id, true),
            (school_id, 'English 101', 9, '2024-2025', teacher_id, true)
        ON CONFLICT (school_id, name, academic_year) DO UPDATE SET is_active = true;
        
        -- Create test students
        INSERT INTO users (email, password, first_name, last_name, role, is_active, email_verified)
        VALUES 
            ('alice.brown@student.edu', '$2a$10$testpassword', 'Alice', 'Brown', 'student', true, true),
            ('bob.wilson@student.edu', '$2a$10$testpassword', 'Bob', 'Wilson', 'student', true, true),
            ('charlie.davis@student.edu', '$2a$10$testpassword', 'Charlie', 'Davis', 'student', true, true),
            ('diana.miller@student.edu', '$2a$10$testpassword', 'Diana', 'Miller', 'student', true, true),
            ('eve.garcia@student.edu', '$2a$10$testpassword', 'Eve', 'Garcia', 'student', true, true)
        ON CONFLICT (email) DO UPDATE SET is_active = true;
        
        -- Assign students to classes
        INSERT INTO class_students (class_id, student_id, is_active)
        SELECT c.id, u.id, true
        FROM classes c, users u
        WHERE c.school_id = school_id 
        AND c.teacher_id = teacher_id
        AND u.role = 'student'
        AND u.email IN ('alice.brown@student.edu', 'bob.wilson@student.edu', 'charlie.davis@student.edu', 'diana.miller@student.edu', 'eve.garcia@student.edu')
        ON CONFLICT (class_id, student_id) DO UPDATE SET is_active = true;
        
    END;
END $$;

-- ============================================================================
-- 3. CREATE SAMPLE ATTENDANCE DATA
-- ============================================================================

-- Create attendance sessions for the last 7 days
DO $$
DECLARE
    class_record RECORD;
    student_record RECORD;
    session_date DATE;
    session_id INTEGER;
    current_date DATE := CURRENT_DATE;
BEGIN
    -- Loop through each class
    FOR class_record IN 
        SELECT c.id as class_id, c.teacher_id 
        FROM classes c 
        JOIN schools s ON c.school_id = s.id 
        WHERE s.name = 'Smith High School'
    LOOP
        -- Create sessions for last 7 days
        FOR i IN 0..6 LOOP
            session_date := current_date - i;
            
            -- Skip weekends
            IF EXTRACT(DOW FROM session_date) NOT IN (0, 6) THEN
                -- Create attendance session
                INSERT INTO attendance_sessions (class_id, teacher_id, session_date, session_time, session_type, status)
                VALUES (class_record.class_id, class_record.teacher_id, session_date, '09:00:00', 'regular', 'completed')
                RETURNING session_id INTO session_id;
                
                -- Create attendance records for each student
                FOR student_record IN 
                    SELECT u.id as student_id
                    FROM users u
                    JOIN class_students cs ON u.id = cs.student_id
                    WHERE cs.class_id = class_record.class_id
                    AND u.role = 'student'
                LOOP
                    -- Create realistic attendance patterns (90% present, 5% absent, 5% late)
                    INSERT INTO attendance_records (session_id, student_id, status, arrival_time, marked_by)
                    VALUES (
                        session_id,
                        student_record.student_id,
                        CASE 
                            WHEN random() < 0.90 THEN 'present'
                            WHEN random() < 0.95 THEN 'late'
                            ELSE 'absent'
                        END,
                        CASE 
                            WHEN random() < 0.90 THEN '08:55:00'
                            WHEN random() < 0.95 THEN '09:15:00'
                            ELSE NULL
                        END,
                        class_record.teacher_id
                    );
                END LOOP;
            END IF;
        END LOOP;
    END LOOP;
END $$;

-- ============================================================================
-- 4. VERIFICATION QUERIES
-- ============================================================================

-- Check all tables
SELECT 'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'schools', COUNT(*) FROM schools
UNION ALL
SELECT 'classes', COUNT(*) FROM classes
UNION ALL
SELECT 'class_students', COUNT(*) FROM class_students
UNION ALL
SELECT 'attendance_sessions', COUNT(*) FROM attendance_sessions
UNION ALL
SELECT 'attendance_records', COUNT(*) FROM attendance_records;

-- Check test data
SELECT 'Test School' as item, name as value FROM schools WHERE name = 'Smith High School'
UNION ALL
SELECT 'Test Teacher', email FROM users WHERE email = 'teacher@smithschool.edu'
UNION ALL
SELECT 'Test Students', COUNT(*)::text FROM users WHERE role = 'student';

-- ============================================================================
-- SETUP COMPLETE!
-- ============================================================================
-- Login Credentials:
-- Teacher: teacher@smithschool.edu / password
-- Students: alice.brown@student.edu / password (and others)
-- ============================================================================
