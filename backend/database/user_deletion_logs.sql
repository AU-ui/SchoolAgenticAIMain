-- User Deletion Logs Table
CREATE TABLE IF NOT EXISTS user_deletion_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    user_email VARCHAR(255) NOT NULL,
    user_role VARCHAR(50) NOT NULL,
    tenant_id INTEGER REFERENCES tenants(id),
    tenant_name VARCHAR(255),
    deleted_by INTEGER REFERENCES users(id),
    deletion_reason TEXT NOT NULL,
    deleted_at TIMESTAMP DEFAULT NOW()
);

-- Add status column to users table if not exists
ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(20) DEFAULT 'active';
ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT NOW();

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_user_deletion_logs_user_id ON user_deletion_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_user_deletion_logs_deleted_at ON user_deletion_logs(deleted_at); 