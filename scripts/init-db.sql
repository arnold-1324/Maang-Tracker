-- Initial database setup
-- This runs automatically when PostgreSQL container starts

-- Create necessary functions and types
CREATE OR REPLACE FUNCTION updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Grant execution permissions
GRANT EXECUTE ON FUNCTION updated_at_column() TO PUBLIC;
