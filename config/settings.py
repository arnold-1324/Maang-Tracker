"""
Configuration management for different environments
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.local')
load_dotenv()

class Config:
    """Base configuration"""
    
    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    
    # API Keys
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '5432'))
    DB_NAME = os.getenv('DB_NAME', 'maang_tracker')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
    
    @property
    def DATABASE_URL(self):
        """Construct database URL"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    @property
    def DATABASE_URL_ASYNC(self):
        """Async database URL for SQLAlchemy"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    # Redis
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    REDIS_DB = int(os.getenv('REDIS_DB', '0'))
    REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
    
    @property
    def REDIS_URL(self):
        """Construct Redis URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # RAG & Embeddings
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    EMBEDDING_DIMENSION = int(os.getenv('EMBEDDING_DIMENSION', '384'))
    LLM_MODEL = os.getenv('LLM_MODEL', 'gemini-2.0-flash')
    
    # RAG Settings
    RAG_CHUNK_SIZE = int(os.getenv('RAG_CHUNK_SIZE', '500'))
    RAG_CHUNK_OVERLAP = int(os.getenv('RAG_CHUNK_OVERLAP', '50'))
    RAG_SIMILARITY_THRESHOLD = float(os.getenv('RAG_SIMILARITY_THRESHOLD', '0.3'))
    RAG_TOP_K = int(os.getenv('RAG_TOP_K', '5'))
    
    # Flask
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', '5000'))
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # MCP Server
    MCP_HOST = os.getenv('MCP_HOST', 'localhost')
    MCP_PORT = int(os.getenv('MCP_PORT', '8765'))
    MCP_URL = os.getenv('MCP_URL', f'http://{MCP_HOST}:{MCP_PORT}')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Cache
    CACHE_TTL_DEFAULT = int(os.getenv('CACHE_TTL_DEFAULT', '3600'))  # 1 hour
    CACHE_TTL_SHORT = int(os.getenv('CACHE_TTL_SHORT', '300'))  # 5 minutes
    CACHE_TTL_LONG = int(os.getenv('CACHE_TTL_LONG', '86400'))  # 24 hours
    
    # Interview Settings
    INTERVIEW_TIME_LIMIT = int(os.getenv('INTERVIEW_TIME_LIMIT', '45'))  # minutes
    MAX_CONCURRENT_INTERVIEWS = int(os.getenv('MAX_CONCURRENT_INTERVIEWS', '10'))
    
    # Session
    SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '1800'))  # 30 minutes


class DevelopmentConfig(Config):
    """Development environment configuration"""
    ENVIRONMENT = 'development'
    DEBUG = True
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production environment configuration"""
    ENVIRONMENT = 'production'
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # Enforce security in production
    if not os.getenv('SECRET_KEY'):
        raise ValueError("SECRET_KEY environment variable must be set in production")


class TestingConfig(Config):
    """Testing environment configuration"""
    ENVIRONMENT = 'testing'
    DEBUG = True
    DB_NAME = 'maang_tracker_test'
    REDIS_DB = 15  # Separate Redis DB for tests
    LOG_LEVEL = 'DEBUG'


# Configuration factory
def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv('ENVIRONMENT', 'development').lower()
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }
    
    config_class = configs.get(env, DevelopmentConfig)
    return config_class()


# Export default config
config = get_config()
