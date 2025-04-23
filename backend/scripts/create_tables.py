from app.models.database import DatabaseConfig
from app.models.database import initialize_database as initialize_mongo
from app.models.postgresql_schema import initialize_database as initialize_postgresql
import os

def main():
    """Initialize database tables."""
    db_config = DatabaseConfig()
    db_type = os.getenv('DB_TYPE', 'mongodb').lower()
    
    if db_type == 'mongodb':
        # Connect to MongoDB
        success = db_config.connect()
        if not success:
            print("Failed to connect to MongoDB")
            return
        
        # Initialize collections and indexes
        success = initialize_mongo(db_config.db)
        if success:
            print("MongoDB collections and indexes created successfully")
        else:
            print("Failed to initialize MongoDB collections")
    
    elif db_type == 'postgresql':
        # Initialize PostgreSQL tables
        engine = initialize_postgresql()
        if engine:
            print("PostgreSQL tables created successfully")
        else:
            print("Failed to initialize PostgreSQL tables")
    
    else:
        print(f"Unsupported database type: {db_type}")

if __name__ == '__main__':
    main()