"""
Database initialization script for the Tournament Management System.
This script initializes the database based on the configured database type.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.database_config import DatabaseConfig
from app.models.database import DatabaseConfig as MongoConfig, initialize_database as initialize_mongo

try:
    from app.models.postgresql_schema import initialize_database as initialize_postgres
except ImportError:
    print("SQLAlchemy not installed. PostgreSQL initialization skipped.")

def init_db():
    """Initialize the database based on the configured database type."""
    load_dotenv()
    
    db_type = os.getenv('DB_TYPE', 'mongodb')
    
    if db_type.lower() == 'mongodb':
        print("Initializing MongoDB database...")
        mongo_config = MongoConfig(
            host=DatabaseConfig.MONGO_HOST,
            port=DatabaseConfig.MONGO_PORT,
            db_name=DatabaseConfig.MONGO_DB_NAME
        )
        
        if mongo_config.connect():
            initialize_mongo(mongo_config.db)
            print(f"MongoDB database '{DatabaseConfig.MONGO_DB_NAME}' initialized successfully.")
            mongo_config.close()
            return True
        else:
            print("Failed to connect to MongoDB.")
            return False
    
    elif db_type.lower() == 'postgresql':
        try:
            print("Initializing PostgreSQL database...")
            engine = initialize_postgres()
            print(f"PostgreSQL database '{DatabaseConfig.POSTGRES_DB_NAME}' initialized successfully.")
            return True
        except Exception as e:
            print(f"Failed to initialize PostgreSQL database: {e}")
            return False
    
    else:
        print(f"Unsupported database type: {db_type}")
        return False

if __name__ == "__main__":
    init_db()
