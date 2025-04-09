"""
Player service for the Tournament Management System.
"""

from datetime import datetime
from bson.objectid import ObjectId
from app.models.database import DatabaseConfig

class PlayerService:
    """Service for player operations."""
    
    def __init__(self):
        """Initialize the player service."""
        self.db_config = DatabaseConfig()
        self.db_config.connect()
        self.db = self.db_config.db
    
    def get_all_players(self):
        """Get all players."""
        players = list(self.db.players.find({}, {'_id': 1, 'name': 1, 'email': 1, 'active': 1}))
        for player in players:
            player['id'] = str(player.pop('_id'))
        return players
    
    def get_player_by_id(self, player_id):
        """Get player by ID."""
        try:
            player = self.db.players.find_one({'_id': ObjectId(player_id)})
            if player:
                player['id'] = str(player.pop('_id'))
                return player
            return None
        except Exception:
            return None
    
    def create_player(self, player_data):
        """Create a new player."""
        try:
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
        except Exception as e:
            print(f"Error creating player: {e}")
            return None
    
    def update_player(self, player_id, player_data):
        """Update player by ID."""
        try:
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
        except Exception as e:
            print(f"Error updating player: {e}")
            return False
    
    def delete_player(self, player_id):
        """Delete player by ID."""
        try:
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
        except Exception as e:
            print(f"Error deleting player: {e}")
            return False
    
    def search_players(self, query):
        """Search players by name or email."""
        try:
            players = list(self.db.players.find({
                '$or': [
                    {'name': {'$regex': query, '$options': 'i'}},
                    {'email': {'$regex': query, '$options': 'i'}}
                ]
            }, {'_id': 1, 'name': 1, 'email': 1}))
            
            for player in players:
                player['id'] = str(player.pop('_id'))
            
            return players
        except Exception as e:
            print(f"Error searching players: {e}")
            return []
    
    def get_player_tournaments(self, player_id):
        """Get tournaments for a player."""
        try:
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
        except Exception as e:
            print(f"Error getting player tournaments: {e}")
            return []
    
    def get_player_decks(self, player_id):
        """Get decks for a player."""
        try:
            decks = list(self.db.decks.find({
                'player_id': player_id
            }, {'_id': 1, 'name': 1, 'format': 1, 'tournament_id': 1}))
            
            for deck in decks:
                deck['id'] = str(deck.pop('_id'))
            
            return decks
        except Exception as e:
            print(f"Error getting player decks: {e}")
            return []
