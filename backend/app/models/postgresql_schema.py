"""
PostgreSQL schema for the Tournament Management System.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Table, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

Base = declarative_base()

# Association tables for many-to-many relationships
tournament_players = Table(
    'tournament_players',
    Base.metadata,
    Column('tournament_id', Integer, ForeignKey('tournaments.id')),
    Column('player_id', Integer, ForeignKey('players.id'))
)

# Models
class Player(Base):
    """Player model for PostgreSQL."""
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(20))
    dci_number = Column(String(50), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    active = Column(Boolean, default=True)
    
    # Relationships
    tournaments = relationship("Tournament", secondary=tournament_players, back_populates="players")
    decks = relationship("Deck", back_populates="player")
    standings = relationship("Standing", back_populates="player")

class Tournament(Base):
    """Tournament model for PostgreSQL."""
    __tablename__ = 'tournaments'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    format = Column(String(50), nullable=False)
    structure = Column(String(50), default='swiss')
    date = Column(DateTime, nullable=False)
    location = Column(String(100))
    status = Column(String(20), default='planned')
    rounds = Column(Integer, default=0)
    current_round = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tiebreakers = Column(JSON)
    time_limits = Column(JSON)
    format_config = Column(JSON)
    structure_config = Column(JSON)
    
    # Relationships
    players = relationship("Player", secondary=tournament_players, back_populates="tournaments")
    matches = relationship("Match", back_populates="tournament")
    decks = relationship("Deck", back_populates="tournament")
    standings = relationship("Standing", back_populates="tournament")

class Match(Base):
    """Match model for PostgreSQL."""
    __tablename__ = 'matches'
    
    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'), nullable=False)
    round = Column(Integer, nullable=False)
    table_number = Column(Integer)
    player1_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    player2_id = Column(Integer, ForeignKey('players.id'))
    player1_wins = Column(Integer, default=0)
    player2_wins = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    result = Column(String(20))
    status = Column(String(20), default='pending')
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    notes = Column(Text)
    bracket = Column(String(20))
    bracket_position = Column(Integer)
    winners_next_match = Column(Integer)
    losers_next_match = Column(Integer)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="matches")
    player1 = relationship("Player", foreign_keys=[player1_id])
    player2 = relationship("Player", foreign_keys=[player2_id])

class Deck(Base):
    """Deck model for PostgreSQL."""
    __tablename__ = 'decks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'), nullable=False)
    format = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    validation_status = Column(String(20), default='pending')
    validation_errors = Column(JSON)
    
    # Relationships
    player = relationship("Player", back_populates="decks")
    tournament = relationship("Tournament", back_populates="decks")
    cards = relationship("DeckCard", back_populates="deck")

class Card(Base):
    """Card model for PostgreSQL."""
    __tablename__ = 'cards'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    set_code = Column(String(10))
    collector_number = Column(String(10))
    mana_cost = Column(String(50))
    type_line = Column(String(100))
    oracle_text = Column(Text)
    colors = Column(JSON)
    color_identity = Column(JSON)
    legalities = Column(JSON)
    rarity = Column(String(20))
    image_uri = Column(String(255))
    
    # Relationships
    deck_cards = relationship("DeckCard", back_populates="card")

class DeckCard(Base):
    """DeckCard model for PostgreSQL (junction table with additional data)."""
    __tablename__ = 'deck_cards'
    
    id = Column(Integer, primary_key=True)
    deck_id = Column(Integer, ForeignKey('decks.id'), nullable=False)
    card_id = Column(Integer, ForeignKey('cards.id'), nullable=False)
    quantity = Column(Integer, default=1)
    is_sideboard = Column(Boolean, default=False)
    
    # Relationships
    deck = relationship("Deck", back_populates="cards")
    card = relationship("Card", back_populates="deck_cards")

class Standing(Base):
    """Standing model for PostgreSQL."""
    __tablename__ = 'standings'
    
    id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey('tournaments.id'), nullable=False)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False)
    matches_played = Column(Integer, default=0)
    match_points = Column(Integer, default=0)
    game_points = Column(Integer, default=0)
    match_win_percentage = Column(Float, default=0.0)
    game_win_percentage = Column(Float, default=0.0)
    opponents_match_win_percentage = Column(Float, default=0.0)
    opponents_game_win_percentage = Column(Float, default=0.0)
    rank = Column(Integer)
    active = Column(Boolean, default=True)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="standings")
    player = relationship("Player", back_populates="standings")

def get_postgresql_uri():
    """Get PostgreSQL URI from environment variables."""
    load_dotenv()
    pg_host = os.getenv('POSTGRES_HOST', 'localhost')
    pg_port = os.getenv('POSTGRES_PORT', '5432')
    pg_db = os.getenv('POSTGRES_DB_NAME', 'tournament_management')
    pg_user = os.getenv('POSTGRES_USERNAME', 'postgres')
    pg_password = os.getenv('POSTGRES_PASSWORD', 'postgres')
    
    return f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}"

def initialize_database():
    """Initialize PostgreSQL database with tables."""
    engine = create_engine(get_postgresql_uri())
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    """Get a database session."""
    Session = sessionmaker(bind=engine)
    return Session()