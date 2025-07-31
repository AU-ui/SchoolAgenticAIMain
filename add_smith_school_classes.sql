-- Add Classes to Smith School
-- This script creates classes for W H Smith School

-- First, let's check the current Smith School
SELECT 'Current Smith School:' as info;
SELECT id, name, tenant_id FROM schools WHERE name LIKE '%Smith%';

-- Get the Smith School ID
SELECT 'Smith School ID:' as info;
SELECT id, name FROM schools WHERE name LIKE '%Smith%';

-- Add Classes for Smith School
INSERT INTO classes (school_id, name, grade_level, academic_year, is_active, created_at, updated_at)
SELECT 
    (SELECT id FROM schools WHERE name LIKE '%Smith%' LIMIT 1) as school_id,
    'Grade ' || grade_level || 'A' as name,
    grade_level,
    '2024-2025' as academic_year,
    true as is_active,
    NOW() as created_at,
    NOW() as updated_at
FROM (VALUES (5), (6), (7), (8)) as grades(grade_level);

-- Show the classes we created
SELECT 'Created Classes:' as info;
SELECT c.id, c.name, c.grade_level, c.academic_year, s.name as school_name
FROM classes c
JOIN schools s ON c.school_id = s.id
WHERE s.name LIKE '%Smith%'
ORDER BY c.grade_level;

-- Show final results
SELECT 'Final Class Structure:' as info;
SELECT 
    s.name as school_name,
    c.name as class_name,
    c.grade_level,
    c.academic_year,
    COUNT(st.id) as student_count
FROM schools s
JOIN classes c ON s.id = c.school_id
LEFT JOIN students st ON c.id = st.class_id
WHERE s.name LIKE '%Smith%'
GROUP BY s.name, c.id, c.name, c.grade_level, c.academic_year
ORDER BY c.grade_level;

-- Summary
SELECT 'Summary:' as info;
SELECT 
    'Total Classes Created' as metric,
    COUNT(*) as count
FROM classes c
JOIN schools s ON c.school_id = s.id
WHERE s.name LIKE '%Smith%'

UNION ALL

SELECT 
    'Total Students in Classes' as metric,
    COUNT(st.id) as count
FROM classes c
JOIN schools s ON c.school_id = s.id
LEFT JOIN students st ON c.id = st.class_id
WHERE s.name LIKE '%Smith%'; 