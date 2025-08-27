-- ============================================================================
-- QR CODE ATTENDANCE SYSTEM - DATABASE SCHEMA
-- ============================================================================
-- PostgreSQL-based QR code attendance tracking system
-- Features: QR code generation, scanning, session management
-- ============================================================================

-- QR Attendance Sessions Table
-- Tracks QR code sessions for attendance
CREATE TABLE IF NOT EXISTS qr_attendance_sessions (
    id SERIAL PRIMARY KEY,
    class_id INTEGER NOT NULL,
    teacher_id INTEGER NOT NULL,
    session_date DATE NOT NULL,
    session_time TIME NOT NULL,
    qr_data JSONB NOT NULL, -- Stores QR code data as JSON
    expiry_time TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_qr_sessions_class FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    CONSTRAINT fk_qr_sessions_teacher FOREIGN KEY (teacher_id) REFERENCES users(id) ON DELETE CASCADE,
    
    -- Unique constraint to prevent duplicate QR sessions
    CONSTRAINT unique_qr_session UNIQUE (class_id, session_date, session_time)
);

-- QR Code Scans Table
-- Tracks each QR code scan for audit purposes
CREATE TABLE IF NOT EXISTS qr_code_scans (
    id SERIAL PRIMARY KEY,
    qr_session_id INTEGER NOT NULL,
    student_id INTEGER NOT NULL,
    scanned_by INTEGER NOT NULL, -- Who scanned the QR code
    scan_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    device_info JSONB, -- Store device information
    location_info JSONB, -- Store location if available
    scan_result VARCHAR(50) NOT NULL, -- success, expired, invalid, duplicate
    
    -- Foreign key constraints
    CONSTRAINT fk_qr_scans_session FOREIGN KEY (qr_session_id) REFERENCES qr_attendance_sessions(id) ON DELETE CASCADE,
    CONSTRAINT fk_qr_scans_student FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_qr_scans_scanned_by FOREIGN KEY (scanned_by) REFERENCES users(id) ON DELETE CASCADE
);

-- QR Code Analytics Table
-- Pre-calculated analytics for QR code usage
CREATE TABLE IF NOT EXISTS qr_attendance_analytics (
    analytics_id SERIAL PRIMARY KEY,
    qr_session_id INTEGER NOT NULL,
    class_id INTEGER NOT NULL,
    total_scans INTEGER DEFAULT 0,
    successful_scans INTEGER DEFAULT 0,
    failed_scans INTEGER DEFAULT 0,
    duplicate_scans INTEGER DEFAULT 0,
    average_scan_time DECIMAL(5,2), -- Average time to scan in seconds
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_qr_analytics_session FOREIGN KEY (qr_session_id) REFERENCES qr_attendance_sessions(id) ON DELETE CASCADE,
    CONSTRAINT fk_qr_analytics_class FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
);

-- Performance Indexes for Fast Queries
CREATE INDEX IF NOT EXISTS idx_qr_sessions_class_date ON qr_attendance_sessions(class_id, session_date);
CREATE INDEX IF NOT EXISTS idx_qr_sessions_teacher ON qr_attendance_sessions(teacher_id);
CREATE INDEX IF NOT EXISTS idx_qr_sessions_expiry ON qr_attendance_sessions(expiry_time);
CREATE INDEX IF NOT EXISTS idx_qr_scans_session ON qr_code_scans(qr_session_id);
CREATE INDEX IF NOT EXISTS idx_qr_scans_student ON qr_code_scans(student_id);
CREATE INDEX IF NOT EXISTS idx_qr_scans_timestamp ON qr_code_scans(scan_timestamp);

-- Comments for Documentation
COMMENT ON TABLE qr_attendance_sessions IS 'QR code sessions for attendance tracking';
COMMENT ON TABLE qr_code_scans IS 'Audit trail of QR code scans';
COMMENT ON TABLE qr_attendance_analytics IS 'Analytics for QR code attendance usage';

-- ============================================================================
-- SAMPLE DATA FOR TESTING
-- ============================================================================

-- Insert sample QR session (uncomment to test)
/*
INSERT INTO qr_attendance_sessions (
    class_id, 
    teacher_id, 
    session_date, 
    session_time, 
    qr_data, 
    expiry_time
) VALUES (
    7, -- Class ID
    5, -- Teacher ID
    CURRENT_DATE,
    '09:00:00',
    '{"class_id": 7, "teacher_id": 5, "session_date": "2024-01-01", "session_time": "09:00:00", "timestamp": "2024-01-01T09:00:00Z"}',
    CURRENT_TIMESTAMP + INTERVAL '30 minutes'
);
*/

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to clean up expired QR sessions
CREATE OR REPLACE FUNCTION cleanup_expired_qr_sessions()
RETURNS void AS $$
BEGIN
    UPDATE qr_attendance_sessions 
    SET is_active = false 
    WHERE expiry_time < NOW() AND is_active = true;
END;
$$ LANGUAGE plpgsql;

-- Function to get QR session statistics
CREATE OR REPLACE FUNCTION get_qr_session_stats(session_id INTEGER)
RETURNS TABLE(
    total_scans INTEGER,
    successful_scans INTEGER,
    failed_scans INTEGER,
    duplicate_scans INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total_scans,
        COUNT(CASE WHEN scan_result = 'success' THEN 1 END)::INTEGER as successful_scans,
        COUNT(CASE WHEN scan_result IN ('expired', 'invalid') THEN 1 END)::INTEGER as failed_scans,
        COUNT(CASE WHEN scan_result = 'duplicate' THEN 1 END)::INTEGER as duplicate_scans
    FROM qr_code_scans
    WHERE qr_session_id = session_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- ============================================================================

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_qr_sessions_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_qr_sessions_updated_at
    BEFORE UPDATE ON qr_attendance_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_qr_sessions_updated_at();

-- ============================================================================
-- VIEWS FOR EASY QUERYING
-- ============================================================================

-- View for active QR sessions
CREATE OR REPLACE VIEW active_qr_sessions AS
SELECT 
    qs.id,
    qs.class_id,
    c.name as class_name,
    qs.teacher_id,
    u.first_name || ' ' || u.last_name as teacher_name,
    qs.session_date,
    qs.session_time,
    qs.expiry_time,
    qs.is_active,
    CASE 
        WHEN qs.expiry_time > NOW() THEN 'active'
        ELSE 'expired'
    END as status
FROM qr_attendance_sessions qs
JOIN classes c ON qs.class_id = c.id
JOIN users u ON qs.teacher_id = u.id
WHERE qs.is_active = true;

-- View for QR session analytics
CREATE OR REPLACE VIEW qr_session_analytics AS
SELECT 
    qs.id as qr_session_id,
    qs.class_id,
    c.name as class_name,
    qs.session_date,
    qs.session_time,
    COUNT(qcs.id) as total_scans,
    COUNT(CASE WHEN qcs.scan_result = 'success' THEN 1 END) as successful_scans,
    COUNT(CASE WHEN qcs.scan_result IN ('expired', 'invalid') THEN 1 END) as failed_scans,
    COUNT(CASE WHEN qcs.scan_result = 'duplicate' THEN 1 END) as duplicate_scans,
    ROUND(
        COUNT(CASE WHEN qcs.scan_result = 'success' THEN 1 END) * 100.0 / 
        NULLIF(COUNT(qcs.id), 0), 2
    ) as success_rate
FROM qr_attendance_sessions qs
JOIN classes c ON qs.class_id = c.id
LEFT JOIN qr_code_scans qcs ON qs.id = qcs.qr_session_id
GROUP BY qs.id, qs.class_id, c.name, qs.session_date, qs.session_time;

-- ============================================================================
-- SECURITY POLICIES (if using Row Level Security)
-- ============================================================================

-- Enable RLS on qr_attendance_sessions
ALTER TABLE qr_attendance_sessions ENABLE ROW LEVEL SECURITY;

-- Policy for teachers to see only their QR sessions
CREATE POLICY teacher_qr_sessions_policy ON qr_attendance_sessions
    FOR ALL TO authenticated
    USING (teacher_id = current_setting('app.current_user_id')::INTEGER);

-- Policy for admins to see all QR sessions
CREATE POLICY admin_qr_sessions_policy ON qr_attendance_sessions
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = current_setting('app.current_user_id')::INTEGER 
            AND role IN ('admin', 'superadmin')
        )
    );

-- ============================================================================
-- END OF QR CODE ATTENDANCE SCHEMA
-- ============================================================================
