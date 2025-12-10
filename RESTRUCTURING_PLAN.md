# Maang-Tracker Restructuring Plan

## Overview
Restructure the entire Maang-Tracker platform to use PostgreSQL, implement RAG-based memory, add Redis caching, and containerize everything for production deployment.

## Architecture Changes

### Current Stack
- **Database**: SQLite (memory.db)
- **Cache**: In-memory caching in Python
- **Memory**: Basic conversation history storage
- **ORM**: Raw SQL queries
- **Deployment**: Standalone applications

### New Stack
- **Database**: PostgreSQL 15 with pgvector extension
- **Cache**: Redis (distributed caching)
- **Memory**: RAG-based semantic memory with vector embeddings
- **ORM**: SQLAlchemy with connection pooling
- **Search**: Vector similarity search with pgvector
- **Deployment**: Docker Compose with multi-container orchestration

## Directory Structure

```
Maang-Tracker/
├── config/
│   ├── __init__.py
│   ├── settings.py           (Environment-based configuration)
│   ├── database.py           (Database connection setup)
│   └── constants.py          (Constants and enums)
├── database/
│   ├── __init__.py
│   ├── models.py             (SQLAlchemy models)
│   ├── migrations/           (Alembic migrations)
│   │   ├── alembic.ini
│   │   └── versions/
│   └── seed.py               (Database seeding)
├── memory/
│   ├── __init__.py
│   ├── rag_engine.py         (RAG core - vector embeddings, retrieval)
│   ├── memory_manager.py     (Memory persistence with PostgreSQL)
│   ├── vector_store.py       (Vector database operations)
│   └── embedding_service.py  (Embedding generation)
├── cache/
│   ├── __init__.py
│   └── redis_manager.py      (Redis caching layer)
├── services/
│   ├── __init__.py
│   ├── user_service.py
│   ├── interview_service.py
│   ├── training_service.py
│   └── tracking_service.py
├── docker/
│   ├── Dockerfile.app
│   ├── Dockerfile.mcp
│   ├── Dockerfile.dashboard
│   ├── docker-compose.yml
│   └── .env.example
├── scripts/
│   ├── migrate_sqlite_to_pg.py    (Migration script)
│   └── init_db.py
└── ... (existing files)
```

## Key Components

### 1. RAG Memory System
- **Vector Embeddings**: Use sentence-transformers or OpenAI embeddings
- **Vector Store**: pgvector PostgreSQL extension
- **Retrieval**: Semantic search for relevant conversation context
- **Integration**: Used by agent for better context awareness

### 2. PostgreSQL Migration
- Replace all SQLite tables with PostgreSQL equivalents
- Add vector embeddings table for RAG
- Add indexes for performance
- Connection pooling with SQLAlchemy

### 3. Redis Caching
- Cache frequently accessed data
- Cache interview questions, user stats
- Cache embedding vectors temporarily
- Session management

### 4. Docker Orchestration
- PostgreSQL 15 service with pgvector
- Redis service
- pgAdmin for database management
- Dashboard (Flask)
- MCP Server
- Agent service
- Migration service

## Implementation Steps

1. **Setup Config Management**
   - Create environment-based settings
   - Configure database connections
   - Setup logging

2. **Create PostgreSQL Migrations**
   - Use Alembic for version control
   - Create all tables from SQLite schema
   - Add RAG vector tables

3. **Implement RAG System**
   - Vector embedding service
   - Memory manager with semantic search
   - Integration with agent

4. **Setup Redis Caching**
   - Cache manager
   - Integration with services

5. **Docker Containerization**
   - Create Dockerfiles for each service
   - Setup docker-compose
   - Add health checks and logging

6. **Refactor Core Services**
   - Update agent to use new database
   - Update interview engine
   - Update training system
   - Update dashboard

7. **Testing & Validation**
   - Unit tests for RAG retrieval
   - Integration tests for database
   - End-to-end tests with Docker
   - Performance benchmarks

## Benefits

✅ **Scalability**: PostgreSQL handles millions of records
✅ **Performance**: Redis caching + connection pooling
✅ **Intelligence**: RAG enables context-aware responses
✅ **Reliability**: Persistent storage + backup capabilities
✅ **Deployment**: Easy containerization and orchestration
✅ **Maintainability**: ORM + migrations + clean architecture
✅ **Observability**: Centralized logging and monitoring

## Timeline

- Phase 1: Config & Database Setup (2-3 hours)
- Phase 2: PostgreSQL Migration (2-3 hours)
- Phase 3: RAG Implementation (3-4 hours)
- Phase 4: Redis Integration (1-2 hours)
- Phase 5: Docker Setup (2-3 hours)
- Phase 6: Testing & Validation (2-3 hours)

**Total: ~13-18 hours of implementation**
