-- Assign Teacher to Smith School Classes
-- This script assigns the current teacher to the classes we created

-- Step 1: Check current teacher
SELECT 'Current Teacher:' as info;
SELECT id, email, first_name, last_name, role, tenant_id 
FROM users 
WHERE email = 'newanilupadhyay@gmail.com' AND role = 'teacher';

-- Step 2: Check current classes in Smith School
SELECT 'Current Classes in Smith School:' as info;
SELECT c.id, c.name, c.grade_level, c.teacher_id, s.name as school_name
FROM classes c
JOIN schools s ON c.school_id = s.id
WHERE s.name LIKE '%Smith%'
ORDER BY c.grade_level;

-- Step 3: Assign teacher to all classes in Smith School
UPDATE classes 
SET teacher_id = (SELECT id FROM users WHERE email = 'newanilupadhyay@gmail.com' AND role = 'teacher' LIMIT 1)
WHERE school_id = (SELECT id FROM schools WHERE name LIKE '%Smith%' LIMIT 1)
  AND teacher_id IS NULL;

-- Step 4: Verify the assignment
SELECT 'Classes after teacher assignment:' as info;
SELECT 
    c.id,
    c.name,
    c.grade_level,
    c.teacher_id,
    u.first_name || ' ' || u.last_name as teacher_name,
    s.name as school_name
FROM classes c
JOIN schools s ON c.school_id = s.id
LEFT JOIN users u ON c.teacher_id = u.id
WHERE s.name LIKE '%Smith%'
ORDER BY c.grade_level;

-- Step 5: Check if teacher can now see classes
SELECT 'Teacher Classes Query Test:' as info;
SELECT 
    c.id,
    c.name,
    c.grade_level,
    c.academic_year,
    COUNT(s.id) as student_count
FROM classes c
LEFT JOIN students s ON c.id = s.class_id
WHERE c.teacher_id = (SELECT id FROM users WHERE email = 'newanilupadhyay@gmail.com' AND role = 'teacher' LIMIT 1)
  AND c.is_active = true
GROUP BY c.id, c.name, c.grade_level, c.academic_year
ORDER BY c.name;

-- Step 6: Summary
SELECT 'Summary:' as info;
SELECT 
    'Total Classes Assigned to Teacher' as metric,
    COUNT(*) as count
FROM classes c
JOIN schools s ON c.school_id = s.id
WHERE s.name LIKE '%Smith%'
  AND c.teacher_id = (SELECT id FROM users WHERE email = 'newanilupadhyay@gmail.com' AND role = 'teacher' LIMIT 1)

UNION ALL

SELECT 
    'Total Students in Teacher Classes' as metric,
    COUNT(st.id) as count
FROM classes c
JOIN schools s ON c.school_id = s.id
LEFT JOIN students st ON c.id = st.class_id
WHERE s.name LIKE '%Smith%'
  AND c.teacher_id = (SELECT id FROM users WHERE email = 'newanilupadhyay@gmail.com' AND role = 'teacher' LIMIT 1); 