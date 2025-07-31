-- Add Students to Smith School
-- This script adds multiple students to the Smith School

-- First, let's check the current school structure
SELECT 'Current Schools:' as info;
SELECT id, name, tenant_id FROM schools WHERE name LIKE '%Smith%';

SELECT 'Current Classes:' as info;
SELECT c.id, c.name, c.grade_level, s.name as school_name 
FROM classes c 
JOIN schools s ON c.school_id = s.id 
WHERE s.name LIKE '%Smith%';

-- Add Student Users (if they don't exist)
INSERT INTO users (email, password, first_name, last_name, role, tenant_id, is_active, created_at, updated_at)
VALUES 
    ('sarah.johnson@smithschool.edu', '$2b$10$hashedpassword', 'Sarah', 'Johnson', 'student', 2, true, NOW(), NOW()),
    ('alex.smith@smithschool.edu', '$2b$10$hashedpassword', 'Alex', 'Smith', 'student', 2, true, NOW(), NOW()),
    ('emma.davis@smithschool.edu', '$2b$10$hashedpassword', 'Emma', 'Davis', 'student', 2, true, NOW(), NOW()),
    ('michael.brown@smithschool.edu', '$2b$10$hashedpassword', 'Michael', 'Brown', 'student', 2, true, NOW(), NOW()),
    ('sophia.wilson@smithschool.edu', '$2b$10$hashedpassword', 'Sophia', 'Wilson', 'student', 2, true, NOW(), NOW()),
    ('james.martinez@smithschool.edu', '$2b$10$hashedpassword', 'James', 'Martinez', 'student', 2, true, NOW(), NOW()),
    ('olivia.taylor@smithschool.edu', '$2b$10$hashedpassword', 'Olivia', 'Taylor', 'student', 2, true, NOW(), NOW()),
    ('william.anderson@smithschool.edu', '$2b$10$hashedpassword', 'William', 'Anderson', 'student', 2, true, NOW(), NOW()),
    ('ava.thomas@smithschool.edu', '$2b$10$hashedpassword', 'Ava', 'Thomas', 'student', 2, true, NOW(), NOW()),
    ('benjamin.jackson@smithschool.edu', '$2b$10$hashedpassword', 'Benjamin', 'Jackson', 'student', 2, true, NOW(), NOW());

-- Get the user IDs we just created
SELECT 'Created Student Users:' as info;
SELECT id, email, first_name, last_name FROM users 
WHERE email LIKE '%@smithschool.edu' AND role = 'student';

-- Get Smith School ID
SELECT 'Smith School ID:' as info;
SELECT id, name FROM schools WHERE name LIKE '%Smith%';

-- Add Students to the students table (using class_id instead of grade_level)
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
WHERE u.email LIKE '%@smithschool.edu' AND u.role = 'student';

-- Show the students we created
SELECT 'Created Students:' as info;
SELECT s.student_id, c.grade_level, u.first_name, u.last_name, u.email
FROM students s
JOIN users u ON s.user_id = u.id
JOIN classes c ON s.class_id = c.id
WHERE u.email LIKE '%@smithschool.edu'
ORDER BY c.grade_level, u.first_name;

-- Show final results
SELECT 'Final Student-Class Assignments:' as info;
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

-- Summary
SELECT 'Summary:' as info;
SELECT 
    'Total Students Added' as metric,
    COUNT(*) as count
FROM students s
JOIN users u ON s.user_id = u.id
WHERE u.email LIKE '%@smithschool.edu'

UNION ALL

SELECT 
    'Total Classes with Students' as metric,
    COUNT(DISTINCT s.class_id) as count
FROM students s
JOIN users u ON s.user_id = u.id
WHERE u.email LIKE '%@smithschool.edu'; 