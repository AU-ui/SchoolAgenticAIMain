# Parent-Child Relationship Setup Guide

## Overview
This guide explains how to set up parent-child relationships in the EdTech platform and how the synchronization works between Teacher → Student → Parent dashboards.

## Database Structure

### Key Tables:
```sql
-- Users table (all users)
users (id, email, first_name, last_name, role, tenant_id)

-- Parents table (links to users)
parents (id, user_id, occupation, address, is_active)

-- Students table (links to users)
students (id, user_id, class_id, school_id, is_active)

-- Parent-Student relationships (the key table!)
parent_students (id, parent_id, student_id, relationship, is_primary)
```

## Setup Instructions

### Step 1: Run the Database Setup Script
```bash
cd backend
node setup-parent-child-relationships.js
```

This script will:
- Create parent records for users with 'parent' role
- Link parents to students via the `parent_students` table
- Verify the relationships are properly established

### Step 2: Insert Sample Data (Optional)
```bash
# Run the sample data SQL script
psql -d your_database -f database/sample_parent_child_data.sql
```

### Step 3: Test the Setup
```bash
node test-parent-child-relationships.js
```

## How Synchronization Works

### Teacher → Student → Parent Flow:

1. **Teacher Marks Attendance:**
   ```javascript
   POST /api/attendance/teacher/save
   {
     "class_id": 1,
     "date": "2025-02-15",
     "attendance_data": [
       {"student_id": 1, "status": "present"},
       {"student_id": 2, "status": "absent"}
     ]
   }
   ```

2. **Data Saved to Database:**
   ```sql
   INSERT INTO attendance_records (student_id, class_id, date, status)
   VALUES (1, 1, '2025-02-15', 'present');
   ```

3. **Student Views Their Attendance:**
   ```javascript
   GET /api/attendance/student/my-attendance?month=1&year=2025
   ```

4. **Parent Views Child's Attendance:**
   ```javascript
   GET /api/students/1/attendance?month=1&year=2025
   ```

### Security & Access Control:

- **Teachers**: Can only see/mark attendance for their assigned classes
- **Students**: Can only see their own attendance
- **Parents**: Can only see their children's attendance (via `parent_students` table)
- **Admins**: Can see all attendance data for their school

## API Endpoints

### Parent Endpoints:
- `GET /api/parent/children` - Get all children for authenticated parent
- `GET /api/parents/:parentId/children` - Get children for specific parent (with access control)
- `GET /api/parent/dashboard` - Get parent dashboard data

### Student Endpoints:
- `GET /api/students/:studentId/attendance` - Get student attendance (with parent access control)
- `GET /api/student/dashboard` - Get student dashboard data

### Teacher Endpoints:
- `GET /api/attendance/teacher/classes` - Get teacher's classes
- `POST /api/attendance/teacher/save` - Save attendance

## Testing the System

### 1. Test Parent Dashboard:
```bash
# Login as parent user
# Navigate to Parent Dashboard
# Verify child list loads
# Verify attendance data displays
```

### 2. Test Teacher Dashboard:
```bash
# Login as teacher
# Mark attendance for students
# Verify data appears in student and parent dashboards
```

### 3. Test Student Dashboard:
```bash
# Login as student
# View attendance data
# Verify it matches teacher's records
```

## Troubleshooting

### Common Issues:

1. **Parent Dashboard shows no children:**
   - Check if parent-student relationships exist in `parent_students` table
   - Verify parent user has 'parent' role
   - Run setup script again

2. **Access denied errors:**
   - Check if parent is linked to student via `parent_students` table
   - Verify user roles and permissions

3. **Attendance data not syncing:**
   - Check if attendance records exist in `attendance_records` table
   - Verify class and student relationships

### Debug Queries:

```sql
-- Check parent-student relationships
SELECT 
  pu.first_name || ' ' || pu.last_name as parent_name,
  su.first_name || ' ' || su.last_name as student_name
FROM parent_students ps
JOIN parents p ON ps.parent_id = p.id
JOIN users pu ON p.user_id = pu.id
JOIN students s ON ps.student_id = s.id
JOIN users su ON s.user_id = su.id;

-- Check attendance records
SELECT 
  ar.date,
  ar.status,
  su.first_name || ' ' || su.last_name as student_name
FROM attendance_records ar
JOIN students s ON ar.student_id = s.id
JOIN users su ON s.user_id = su.id
ORDER BY ar.date DESC;
```

## Security Features

1. **Role-based Access Control**: Users can only access data appropriate for their role
2. **Parent-Child Relationship Validation**: Parents can only see their linked children's data
3. **API Endpoint Protection**: All endpoints validate user permissions before returning data
4. **Database-level Security**: Foreign key constraints ensure data integrity

## Future Enhancements

1. **Real-time Updates**: WebSocket connections for live attendance updates
2. **Push Notifications**: Alerts when attendance is marked or absences detected
3. **Email/SMS Alerts**: Automated notifications for attendance issues
4. **Advanced Analytics**: ML-powered attendance predictions and insights
5. **Mobile App**: Native mobile applications for better accessibility

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Run the test script to verify setup
3. Check database logs for errors
4. Verify all API endpoints are properly configured
