"""
Database schema for the Tournament Management System.
"""

from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

class DatabaseConfig:
    """Database configuration for MongoDB or PostgreSQL."""
    def __init__(self):
        """Initialize the database configuration."""
        # Load environment variables
        load_dotenv()
        
        self.db_type = os.getenv('DB_TYPE', 'mongodb').lower()
        self.client = None
        self.db = None
        self.engine = None
        self.session = None

    def connect(self):
        """Connect to the configured database."""
        try:
            if self.db_type == 'mongodb':
                # MongoDB connection
                mongo_uri = os.getenv('MONGO_URI')
                if not mongo_uri:
                    # Build MongoDB URI from individual settings
                    mongo_host = os.getenv('MONGO_HOST', 'localhost')
                    mongo_port = os.getenv('MONGO_PORT', '27017')
                    mongo_db = os.getenv('MONGO_DB_NAME', 'tournament_management')
                    mongo_user = os.getenv('MONGO_USERNAME', '')
                    mongo_password = os.getenv('MONGO_PASSWORD', '')
                    
                    if mongo_user and mongo_password:
                        mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/{mongo_db}"
                    else:
                        mongo_uri = f"mongodb://{mongo_host}:{mongo_port}/{mongo_db}"
                
                self.client = MongoClient(mongo_uri)
                self.db = self.client[os.getenv('MONGO_DB_NAME', 'tournament_management')]
                # Test connection
                self.client.admin.command('ping')
                print(f"Connected to MongoDB: {mongo_uri}")
                return True
            
            elif self.db_type == 'postgresql':
                # PostgreSQL connection
                pg_uri = os.getenv('POSTGRES_URI')
                if not pg_uri:
                    # Build PostgreSQL URI from individual settings
                    pg_host = os.getenv('POSTGRES_HOST', 'localhost')
                    pg_port = os.getenv('POSTGRES_PORT', '5432')
                    pg_db = os.getenv('POSTGRES_DB_NAME', 'tournament_management')
                    pg_user = os.getenv('POSTGRES_USERNAME', 'postgres')
                    pg_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
                    
                    pg_uri = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"
                
                self.engine = create_engine(pg_uri)
                Session = sessionmaker(bind=self.engine)
                self.session = Session()
                self.db = self.session
                
                # Test connection
                self.engine.connect()
                print(f"Connected to PostgreSQL: {pg_uri}")
                return True
            
            else:
                raise ValueError(f"Unsupported database type: {self.db_type}")
                
        except Exception as e:
            print(f"Error connecting to database: {e}")
            if self.db_type == 'mongodb':
                print("Make sure MongoDB is installed and running on localhost:27017")
                print("You can also change DB_TYPE to 'postgresql' in .env file to use PostgreSQL")
            else:
                print("Make sure PostgreSQL is installed and running")
                print("Check your PostgreSQL credentials in .env file")
            return False

    def close(self):
        """Close database connection."""
        if self.db_type == 'mongodb' and self.client:
            self.client.close()
        elif self.db_type == 'postgresql' and self.session:
            self.session.close()
            
    def initialize_database(db):
        """Initialize MongoDB collections and indexes."""
        try:
            # Create collections if they don't exist
            if "players" not in db.list_collection_names():
                db.create_collection("players")
            
            if "tournaments" not in db.list_collection_names():
                db.create_collection("tournaments")
            
            if "matches" not in db.list_collection_names():
                db.create_collection("matches")
                
            if "decks" not in db.list_collection_names():
                db.create_collection("decks")
                
            if "cards" not in db.list_collection_names():
                db.create_collection("cards")
                
            if "standings" not in db.list_collection_names():
                db.create_collection("standings")
                
            # Create indexes
            db.players.create_index("email", unique=True)
            db.players.create_index("name")
            
            db.tournaments.create_index("name")
            db.tournaments.create_index("status")
            
            db.matches.create_index("tournament_id")
            db.matches.create_index([("tournament_id", 1), ("round", 1)])
            
            db.decks.create_index([("player_id", 1), ("tournament_id", 1)])
            db.decks.create_index("tournament_id")
            
            db.cards.create_index("name", unique=True)
            db.cards.create_index("set_code")
            
            db.standings.create_index([("tournament_id", 1), ("player_id", 1)], unique=True)
            
            print("MongoDB collections and indexes created successfully")
            return True
        except Exception as e:
            print(f"Error initializing MongoDB: {e}")
            return False