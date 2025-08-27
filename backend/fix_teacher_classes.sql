-- Fix Teacher Classes Assignment
-- This script assigns classes to teacher ID 5

-- First, let's see what we have
SELECT 'Current Users:' as info;
SELECT id, email, first_name, last_name, role FROM users ORDER BY id;

SELECT 'Current Classes:' as info;
SELECT id, name, teacher_id, grade_level, academic_year FROM classes ORDER BY id;

SELECT 'Classes for Teacher 5:' as info;
SELECT id, name, teacher_id, grade_level FROM classes WHERE teacher_id = 5;

-- Update classes to assign to teacher 5
UPDATE classes 
SET teacher_id = 5 
WHERE id IN (1, 2, 3, 4, 5)
AND teacher_id IS NULL OR teacher_id != 5;

-- Verify the update
SELECT 'Updated Classes for Teacher 5:' as info;
SELECT id, name, teacher_id, grade_level FROM classes WHERE teacher_id = 5;

-- Also check if we have any classes at all
SELECT 'Total Classes Count:' as info;
SELECT COUNT(*) as total_classes FROM classes;

SELECT 'Classes with Teachers:' as info;
SELECT teacher_id, COUNT(*) as class_count 
FROM classes 
GROUP BY teacher_id 
ORDER BY teacher_id;
