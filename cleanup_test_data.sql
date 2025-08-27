-- ============================================================================
-- CLEANUP TEST DATA SCRIPT
-- ============================================================================
-- Run this script when project is complete to remove test data
-- WARNING: This will delete all test data permanently!
-- ============================================================================

-- Connect to database (run this in psql)
-- \c edtech_platform;

-- ============================================================================
-- 1. DELETE TEST ATTENDANCE DATA
-- ============================================================================

-- Delete attendance records for test sessions
DELETE FROM attendance_records 
WHERE session_id IN (
    SELECT session_id 
    FROM attendance_sessions 
    WHERE class_id IN (
        SELECT id FROM classes WHERE school_id IN (
            SELECT id FROM schools WHERE name = 'Smith High School'
        )
    )
);

-- Delete attendance sessions for test classes
DELETE FROM attendance_sessions 
WHERE class_id IN (
    SELECT id FROM classes WHERE school_id IN (
        SELECT id FROM schools WHERE name = 'Smith High School'
    )
);

-- ============================================================================
-- 2. DELETE TEST CLASS-STUDENT RELATIONSHIPS
-- ============================================================================

-- Delete class-student relationships for test classes
DELETE FROM class_students 
WHERE class_id IN (
    SELECT id FROM classes WHERE school_id IN (
        SELECT id FROM schools WHERE name = 'Smith High School'
    )
);

-- ============================================================================
-- 3. DELETE TEST CLASSES
-- ============================================================================

-- Delete test classes
DELETE FROM classes 
WHERE school_id IN (
    SELECT id FROM schools WHERE name = 'Smith High School'
);

-- ============================================================================
-- 4. DELETE TEST STUDENTS
-- ============================================================================

-- Delete test students
DELETE FROM users 
WHERE email IN (
    'alice.brown@student.edu',
    'bob.wilson@student.edu',
    'charlie.davis@student.edu',
    'diana.miller@student.edu',
    'eve.garcia@student.edu'
);

-- ============================================================================
-- 5. DELETE TEST TEACHER
-- ============================================================================

-- Delete test teacher
DELETE FROM users 
WHERE email = 'teacher@smithschool.edu';

-- ============================================================================
-- 6. DELETE TEST SCHOOL
-- ============================================================================

-- Delete test school
DELETE FROM schools 
WHERE name = 'Smith High School';

-- ============================================================================
-- 7. VERIFICATION
-- ============================================================================

-- Check if test data is removed
SELECT 'Cleanup Verification' as check_type,
       'Test School' as item,
       CASE 
           WHEN COUNT(*) = 0 THEN '✅ Removed'
           ELSE '❌ Still exists'
       END as status
FROM schools 
WHERE name = 'Smith High School'
UNION ALL
SELECT 'Cleanup Verification', 'Test Teacher',
       CASE 
           WHEN COUNT(*) = 0 THEN '✅ Removed'
           ELSE '❌ Still exists'
       END
FROM users 
WHERE email = 'teacher@smithschool.edu'
UNION ALL
SELECT 'Cleanup Verification', 'Test Students',
       CASE 
           WHEN COUNT(*) = 0 THEN '✅ Removed'
           ELSE '❌ Still exists (' || COUNT(*) || ' remaining)'
       END
FROM users 
WHERE email IN (
    'alice.brown@student.edu',
    'bob.wilson@student.edu',
    'charlie.davis@student.edu',
    'diana.miller@student.edu',
    'eve.garcia@student.edu'
);

-- ============================================================================
-- CLEANUP COMPLETE!
-- ============================================================================
-- All test data has been removed from the database
-- ============================================================================
