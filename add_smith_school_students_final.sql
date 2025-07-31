-- Final Script: Add Classes and Students to Smith School
-- This script handles existing data and only adds what's missing

-- Step 1: Check current Smith School
SELECT 'Current Smith School:' as info;
SELECT id, name, tenant_id FROM schools WHERE name LIKE '%Smith%';

-- Step 2: Add Classes for Smith School (if they don't exist)
INSERT INTO classes (school_id, name, grade_level, academic_year, is_active, created_at, updated_at)
SELECT 
    (SELECT id FROM schools WHERE name LIKE '%Smith%' LIMIT 1) as school_id,
    'Grade ' || grade_level || 'A' as name,
    grade_level,
    '2024-2025' as academic_year,
    true as is_active,
    NOW() as created_at,
    NOW() as updated_at
FROM (VALUES (5), (6), (7), (8)) as grades(grade_level)
WHERE NOT EXISTS (
    SELECT 1 FROM classes c 
    JOIN schools s ON c.school_id = s.id 
    WHERE s.name LIKE '%Smith%' AND c.grade_level = grades.grade_level
);

-- Step 3: Check existing students
SELECT 'Existing Students:' as info;
SELECT u.email, u.first_name, u.last_name, u.role
FROM users u 
WHERE u.email LIKE '%@smithschool.edu' AND u.role = 'student';

-- Step 4: Add only missing student users
INSERT INTO users (email, password, first_name, last_name, role, tenant_id, is_active, created_at, updated_at)
SELECT 
    email,
    '$2b$10$hashedpassword' as password,
    first_name,
    last_name,
    'student' as role,
    2 as tenant_id,
    true as is_active,
    NOW() as created_at,
    NOW() as updated_at
FROM (VALUES 
    ('sarah.johnson@smithschool.edu', 'Sarah', 'Johnson'),
    ('alex.smith@smithschool.edu', 'Alex', 'Smith'),
    ('emma.davis@smithschool.edu', 'Emma', 'Davis'),
    ('michael.brown@smithschool.edu', 'Michael', 'Brown'),
    ('sophia.wilson@smithschool.edu', 'Sophia', 'Wilson'),
    ('james.martinez@smithschool.edu', 'James', 'Martinez'),
    ('olivia.taylor@smithschool.edu', 'Olivia', 'Taylor'),
    ('william.anderson@smithschool.edu', 'William', 'Anderson'),
    ('ava.thomas@smithschool.edu', 'Ava', 'Thomas'),
    ('benjamin.jackson@smithschool.edu', 'Benjamin', 'Jackson')
) as new_students(email, first_name, last_name)
WHERE NOT EXISTS (
    SELECT 1 FROM users WHERE email = new_students.email
);

-- Step 5: Check which students are already in the students table
SELECT 'Students already in students table:' as info;
SELECT s.student_id, u.first_name, u.last_name, c.grade_level
FROM students s
JOIN users u ON s.user_id = u.id
JOIN classes c ON s.class_id = c.id
WHERE u.email LIKE '%@smithschool.edu'
ORDER BY c.grade_level, u.first_name;

-- Step 6: Add students to students table (only if not already there)
INSERT INTO students (user_id, school_id, class_id, student_id, enrollment_date, is_active, created_at, updated_at)
SELECT 
    u.id,
    (SELECT s.id FROM schools s WHERE s.name LIKE '%Smith%' LIMIT 1) as school_id,
    CASE 
        WHEN u.first_name IN ('Sarah', 'Alex', 'Emma') THEN 
            (SELECT c.id FROM classes c JOIN schools s ON c.school_id = s.id WHERE s.name LIKE '%Smith%' AND c.grade_level = 5 LIMIT 1)
        WHEN u.first_name IN ('Michael', 'Sophia', 'James') THEN 
            (SELECT c.id FROM classes c JOIN schools s ON c.school_id = s.id WHERE s.name LIKE '%Smith%' AND c.grade_level = 6 LIMIT 1)
        WHEN u.first_name IN ('Olivia', 'William', 'Ava') THEN 
            (SELECT c.id FROM classes c JOIN schools s ON c.school_id = s.id WHERE s.name LIKE '%Smith%' AND c.grade_level = 7 LIMIT 1)
        ELSE 
            (SELECT c.id FROM classes c JOIN schools s ON c.school_id = s.id WHERE s.name LIKE '%Smith%' AND c.grade_level = 8 LIMIT 1)
    END as class_id,
    'ST' || LPAD(u.id::text, 6, '0') as student_id,
    NOW() as enrollment_date,
    true as is_active,
    NOW() as created_at,
    NOW() as updated_at
FROM users u 
WHERE u.email LIKE '%@smithschool.edu' 
  AND u.role = 'student'
  AND NOT EXISTS (
      SELECT 1 FROM students WHERE user_id = u.id
  );

-- Step 7: Show final results
SELECT 'Final Results:' as info;
SELECT 
    c.name as class_name,
    c.grade_level,
    COUNT(st.id) as student_count,
    STRING_AGG(u.first_name || ' ' || u.last_name, ', ') as students
FROM classes c
JOIN schools s ON c.school_id = s.id
LEFT JOIN students st ON c.id = st.class_id
LEFT JOIN users u ON st.user_id = u.id
WHERE s.name LIKE '%Smith%'
GROUP BY c.id, c.name, c.grade_level
ORDER BY c.grade_level, c.name;

-- Step 8: Summary
SELECT 'Summary:' as info;
SELECT 
    'Total Classes' as metric,
    COUNT(*) as count
FROM classes c
JOIN schools s ON c.school_id = s.id
WHERE s.name LIKE '%Smith%'

UNION ALL

SELECT 
    'Total Students' as metric,
    COUNT(st.id) as count
FROM classes c
JOIN schools s ON c.school_id = s.id
LEFT JOIN students st ON c.id = st.class_id
WHERE s.name LIKE '%Smith%'; 