-- ============================================================================
-- SMART ATTENDANCE SYSTEM - COMPLETE DATABASE SCHEMA
-- ============================================================================
-- PostgreSQL-based AI/ML attendance tracking system
-- Features: Present/Absent/Late marking, pattern analysis, AI predictions
-- ============================================================================

-- First, create the basic tables that attendance depends on

-- Users table (if not exists)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('superadmin', 'admin', 'administrator', 'teacher', 'parent', 'student')),
    profile_picture_url TEXT,
    phone VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Schools table (if not exists)
CREATE TABLE IF NOT EXISTS schools (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(50),
    email VARCHAR(255),
    principal_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Classes table (if not exists)
CREATE TABLE IF NOT EXISTS classes (
    id SERIAL PRIMARY KEY,
    school_id INTEGER REFERENCES schools(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    grade_level INTEGER,
    academic_year VARCHAR(20),
    teacher_id INTEGER REFERENCES users(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Now create the attendance tables

-- Attendance Sessions Table
-- Tracks each attendance session (class period, date, teacher)
CREATE TABLE IF NOT EXISTS attendance_sessions (
    session_id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    session_date DATE NOT NULL,
    session_time TIME NOT NULL,
    session_type VARCHAR(50) DEFAULT 'regular', -- regular, exam, special
    status VARCHAR(20) DEFAULT 'active', -- active, completed, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_attendance_sessions_class FOREIGN KEY (class_id) REFERENCES classes(id),
    CONSTRAINT fk_attendance_sessions_teacher FOREIGN KEY (teacher_id) REFERENCES users(id),
    
    -- Unique constraint to prevent duplicate sessions
    CONSTRAINT unique_session UNIQUE (class_id, session_date, session_time)
);

-- Attendance Records Table
-- Individual student attendance for each session
CREATE TABLE IF NOT EXISTS attendance_records (
    record_id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('present', 'absent', 'late', 'excused')),
    arrival_time TIME,
    departure_time TIME,
    notes TEXT,
    marked_by INTEGER NOT NULL, -- teacher who marked attendance
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_attendance_records_session FOREIGN KEY (session_id) REFERENCES attendance_sessions(session_id),
    CONSTRAINT fk_attendance_records_student FOREIGN KEY (student_id) REFERENCES users(id),
    CONSTRAINT fk_attendance_records_marked_by FOREIGN KEY (marked_by) REFERENCES users(id),
    
    -- Unique constraint to prevent duplicate records
    CONSTRAINT unique_attendance_record UNIQUE (session_id, student_id)
);

-- Attendance Analytics Table
-- Pre-calculated analytics for fast reporting
CREATE TABLE IF NOT EXISTS attendance_analytics (
    analytics_id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    period_type VARCHAR(20) NOT NULL, -- daily, weekly, monthly, quarterly, yearly
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    total_sessions INTEGER DEFAULT 0,
    present_count INTEGER DEFAULT 0,
    absent_count INTEGER DEFAULT 0,
    late_count INTEGER DEFAULT 0,
    excused_count INTEGER DEFAULT 0,
    attendance_percentage DECIMAL(5,2) DEFAULT 0.00,
    ai_prediction VARCHAR(50), -- predicted attendance pattern
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_attendance_analytics_student FOREIGN KEY (student_id) REFERENCES users(id),
    CONSTRAINT fk_attendance_analytics_class FOREIGN KEY (class_id) REFERENCES classes(id),
    
    -- Unique constraint for analytics
    CONSTRAINT unique_analytics UNIQUE (student_id, class_id, period_type, period_start, period_end)
);

-- Performance Indexes for Fast Queries
CREATE INDEX IF NOT EXISTS idx_attendance_sessions_class_date ON attendance_sessions(class_id, session_date);
CREATE INDEX IF NOT EXISTS idx_attendance_sessions_teacher ON attendance_sessions(teacher_id);
CREATE INDEX IF NOT EXISTS idx_attendance_records_session ON attendance_records(session_id);
CREATE INDEX IF NOT EXISTS idx_attendance_records_student ON attendance_records(student_id);
CREATE INDEX IF NOT EXISTS idx_attendance_analytics_student_period ON attendance_analytics(student_id, period_type, period_start);

-- Comments for Documentation
COMMENT ON TABLE attendance_sessions IS 'Tracks attendance sessions for classes';
COMMENT ON TABLE attendance_records IS 'Individual student attendance records';
COMMENT ON TABLE attendance_analytics IS 'Pre-calculated attendance analytics for reporting';

COMMENT ON COLUMN attendance_sessions.session_type IS 'Type of session: regular, exam, special event';
COMMENT ON COLUMN attendance_records.status IS 'Attendance status: present, absent, late, or excused';
COMMENT ON COLUMN attendance_analytics.ai_prediction IS 'AI-generated attendance pattern prediction';