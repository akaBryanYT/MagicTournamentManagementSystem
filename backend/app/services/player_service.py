"""
Player service for the Tournament Management System.
"""

from datetime import datetime
from bson.objectid import ObjectId
from app.models.database import DatabaseConfig
from sqlalchemy import text
import json

class PlayerService:
    """Service for player operations."""
    
    def __init__(self):
        """Initialize the player service."""
        self.db_config = DatabaseConfig()
        self.db_config.connect()
        self.db = self.db_config.db
        self.db_type = self.db_config.db_type
    
    def get_all_players(self):
        """Get all players."""
        try:
            if self.db_type == 'mongodb':
                players = list(self.db.players.find({}, {'_id': 1, 'name': 1, 'email': 1, 'active': 1}))
                for player in players:
                    player['id'] = str(player.pop('_id'))
                return players
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT id, name, email, active 
                    FROM players
                """))
                players = []
                for row in result.mappings():
                    players.append({
                        'id': str(row['id']),
                        'name': row['name'],
                        'email': row['email'],
                        'active': row['active']
                    })
                return players
        except Exception as e:
            print(f"Error getting players: {e}")
            return []
    
    def get_player_by_id(self, player_id):
        """Get player by ID."""
        try:
            if self.db_type == 'mongodb':
                player = self.db.players.find_one({'_id': ObjectId(player_id)})
                if player:
                    player['id'] = str(player.pop('_id'))
                    return player
                return None
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT * FROM players WHERE id = :player_id
                """), {'player_id': int(player_id)})
                row = result.mappings().first()
                if row:
                    player = dict(row)
                    player['id'] = str(player['id'])
                    return player
                return None
        except Exception as e:
            print(f"Error getting player: {e}")
            return None
    
    def create_player(self, player_data):
        """Create a new player."""
        try:
            if self.db_type == 'mongodb':
                # Check if player with email already exists
                existing_player = self.db.players.find_one({'email': player_data['email']})
                if existing_player:
                    return None
                
                # Add timestamps
                player_data['created_at'] = datetime.utcnow().isoformat()
                player_data['updated_at'] = datetime.utcnow().isoformat()
                player_data['active'] = True
                player_data['tournaments'] = []
                
                # Insert player
                result = self.db.players.insert_one(player_data)
                return str(result.inserted_id)
            else:
                # PostgreSQL implementation
                # Check if player with email already exists
                try:
                    print("Checking if email already exists...")
                    result = self.db.execute(text("""
                        SELECT id FROM players WHERE email = :email
                    """), {'email': player_data['email']})
                    
                    if result.first():
                        print(f"Player with email {player_data['email']} already exists")
                        return None
                    
                    # Insert player with better error handling
                    print("Attempting to insert new player...")
                    
                    # Create a proper params dict with all possible fields
                    params = {
                        'name': player_data['name'],
                        'email': player_data['email'],
                        'phone': player_data.get('phone') if player_data.get('phone') else None,
                        'dci_number': player_data.get('dci_number') if player_data.get('dci_number') else None
                    }
                    
                    print(f"SQL parameters: {params}")
                    
                    # Simplified query that doesn't specify all fields explicitly
                    result = self.db.execute(text("""
                        INSERT INTO players (name, email, phone, dci_number, active, created_at, updated_at)
                        VALUES (:name, :email, :phone, :dci_number, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        RETURNING id
                    """), params)
                    
                    self.db.commit()
                    player_id = result.scalar()
                    print(f"Player created successfully with ID: {player_id}")
                    return str(player_id)
                except Exception as db_error:
                    print(f"Database operation error: {db_error}")
                    import traceback
                    traceback.print_exc()
                    self.db.rollback()
                    raise  # Re-raise to be caught by outer exception handler
                    
        except Exception as e:
            print(f"Error creating player: {e}")
            import traceback
            traceback.print_exc()
            if self.db_type == 'postgresql':
                try:
                    self.db.rollback()
                except:
                    print("Error during rollback")
            return None
    
    def update_player(self, player_id, player_data):
        """Update player by ID."""
        try:
            if self.db_type == 'mongodb':
                # Remove fields that shouldn't be updated
                if 'created_at' in player_data:
                    del player_data['created_at']
                if 'tournaments' in player_data:
                    del player_data['tournaments']
                
                # Add updated timestamp
                player_data['updated_at'] = datetime.utcnow().isoformat()
                
                # Update player
                result = self.db.players.update_one(
                    {'_id': ObjectId(player_id)},
                    {'$set': player_data}
                )
                return result.modified_count > 0
            else:
                # PostgreSQL implementation
                # Remove fields that shouldn't be updated
                if 'created_at' in player_data:
                    del player_data['created_at']
                if 'tournaments' in player_data:
                    del player_data['tournaments']
                
                # Build update query
                set_clauses = []
                params = {'player_id': int(player_id)}
                
                for key, value in player_data.items():
                    set_clauses.append(f"{key} = :{key}")
                    params[key] = value
                
                set_clause = ", ".join(set_clauses)
                set_clause += ", updated_at = CURRENT_TIMESTAMP"
                
                query = f"""
                    UPDATE players
                    SET {set_clause}
                    WHERE id = :player_id
                """
                
                result = self.db.execute(text(query), params)
                self.db.commit()
                
                return result.rowcount > 0
        except Exception as e:
            print(f"Error updating player: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False
    
    def delete_player(self, player_id):
        """Delete player by ID."""
        try:
            if self.db_type == 'mongodb':
                # Check if player is registered in any active tournaments
                active_tournaments = self.db.tournaments.find_one({
                    'players': player_id,
                    'status': {'$in': ['planned', 'active']}
                })
                
                if active_tournaments:
                    return False
                
                # Delete player
                result = self.db.players.delete_one({'_id': ObjectId(player_id)})
                return result.deleted_count > 0
            else:
                # PostgreSQL implementation
                # Check if player is registered in any active tournaments
                result = self.db.execute(text("""
                    SELECT t.id
                    FROM tournaments t
                    JOIN tournament_players tp ON t.id = tp.tournament_id
                    WHERE tp.player_id = :player_id
                    AND t.status IN ('planned', 'active')
                    LIMIT 1
                """), {'player_id': int(player_id)})
                
                if result.first():
                    return False
                
                # Delete player
                result = self.db.execute(text("""
                    DELETE FROM players
                    WHERE id = :player_id
                """), {'player_id': int(player_id)})
                
                self.db.commit()
                return result.rowcount > 0
        except Exception as e:
            print(f"Error deleting player: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False
    
    def search_players(self, query):
        """Search players by name or email."""
        try:
            if self.db_type == 'mongodb':
                players = list(self.db.players.find({
                    '$or': [
                        {'name': {'$regex': query, '$options': 'i'}},
                        {'email': {'$regex': query, '$options': 'i'}}
                    ]
                }, {'_id': 1, 'name': 1, 'email': 1}))
                
                for player in players:
                    player['id'] = str(player.pop('_id'))
                
                return players
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT id, name, email
                    FROM players
                    WHERE name ILIKE :query OR email ILIKE :query
                """), {'query': f'%{query}%'})
                
                players = []
                for row in result.mappings():
                    players.append({
                        'id': str(row['id']),
                        'name': row['name'],
                        'email': row['email']
                    })
                
                return players
        except Exception as e:
            print(f"Error searching players: {e}")
            return []
    
    def get_player_tournaments(self, player_id):
        """Get tournaments for a player."""
        try:
            if self.db_type == 'mongodb':
                player = self.db.players.find_one({'_id': ObjectId(player_id)})
                if not player or 'tournaments' not in player:
                    return []
                
                tournament_ids = [ObjectId(t_id) for t_id in player['tournaments']]
                tournaments = list(self.db.tournaments.find({
                    '_id': {'$in': tournament_ids}
                }, {'_id': 1, 'name': 1, 'format': 1, 'date': 1, 'status': 1}))
                
                for tournament in tournaments:
                    tournament['id'] = str(tournament.pop('_id'))
                
                return tournaments
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT t.id, t.name, t.format, t.date, t.status
                    FROM tournaments t
                    JOIN tournament_players tp ON t.id = tp.tournament_id
                    WHERE tp.player_id = :player_id
                """), {'player_id': int(player_id)})
                
                tournaments = []
                for row in result.mappings():
                    tournament = dict(row)
                    tournament['id'] = str(tournament['id'])
                    tournament['date'] = tournament['date'].isoformat() if tournament['date'] else None
                    tournaments.append(tournament)
                
                return tournaments
        except Exception as e:
            print(f"Error getting player tournaments: {e}")
            return []
    
    def get_player_decks(self, player_id):
        """Get decks for a player."""
        try:
            if self.db_type == 'mongodb':
                decks = list(self.db.decks.find({
                    'player_id': player_id
                }, {'_id': 1, 'name': 1, 'format': 1, 'tournament_id': 1}))
                
                for deck in decks:
                    deck['id'] = str(deck.pop('_id'))
                
                return decks
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT d.id, d.name, d.format, d.tournament_id
                    FROM decks d
                    WHERE d.player_id = :player_id
                """), {'player_id': int(player_id)})
                
                decks = []
                for row in result.mappings():
                    deck = dict(row)
                    deck['id'] = str(deck['id'])
                    deck['tournament_id'] = str(deck['tournament_id'])
                    decks.append(deck)
                
                return decks
        except Exception as e:
            print(f"Error getting player decks: {e}")
            return []