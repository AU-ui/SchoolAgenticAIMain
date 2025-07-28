-- Syllabus and Question Papers Tables

-- Education Boards
CREATE TABLE IF NOT EXISTS education_boards (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    country VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Syllabus Table
CREATE TABLE IF NOT EXISTS syllabus (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    subject VARCHAR(100) NOT NULL,
    class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    board_id INTEGER REFERENCES education_boards(id) ON DELETE CASCADE,
    teacher_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
    uploaded_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Subjects Table
CREATE TABLE IF NOT EXISTS subjects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Question Papers Table
CREATE TABLE IF NOT EXISTS question_papers (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    class_id INTEGER REFERENCES classes(id) ON DELETE CASCADE,
    subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
    syllabus_id INTEGER REFERENCES syllabus(id) ON DELETE CASCADE,
    total_marks INTEGER NOT NULL,
    duration INTEGER NOT NULL, -- in minutes
    filename VARCHAR(255),
    teacher_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    tenant_id INTEGER REFERENCES tenants(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Question Paper Sections Table
CREATE TABLE IF NOT EXISTS question_paper_sections (
    id SERIAL PRIMARY KEY,
    question_paper_id INTEGER REFERENCES question_papers(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    marks INTEGER NOT NULL,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert sample data
INSERT INTO education_boards (name, description, country) VALUES
('CBSE', 'Central Board of Secondary Education', 'India'),
('ICSE', 'Indian Certificate of Secondary Education', 'India'),
('State Board', 'State Board of Education', 'India'),
('International Board', 'International Baccalaureate', 'International');

INSERT INTO subjects (name, description) VALUES
('Mathematics', 'Advanced mathematics including algebra, geometry, and calculus'),
('Science', 'Physics, Chemistry, and Biology'),
('English', 'English language and literature'),
('History', 'World history and social studies'),
('Geography', 'Physical and human geography'),
('Computer Science', 'Programming and computer fundamentals'),
('Art', 'Visual arts and creative expression'),
('Physical Education', 'Sports and physical fitness'); 