import os
import sys

# Add the parent directory (backend/) to Python path so app module can be found
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from app.models.database import DatabaseConfig
from sqlalchemy import text

def add_structure_column():
    """Add the structure column to the tournaments table if it doesn't exist."""
    db_config = DatabaseConfig()
    db_config.connect()
    
    if db_config.db_type == 'postgresql':
        try:
            # Check if column exists
            result = db_config.db.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'tournaments' AND column_name = 'structure'
            """))
            
            if not result.first():
                print("Adding 'structure' column to tournaments table...")
                db_config.db.execute(text("""
                    ALTER TABLE tournaments 
                    ADD COLUMN structure VARCHAR(50) DEFAULT 'swiss'
                """))
                db_config.db.commit()
                print("Column added successfully.")
            else:
                print("Column 'structure' already exists.")
                
        except Exception as e:
            print(f"Error adding column: {e}")
            db_config.db.rollback()
        finally:
            db_config.db.close()
    else:
        print("This script is for PostgreSQL only.")

if __name__ == "__main__":
    add_structure_column()