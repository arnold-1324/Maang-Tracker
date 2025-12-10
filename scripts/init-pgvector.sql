-- Initialize pgvector extension (optional, requires compiled extension)
-- CREATE EXTENSION IF NOT EXISTS vector;

-- For now, create a basic vector table without pgvector
-- Vector storage will be handled at application level
CREATE TABLE IF NOT EXISTS vector_embeddings (
    id SERIAL PRIMARY KEY,
    embedding_data BYTEA,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
