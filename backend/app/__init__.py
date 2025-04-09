"""
Flask application initialization for the Tournament Management System.
"""

from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

def create_app(test_config=None):
    """Create and configure the Flask application."""
    # Load environment variables
    load_dotenv()
    
    # Create Flask app
    app = Flask(__name__, instance_relative_config=True)
    
    # Enable CORS
    CORS(app)
    
    # Load configuration
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.getenv('SECRET_KEY', 'dev'),
            DB_TYPE=os.getenv('DB_TYPE', 'mongodb'),
            MONGO_URI=os.getenv('MONGO_URI', 'mongodb://localhost:27017/tms_db'),
            POSTGRES_URI=os.getenv('POSTGRES_URI', 'postgresql://postgres:postgres@localhost:5432/tms_db'),
        )
    else:
        app.config.from_mapping(test_config)
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Register blueprints
    from app.routes import players, tournaments, matches, decks, cards
    
    app.register_blueprint(players.bp)
    app.register_blueprint(tournaments.bp)
    app.register_blueprint(matches.bp)
    app.register_blueprint(decks.bp)
    app.register_blueprint(cards.bp)
    
    # Simple index route
    @app.route('/')
    def index():
        return {
            'message': 'Tournament Management System API',
            'version': '1.0.0',
            'status': 'running'
        }
    
    return app
