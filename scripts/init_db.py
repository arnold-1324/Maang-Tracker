"""
Database initialization script
Run this to set up the database schema, create tables, and seed initial data
"""

import logging
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import config
from config.database import DatabaseManager
from database.models import Base

logging.basicConfig(level=config.LOG_LEVEL)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize database with all tables"""
    try:
        logger.info("Initializing database...")
        
        # Initialize connection
        DatabaseManager.initialize()
        
        # Get engine
        engine = DatabaseManager._engine
        
        # Create all tables
        logger.info("Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        logger.info("Database tables created successfully")
        
        # Seed initial data if needed
        seed_initial_data()
        
        logger.info("Database initialization complete")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def seed_initial_data():
    """Seed initial data into the database"""
    try:
        logger.info("Seeding initial data...")
        
        from config.database import DatabaseManager
        from database.models import RoadmapTopic, TopicCategory, DifficultyLevel
        
        with DatabaseManager.get_session_context() as session:
            # Check if topics already exist
            existing_count = session.query(RoadmapTopic).count()
            
            if existing_count > 0:
                logger.info(f"Database already has {existing_count} topics. Skipping seed.")
                return
            
            # Initial topics
            initial_topics = [
                {
                    "name": "Arrays & Strings",
                    "category": "dsa",
                    "difficulty": "beginner",
                    "priority": 1,
                    "description": "Master array and string manipulation techniques",
                    "estimated_hours": 8,
                },
                {
                    "name": "Linked Lists",
                    "category": "dsa",
                    "difficulty": "beginner",
                    "priority": 2,
                    "description": "Learn linked list data structure and operations",
                    "estimated_hours": 6,
                },
                {
                    "name": "Dynamic Programming",
                    "category": "dsa",
                    "difficulty": "advanced",
                    "priority": 3,
                    "description": "Master DP patterns and optimization techniques",
                    "estimated_hours": 12,
                },
                {
                    "name": "System Design Fundamentals",
                    "category": "system_design",
                    "difficulty": "intermediate",
                    "priority": 4,
                    "description": "Learn system design principles and architecture",
                    "estimated_hours": 20,
                },
                {
                    "name": "Behavioral Interview",
                    "category": "behavioral",
                    "difficulty": "beginner",
                    "priority": 5,
                    "description": "Prepare for behavioral rounds with STAR method",
                    "estimated_hours": 4,
                },
            ]
            
            for topic_data in initial_topics:
                topic = RoadmapTopic(**topic_data)
                session.add(topic)
            
            session.commit()
            logger.info(f"Seeded {len(initial_topics)} initial topics")
            
    except Exception as e:
        logger.warning(f"Failed to seed initial data: {e}")


def create_cache_tables():
    """Create cache-related tables"""
    try:
        logger.info("Setting up cache tables...")
        
        with DatabaseManager.get_session_context() as session:
            # Cache entries cleanup (optional - mainly uses Redis)
            pass
        
        logger.info("Cache setup complete")
        
    except Exception as e:
        logger.warning(f"Cache setup warning: {e}")


def verify_database():
    """Verify database connection and basic operations"""
    try:
        logger.info("Verifying database...")
        
        with DatabaseManager.get_session_context() as session:
            # Test basic query
            from database.models import User
            user_count = session.query(User).count()
            logger.info(f"Database verification successful. Users: {user_count}")
            
        return True
        
    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        return False


if __name__ == "__main__":
    try:
        logger.info(f"Starting database initialization for {config.ENVIRONMENT} environment")
        logger.info(f"Database: {config.DATABASE_URL}")
        
        init_database()
        create_cache_tables()
        
        if verify_database():
            logger.info("✅ Database initialization complete and verified")
            sys.exit(0)
        else:
            logger.error("❌ Database verification failed")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        sys.exit(1)
