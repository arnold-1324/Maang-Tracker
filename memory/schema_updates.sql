-- Drop new tables if they exist (for development/reset)
DROP TABLE IF EXISTS job_postings;
DROP TABLE IF EXISTS job_applications;
DROP TABLE IF EXISTS resume_versions;
DROP TABLE IF EXISTS ats_analysis;
DROP TABLE IF EXISTS learning_queue;
DROP TABLE IF EXISTS interview_prep;

-- Store crawled job details
CREATE TABLE job_postings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    title TEXT NOT NULL,
    location TEXT,
    url TEXT UNIQUE,
    description TEXT, -- Full JD text
    source TEXT, -- 'linkedin', 'google', 'career_page'
    min_experience INTEGER,
    tech_stack TEXT, -- JSON array of detected skills
    crawled_at DATETIME DEFAULT (datetime('now')),
    is_active BOOLEAN DEFAULT 1
);

-- Track applications and their status
CREATE TABLE job_applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    status TEXT DEFAULT 'wishlist', -- 'wishlist', 'applied', 'interviewing', 'offer', 'rejected'
    applied_at DATETIME,
    last_contact_at DATETIME,
    next_action_date DATETIME,
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES job_postings(id) ON DELETE CASCADE,
    UNIQUE(user_id, job_id)
);

-- Store tailored resumes for specific jobs
CREATE TABLE resume_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    job_id INTEGER, -- Can be NULL if it's a base resume
    version_name TEXT,
    content_tex TEXT, -- LaTeX content
    ats_score REAL,
    created_at DATETIME DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES job_postings(id) ON DELETE SET NULL
);

-- AI Analysis results (ATS Score & Feedback)
CREATE TABLE ats_analysis (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    score REAL, -- 0-100
    missing_skills TEXT, -- JSON array
    keyword_matches TEXT, -- JSON dictionary
    suggestions TEXT, -- AI feedback
    analyzed_at DATETIME DEFAULT (datetime('now')),
    FOREIGN KEY (resume_id) REFERENCES resume_versions(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES job_postings(id) ON DELETE CASCADE
);

-- Learning queue for missing skills
CREATE TABLE learning_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    skill_name TEXT NOT NULL,
    source_job_id INTEGER, -- Which job required this?
    priority TEXT DEFAULT 'medium', -- 'high', 'medium', 'low'
    status TEXT DEFAULT 'pending', -- 'pending', 'learning', 'mastered'
    resources TEXT, -- JSON array of links/books
    added_at DATETIME DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (source_job_id) REFERENCES job_postings(id) ON DELETE SET NULL
);

-- Interview preparation data
CREATE TABLE interview_prep (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    application_id INTEGER NOT NULL,
    round_type TEXT, -- 'screening', 'technical', 'system_design', 'behavioral'
    scheduled_at DATETIME,
    mock_questions TEXT, -- JSON array of AI-generated questions
    feedback TEXT,
    status TEXT DEFAULT 'scheduled',
    FOREIGN KEY (application_id) REFERENCES job_applications(id) ON DELETE CASCADE
);
