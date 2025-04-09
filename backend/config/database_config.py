"""
Database configuration for the Tournament Management System.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Database configuration
class DatabaseConfig:
    """Database configuration settings."""
    
    # MongoDB configuration
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'tms_db')
    MONGO_USERNAME = os.getenv('MONGO_USERNAME', '')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', '')
    
    # PostgreSQL configuration (alternative)
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', 5432))
    POSTGRES_DB_NAME = os.getenv('POSTGRES_DB_NAME', 'tms_db')
    POSTGRES_USERNAME = os.getenv('POSTGRES_USERNAME', 'postgres')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'postgres')
    
    # Database type (mongodb or postgresql)
    DB_TYPE = os.getenv('DB_TYPE', 'mongodb')
    
    @staticmethod
    def get_mongodb_uri():
        """Get MongoDB URI."""
        config = DatabaseConfig
        if config.MONGO_USERNAME and config.MONGO_PASSWORD:
            return f"mongodb://{config.MONGO_USERNAME}:{config.MONGO_PASSWORD}@{config.MONGO_HOST}:{config.MONGO_PORT}/{config.MONGO_DB_NAME}"
        return f"mongodb://{config.MONGO_HOST}:{config.MONGO_PORT}/{config.MONGO_DB_NAME}"
    
    @staticmethod
    def get_postgresql_uri():
        """Get PostgreSQL URI."""
        config = DatabaseConfig
        return f"postgresql://{config.POSTGRES_USERNAME}:{config.POSTGRES_PASSWORD}@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB_NAME}"
