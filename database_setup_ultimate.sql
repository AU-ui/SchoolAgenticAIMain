-- ============================================================================
-- ULTIMATE ATTENDANCE SYSTEM DATABASE SETUP
-- ============================================================================
-- This script fixes ALL variable conflicts and constraint issues
-- ============================================================================

-- Connect to database (run this in psql)
-- \c edtech_platform;

-- ============================================================================
-- 1. FIX EXISTING TABLES (if needed)
-- ============================================================================

-- Check if class_students table exists and has proper constraints
DO $$
BEGIN
    -- Add unique constraint if it doesn't exist
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'unique_class_student'
    ) THEN
        ALTER TABLE class_students 
        ADD CONSTRAINT unique_class_student UNIQUE (class_id, student_id);
        RAISE NOTICE 'Added unique constraint to class_students table';
    END IF;
END $$;

-- ============================================================================
-- 2. CREATE TEST DATA (WITHOUT VARIABLE CONFLICTS)
-- ============================================================================

-- Create test school (if not exists)
INSERT INTO schools (name, address, phone, email, principal_name, is_active)
SELECT 'Smith High School', '123 Education Street', '+1-555-0123', 'admin@smithschool.edu', 'Dr. John Smith', true
WHERE NOT EXISTS (SELECT 1 FROM schools WHERE name = 'Smith High School');

-- Create test teacher (if not exists)
INSERT INTO users (email, password, first_name, last_name, role, is_active, email_verified)
SELECT 'teacher@smithschool.edu', '$2a$10$testpassword', 'Sarah', 'Johnson', 'teacher', true, true
WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'teacher@smithschool.edu');

-- Get school and teacher IDs
DO $$
DECLARE
    v_school_id INTEGER;
    v_teacher_id INTEGER;
BEGIN
    -- Get school ID
    SELECT id INTO v_school_id FROM schools WHERE name = 'Smith High School' LIMIT 1;
    
    -- Get teacher ID
    SELECT id INTO v_teacher_id FROM users WHERE email = 'teacher@smithschool.edu' LIMIT 1;
    
    -- Create test classes (if not exist)
    INSERT INTO classes (school_id, name, grade_level, academic_year, teacher_id, is_active)
    SELECT v_school_id, 'Mathematics 101', 9, '2024-2025', v_teacher_id, true
    WHERE NOT EXISTS (SELECT 1 FROM classes WHERE school_id = v_school_id AND name = 'Mathematics 101' AND academic_year = '2024-2025');
    
    INSERT INTO classes (school_id, name, grade_level, academic_year, teacher_id, is_active)
    SELECT v_school_id, 'Science 101', 9, '2024-2025', v_teacher_id, true
    WHERE NOT EXISTS (SELECT 1 FROM classes WHERE school_id = v_school_id AND name = 'Science 101' AND academic_year = '2024-2025');
    
    INSERT INTO classes (school_id, name, grade_level, academic_year, teacher_id, is_active)
    SELECT v_school_id, 'English 101', 9, '2024-2025', v_teacher_id, true
    WHERE NOT EXISTS (SELECT 1 FROM classes WHERE school_id = v_school_id AND name = 'English 101' AND academic_year = '2024-2025');
    
    -- Create test students (if not exist)
    INSERT INTO users (email, password, first_name, last_name, role, is_active, email_verified)
    SELECT 'alice.brown@student.edu', '$2a$10$testpassword', 'Alice', 'Brown', 'student', true, true
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'alice.brown@student.edu');
    
    INSERT INTO users (email, password, first_name, last_name, role, is_active, email_verified)
    SELECT 'bob.wilson@student.edu', '$2a$10$testpassword', 'Bob', 'Wilson', 'student', true, true
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'bob.wilson@student.edu');
    
    INSERT INTO users (email, password, first_name, last_name, role, is_active, email_verified)
    SELECT 'charlie.davis@student.edu', '$2a$10$testpassword', 'Charlie', 'Davis', 'student', true, true
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'charlie.davis@student.edu');
    
    INSERT INTO users (email, password, first_name, last_name, role, is_active, email_verified)
    SELECT 'diana.miller@student.edu', '$2a$10$testpassword', 'Diana', 'Miller', 'student', true, true
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'diana.miller@student.edu');
    
    INSERT INTO users (email, password, first_name, last_name, role, is_active, email_verified)
    SELECT 'eve.garcia@student.edu', '$2a$10$testpassword', 'Eve', 'Garcia', 'student', true, true
    WHERE NOT EXISTS (SELECT 1 FROM users WHERE email = 'eve.garcia@student.edu');
    
    -- Assign students to classes (if not already assigned)
    INSERT INTO class_students (class_id, student_id, is_active)
    SELECT c.id, u.id, true
    FROM classes c, users u
    WHERE c.school_id = v_school_id 
    AND c.teacher_id = v_teacher_id
    AND u.role = 'student'
    AND u.email IN ('alice.brown@student.edu', 'bob.wilson@student.edu', 'charlie.davis@student.edu', 'diana.miller@student.edu', 'eve.garcia@student.edu')
    AND NOT EXISTS (
        SELECT 1 FROM class_students cs 
        WHERE cs.class_id = c.id AND cs.student_id = u.id
    );
    
END $$;

-- ============================================================================
-- 3. CREATE SAMPLE ATTENDANCE DATA (if not exists)
-- ============================================================================

DO $$
DECLARE
    class_record RECORD;
    student_record RECORD;
    v_session_date DATE;
    v_session_id INTEGER;
    v_current_date DATE := CURRENT_DATE;
    v_existing_sessions INTEGER;
BEGIN
    -- Loop through each class
    FOR class_record IN 
        SELECT c.id as class_id, c.teacher_id 
        FROM classes c 
        JOIN schools s ON c.school_id = s.id 
        WHERE s.name = 'Smith High School'
    LOOP
        -- Create sessions for last 7 days (if not exist)
        FOR i IN 0..6 LOOP
            v_session_date := v_current_date - i;
            
            -- Skip weekends
            IF EXTRACT(DOW FROM v_session_date) NOT IN (0, 6) THEN
                -- Check if session already exists
                SELECT COUNT(*) INTO v_existing_sessions
                FROM attendance_sessions 
                WHERE class_id = class_record.class_id 
                AND session_date = v_session_date;
                
                -- Create session only if it doesn't exist
                IF v_existing_sessions = 0 THEN
                    INSERT INTO attendance_sessions (class_id, teacher_id, session_date, session_time, session_type, status)
                    VALUES (class_record.class_id, class_record.teacher_id, v_session_date, '09:00:00', 'regular', 'completed')
                    RETURNING session_id INTO v_session_id;
                    
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
                            v_session_id,
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
