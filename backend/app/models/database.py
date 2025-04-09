"""
Database schema for the Tournament Management System.
This module defines the MongoDB schema for the TMS application.
"""

from pymongo import MongoClient
from bson.objectid import ObjectId
import os
import json

# Database configuration
class DatabaseConfig:
    """Database configuration for MongoDB."""
    def __init__(self, host='localhost', port=27017, db_name='tournament_management'):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.client = None
        self.db = None

    def connect(self):
        """Connect to MongoDB database."""
        try:
            self.client = MongoClient(f'mongodb://{self.host}:{self.port}/')
            self.db = self.client[self.db_name]
            return True
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            return False

    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()

# Database schema models
class Player:
    """Player model for MongoDB."""
    collection_name = 'players'
    
    schema = {
        'name': str,  # Player's full name
        'email': str,  # Contact email
        'phone': str,  # Contact phone number
        'dci_number': str,  # DCI number (optional)
        'created_at': str,  # Creation timestamp
        'updated_at': str,  # Last update timestamp
        'tournaments': list,  # List of tournament IDs player has participated in
        'active': bool,  # Whether player is active
    }
    
    @staticmethod
    def create_indexes(db):
        """Create indexes for players collection."""
        db[Player.collection_name].create_index('email', unique=True)
        db[Player.collection_name].create_index('dci_number', sparse=True)

class Tournament:
    """Tournament model for MongoDB."""
    collection_name = 'tournaments'
    
    schema = {
        'name': str,  # Tournament name
        'format': str,  # Tournament format (Swiss, Draft, Commander, etc.)
        'date': str,  # Tournament date
        'location': str,  # Tournament location
        'status': str,  # Tournament status (planned, active, completed)
        'rounds': int,  # Number of rounds
        'current_round': int,  # Current round number
        'players': list,  # List of player IDs
        'matches': list,  # List of match IDs
        'created_at': str,  # Creation timestamp
        'updated_at': str,  # Last update timestamp
        'tiebreakers': dict,  # Tiebreaker configuration
        'time_limits': dict,  # Time limits for rounds
        'format_config': dict,  # Format-specific configuration
    }
    
    @staticmethod
    def create_indexes(db):
        """Create indexes for tournaments collection."""
        db[Tournament.collection_name].create_index([('name', 1), ('date', 1)], unique=True)

class Match:
    """Match model for MongoDB."""
    collection_name = 'matches'
    
    schema = {
        'tournament_id': str,  # Tournament ID
        'round': int,  # Round number
        'table_number': int,  # Table number
        'player1_id': str,  # Player 1 ID
        'player2_id': str,  # Player 2 ID (None for bye)
        'player1_wins': int,  # Player 1 wins
        'player2_wins': int,  # Player 2 wins
        'draws': int,  # Number of draws
        'result': str,  # Match result (win, loss, draw, bye)
        'status': str,  # Match status (pending, in_progress, completed)
        'start_time': str,  # Match start time
        'end_time': str,  # Match end time
        'notes': str,  # Match notes
    }
    
    @staticmethod
    def create_indexes(db):
        """Create indexes for matches collection."""
        db[Match.collection_name].create_index([('tournament_id', 1), ('round', 1), ('table_number', 1)], unique=True)
        db[Match.collection_name].create_index([('tournament_id', 1), ('round', 1), ('player1_id', 1)], unique=True)
        db[Match.collection_name].create_index([('tournament_id', 1), ('round', 1), ('player2_id', 1)], unique=True, sparse=True)

class Deck:
    """Deck model for MongoDB."""
    collection_name = 'decks'
    
    schema = {
        'name': str,  # Deck name
        'player_id': str,  # Player ID
        'tournament_id': str,  # Tournament ID
        'format': str,  # Deck format (Standard, Modern, Commander, etc.)
        'main_deck': list,  # List of cards in main deck
        'sideboard': list,  # List of cards in sideboard
        'created_at': str,  # Creation timestamp
        'updated_at': str,  # Last update timestamp
        'validation_status': str,  # Validation status (valid, invalid)
        'validation_errors': list,  # List of validation errors
    }
    
    @staticmethod
    def create_indexes(db):
        """Create indexes for decks collection."""
        db[Deck.collection_name].create_index([('player_id', 1), ('tournament_id', 1)], unique=True)

class Card:
    """Card model for MongoDB."""
    collection_name = 'cards'
    
    schema = {
        'name': str,  # Card name
        'set_code': str,  # Set code
        'collector_number': str,  # Collector number
        'mana_cost': str,  # Mana cost
        'type_line': str,  # Type line
        'oracle_text': str,  # Oracle text
        'colors': list,  # List of colors
        'color_identity': list,  # List of color identities
        'legalities': dict,  # Format legalities
    }
    
    @staticmethod
    def create_indexes(db):
        """Create indexes for cards collection."""
        db[Card.collection_name].create_index([('name', 1)], unique=True)
        db[Card.collection_name].create_index([('set_code', 1), ('collector_number', 1)], unique=True)

class Standing:
    """Standing model for MongoDB."""
    collection_name = 'standings'
    
    schema = {
        'tournament_id': str,  # Tournament ID
        'player_id': str,  # Player ID
        'matches_played': int,  # Number of matches played
        'match_points': int,  # Match points
        'game_points': int,  # Game points
        'match_win_percentage': float,  # Match win percentage
        'game_win_percentage': float,  # Game win percentage
        'opponents_match_win_percentage': float,  # Opponents' match win percentage
        'opponents_game_win_percentage': float,  # Opponents' game win percentage
        'rank': int,  # Current rank
        'active': bool,  # Whether player is active (not dropped)
    }
    
    @staticmethod
    def create_indexes(db):
        """Create indexes for standings collection."""
        db[Standing.collection_name].create_index([('tournament_id', 1), ('player_id', 1)], unique=True)
        db[Standing.collection_name].create_index([('tournament_id', 1), ('rank', 1)])

def initialize_database(db):
    """Initialize database with collections and indexes."""
    # Create collections
    collections = [
        Player.collection_name,
        Tournament.collection_name,
        Match.collection_name,
        Deck.collection_name,
        Card.collection_name,
        Standing.collection_name
    ]
    
    for collection in collections:
        if collection not in db.list_collection_names():
            db.create_collection(collection)
    
    # Create indexes
    Player.create_indexes(db)
    Tournament.create_indexes(db)
    Match.create_indexes(db)
    Deck.create_indexes(db)
    Card.create_indexes(db)
    Standing.create_indexes(db)
    
    return True
