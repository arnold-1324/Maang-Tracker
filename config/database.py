"""
Database configuration and connection management
"""

from sqlalchemy import create_engine, event, pool
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from typing import Optional, Generator
import logging
from config.settings import config

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database connections and sessions"""
    
    _engine = None
    _session_factory = None
    
    @classmethod
    def initialize(cls):
        """Initialize database connection pool"""
        if cls._engine is not None:
            return
        
        try:
            # Create engine with connection pooling
            cls._engine = create_engine(
                config.DATABASE_URL,
                poolclass=QueuePool,
                pool_size=20,  # Number of connections to maintain in pool
                max_overflow=40,  # Max overflow connections
                pool_recycle=3600,  # Recycle connections after 1 hour
                pool_pre_ping=True,  # Test connections before using
                echo=config.DEBUG,  # Log SQL queries in debug mode
                connect_args={
                    'connect_timeout': 10,
                    'application_name': 'maang_tracker',
                }
            )
            
            # Create session factory
            cls._session_factory = sessionmaker(
                bind=cls._engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )
            
            # Setup event listeners
            cls._setup_event_listeners()
            
            # Test connection
            with cls._engine.connect() as conn:
                conn.execute('SELECT 1')
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
    
    @classmethod
    def _setup_event_listeners(cls):
        """Setup SQLAlchemy event listeners"""
        
        @event.listens_for(cls._engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            """Enable pgvector extension on connect"""
            cursor = dbapi_conn.cursor()
            try:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                dbapi_conn.commit()
            except Exception:
                pass  # Extension might already exist
            finally:
                cursor.close()
        
        @event.listens_for(cls._engine, "connect")
        def receive_connect_app_name(dbapi_conn, connection_record):
            """Set application name for monitoring"""
            try:
                dbapi_conn.set_isolation_level(0)
                dbapi_conn.cursor().execute("SET application_name = 'maang_tracker'")
                dbapi_conn.set_isolation_level(1)
            except Exception:
                pass
    
    @classmethod
    def get_session(cls) -> Session:
        """Get new database session"""
        if cls._session_factory is None:
            cls.initialize()
        return cls._session_factory()
    
    @classmethod
    def get_session_context(cls) -> Generator[Session, None, None]:
        """Context manager for session"""
        session = cls.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    @classmethod
    def execute(cls, query):
        """Execute raw SQL query"""
        with cls.get_session_context() as session:
            return session.execute(query)
    
    @classmethod
    def dispose(cls):
        """Dispose of connection pool"""
        if cls._engine:
            cls._engine.dispose()
            logger.info("Database connection pool disposed")


# Dependency injection helper
def get_db() -> Generator[Session, None, None]:
    """FastAPI/Flask dependency for database session"""
    with DatabaseManager.get_session_context() as session:
        yield session


# Initialize on module import
try:
    DatabaseManager.initialize()
except Exception as e:
    logger.warning(f"Database not available yet: {e}")
