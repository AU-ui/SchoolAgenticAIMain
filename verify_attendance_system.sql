-- ============================================================================
-- ATTENDANCE SYSTEM VERIFICATION SCRIPT
-- ============================================================================
-- Run this to verify that the attendance system is working properly
-- ============================================================================

-- 1. Check all tables exist
SELECT 'Table Check' as check_type, 
       table_name,
       CASE WHEN table_name IS NOT NULL THEN '✅ EXISTS' ELSE '❌ MISSING' END as status
FROM (
    SELECT 'users' as table_name
    UNION ALL SELECT 'schools'
    UNION ALL SELECT 'classes'
    UNION ALL SELECT 'class_students'
    UNION ALL SELECT 'attendance_sessions'
    UNION ALL SELECT 'attendance_records'
    UNION ALL SELECT 'attendance_analytics'
) t
WHERE EXISTS (
    SELECT 1 FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = t.table_name
);

-- 2. Check data counts
SELECT 'Data Count' as check_type,
       'users' as table_name,
       COUNT(*) as record_count
FROM users
UNION ALL
SELECT 'Data Count', 'schools', COUNT(*) FROM schools
UNION ALL
SELECT 'Data Count', 'classes', COUNT(*) FROM classes
UNION ALL
SELECT 'Data Count', 'class_students', COUNT(*) FROM class_students
UNION ALL
SELECT 'Data Count', 'attendance_sessions', COUNT(*) FROM attendance_sessions
UNION ALL
SELECT 'Data Count', 'attendance_records', COUNT(*) FROM attendance_records;

-- 3. Check test school and teacher
SELECT 'Test Data' as check_type,
       'School' as item,
       name as value
FROM schools 
WHERE name = 'Smith High School'
UNION ALL
SELECT 'Test Data', 'Teacher', email 
FROM users 
WHERE email = 'teacher@smithschool.edu'
UNION ALL
SELECT 'Test Data', 'Students Count', COUNT(*)::text 
FROM users 
WHERE role = 'student';

-- 4. Check class-student relationships
SELECT 'Class-Student' as check_type,
       c.name as class_name,
       COUNT(cs.student_id) as student_count
FROM classes c
LEFT JOIN class_students cs ON c.id = cs.class_id
WHERE c.school_id = (SELECT id FROM schools WHERE name = 'Smith High School')
GROUP BY c.id, c.name;

-- 5. Check attendance data
SELECT 'Attendance' as check_type,
       c.name as class_name,
       COUNT(DISTINCT as.session_id) as sessions,
       COUNT(ar.record_id) as attendance_records
FROM classes c
LEFT JOIN attendance_sessions as ON c.id = as.class_id
LEFT JOIN attendance_records ar ON as.session_id = ar.session_id
WHERE c.school_id = (SELECT id FROM schools WHERE name = 'Smith High School')
GROUP BY c.id, c.name;

-- 6. Check attendance patterns
SELECT 'Attendance Pattern' as check_type,
       ar.status,
       COUNT(*) as count,
       ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM attendance_records ar
GROUP BY ar.status
ORDER BY count DESC;

-- 7. System Health Check
SELECT 
    CASE 
        WHEN (SELECT COUNT(*) FROM users WHERE role = 'teacher') > 0 THEN '✅ Teachers exist'
        ELSE '❌ No teachers found'
    END as teacher_check,
    
    CASE 
        WHEN (SELECT COUNT(*) FROM users WHERE role = 'student') > 0 THEN '✅ Students exist'
        ELSE '❌ No students found'
    END as student_check,
    
    CASE 
        WHEN (SELECT COUNT(*) FROM classes) > 0 THEN '✅ Classes exist'
        ELSE '❌ No classes found'
    END as class_check,
    
    CASE 
        WHEN (SELECT COUNT(*) FROM class_students) > 0 THEN '✅ Class-student relationships exist'
        ELSE '❌ No class-student relationships'
    END as relationship_check,
    
    CASE 
        WHEN (SELECT COUNT(*) FROM attendance_sessions) > 0 THEN '✅ Attendance sessions exist'
        ELSE '❌ No attendance sessions'
    END as session_check,
    
    CASE 
        WHEN (SELECT COUNT(*) FROM attendance_records) > 0 THEN '✅ Attendance records exist'
        ELSE '❌ No attendance records'
    END as record_check;

-- ============================================================================
-- VERIFICATION COMPLETE!
-- ============================================================================
-- If all checks show ✅, the system is ready to use
-- ============================================================================
