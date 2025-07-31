-- Create user_deletion_logs table for tracking account deletions
CREATE TABLE IF NOT EXISTS user_deletion_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    reason TEXT,
    deleted_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add index for better performance
CREATE INDEX IF NOT EXISTS idx_user_deletion_logs_user_id ON user_deletion_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_user_deletion_logs_deleted_at ON user_deletion_logs(deleted_at);

-- Add comment to table
COMMENT ON TABLE user_deletion_logs IS 'Logs for tracking user account deletions with reasons';

-- Add missing columns to users table if they don't exist
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS address TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS bio TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW(); 