import pytest
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.database import DatabaseConfig

@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app('testing')
    
    # Establish application context
    with app.app_context():
        # Initialize test database
        db_config = DatabaseConfig()
        db_config.connect()
        
        # Clear test collections/tables
        db_config.db.players.delete_many({})
        db_config.db.tournaments.delete_many({})
        db_config.db.matches.delete_many({})
        db_config.db.decks.delete_many({})
        db_config.db.cards.delete_many({})
        
        yield app
        
        # Clean up after tests
        db_config.db.players.delete_many({})
        db_config.db.tournaments.delete_many({})
        db_config.db.matches.delete_many({})
        db_config.db.decks.delete_many({})
        db_config.db.cards.delete_many({})

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()
