"""
Match service for the Tournament Management System.
"""

from datetime import datetime
from bson.objectid import ObjectId
from app.models.database import DatabaseConfig

class MatchService:
    """Service for match operations."""
    
    def __init__(self):
        """Initialize the match service."""
        self.db_config = DatabaseConfig()
        self.db_config.connect()
        self.db = self.db_config.db
    
    def get_all_matches(self):
        """Get all matches."""
        matches = list(self.db.matches.find({}, {
            '_id': 1, 
            'tournament_id': 1, 
            'round': 1, 
            'table_number': 1,
            'player1_id': 1,
            'player2_id': 1,
            'status': 1,
            'result': 1
        }))
        
        for match in matches:
            match['id'] = str(match.pop('_id'))
        
        return matches
    
    def get_matches_by_tournament(self, tournament_id):
        """Get matches for a tournament."""
        matches = list(self.db.matches.find({'tournament_id': tournament_id}, {
            '_id': 1, 
            'round': 1, 
            'table_number': 1,
            'player1_id': 1,
            'player2_id': 1,
            'status': 1,
            'result': 1
        }))
        
        for match in matches:
            match['id'] = str(match.pop('_id'))
        
        return matches
    
    def get_matches_by_tournament_and_round(self, tournament_id, round_number):
        """Get matches for a tournament and round."""
        matches = list(self.db.matches.find({
            'tournament_id': tournament_id,
            'round': int(round_number)
        }))
        
        for match in matches:
            match['id'] = str(match.pop('_id'))
        
        return matches
    
    def get_match_by_id(self, match_id):
        """Get match by ID."""
        try:
            match = self.db.matches.find_one({'_id': ObjectId(match_id)})
            if match:
                match['id'] = str(match.pop('_id'))
                return match
            return None
        except Exception as e:
            print(f"Error getting match: {e}")
            return None
    
    def create_match(self, match_data):
        """Create a new match."""
        try:
            # Validate tournament exists
            tournament = self.db.tournaments.find_one({'_id': ObjectId(match_data['tournament_id'])})
            if not tournament:
                return None
            
            # Validate players exist
            player1 = self.db.players.find_one({'_id': ObjectId(match_data['player1_id'])})
            if not player1:
                return None
            
            if 'player2_id' in match_data and match_data['player2_id']:
                player2 = self.db.players.find_one({'_id': ObjectId(match_data['player2_id'])})
                if not player2:
                    return None
            
            # Set default values
            if 'status' not in match_data:
                match_data['status'] = 'pending'
            
            if 'player1_wins' not in match_data:
                match_data['player1_wins'] = 0
            
            if 'player2_wins' not in match_data:
                match_data['player2_wins'] = 0
            
            if 'draws' not in match_data:
                match_data['draws'] = 0
            
            # Insert match
            result = self.db.matches.insert_one(match_data)
            
            # Update tournament
            self.db.tournaments.update_one(
                {'_id': ObjectId(match_data['tournament_id'])},
                {'$push': {'matches': str(result.inserted_id)}}
            )
            
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating match: {e}")
            return None
    
    def update_match(self, match_id, match_data):
        """Update match by ID."""
        try:
            # Get current match
            current_match = self.db.matches.find_one({'_id': ObjectId(match_id)})
            if not current_match:
                return False
            
            # Don't allow updating completed matches
            if current_match['status'] == 'completed' and match_data.get('status') != 'completed':
                return False
            
            # Update match
            result = self.db.matches.update_one(
                {'_id': ObjectId(match_id)},
                {'$set': match_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating match: {e}")
            return False
    
    def submit_match_result(self, match_id, player1_wins, player2_wins, draws):
        """Submit result for a match."""
        try:
            # Get match
            match = self.db.matches.find_one({'_id': ObjectId(match_id)})
            if not match or match['status'] == 'completed':
                return False
            
            # Validate result
            if player1_wins < 0 or player2_wins < 0 or draws < 0:
                return False
            
            # Determine result
            if player1_wins > player2_wins:
                result = 'win'
                match_points_player1 = 3  # Win = 3 points
                match_points_player2 = 0
            elif player2_wins > player1_wins:
                result = 'loss'
                match_points_player1 = 0
                match_points_player2 = 3
            else:
                result = 'draw'
                match_points_player1 = 1  # Draw = 1 point
                match_points_player2 = 1
            
            # Update match
            self.db.matches.update_one(
                {'_id': ObjectId(match_id)},
                {'$set': {
                    'player1_wins': player1_wins,
                    'player2_wins': player2_wins,
                    'draws': draws,
                    'result': result,
                    'status': 'completed',
                    'end_time': datetime.utcnow().isoformat()
                }}
            )
            
            # Update standings for player 1
            self.db.standings.update_one(
                {'tournament_id': match['tournament_id'], 'player_id': match['player1_id']},
                {'$inc': {
                    'matches_played': 1,
                    'match_points': match_points_player1,
                    'game_points': player1_wins
                }}
            )
            
            # Update standings for player 2 (if not a bye)
            if match.get('player2_id'):
                self.db.standings.update_one(
                    {'tournament_id': match['tournament_id'], 'player_id': match['player2_id']},
                    {'$inc': {
                        'matches_played': 1,
                        'match_points': match_points_player2,
                        'game_points': player2_wins
                    }}
                )
            
            # Update win percentages for all players in the tournament
            self._update_win_percentages(match['tournament_id'])
            
            return True
        except Exception as e:
            print(f"Error submitting match result: {e}")
            return False
    
    def start_match(self, match_id):
        """Start a match."""
        try:
            # Get match
            match = self.db.matches.find_one({'_id': ObjectId(match_id)})
            if not match or match['status'] != 'pending':
                return False
            
            # Update match
            self.db.matches.update_one(
                {'_id': ObjectId(match_id)},
                {'$set': {
                    'status': 'in_progress',
                    'start_time': datetime.utcnow().isoformat()
                }}
            )
            
            return True
        except Exception as e:
            print(f"Error starting match: {e}")
            return False
    
    def end_match(self, match_id):
        """End a match without submitting result."""
        try:
            # Get match
            match = self.db.matches.find_one({'_id': ObjectId(match_id)})
            if not match or match['status'] == 'completed':
                return False
            
            # Update match
            self.db.matches.update_one(
                {'_id': ObjectId(match_id)},
                {'$set': {
                    'status': 'completed',
                    'end_time': datetime.utcnow().isoformat()
                }}
            )
            
            return True
        except Exception as e:
            print(f"Error ending match: {e}")
            return False
    
    def draw_match(self, match_id):
        """Mark a match as intentional draw."""
        try:
            # Get match
            match = self.db.matches.find_one({'_id': ObjectId(match_id)})
            if not match or match['status'] == 'completed' or not match.get('player2_id'):
                return False
            
            # Update match
            self.db.matches.update_one(
                {'_id': ObjectId(match_id)},
                {'$set': {
                    'player1_wins': 0,
                    'player2_wins': 0,
                    'draws': 1,
                    'result': 'draw',
                    'status': 'completed',
                    'end_time': datetime.utcnow().isoformat()
                }}
            )
            
            # Update standings for both players
            for player_id in [match['player1_id'], match['player2_id']]:
                self.db.standings.update_one(
                    {'tournament_id': match['tournament_id'], 'player_id': player_id},
                    {'$inc': {
                        'matches_played': 1,
                        'match_points': 1,  # Draw = 1 point
                        'game_points': 0
                    }}
                )
            
            # Update win percentages for all players in the tournament
            self._update_win_percentages(match['tournament_id'])
            
            return True
        except Exception as e:
            print(f"Error marking match as draw: {e}")
            return False
    
    def _update_win_percentages(self, tournament_id):
        """Update win percentages for all players in a tournament."""
        try:
            # Get all players in the tournament
            standings = list(self.db.standings.find({'tournament_id': tournament_id}))
            
            # Calculate match win percentage for each player
            for standing in standings:
                player_id = standing['player_id']
                matches_played = standing['matches_played']
                
                if matches_played > 0:
                    match_win_percentage = standing['match_points'] / (matches_played * 3)
                    game_win_percentage = 0
                    
                    # Calculate game win percentage
                    matches = list(self.db.matches.find({
                        'tournament_id': tournament_id,
                        '$or': [
                            {'player1_id': player_id},
                            {'player2_id': player_id}
                        ],
                        'status': 'completed'
                    }))
                    
                    total_games = 0
                    games_won = 0
                    
                    for match in matches:
                        if match['player1_id'] == player_id:
                            games_won += match['player1_wins']
                            total_games += match['player1_wins'] + match['player2_wins'] + match['draws']
                        else:
                            games_won += match['player2_wins']
                            total_games += match['player1_wins'] + match['player2_wins'] + match['draws']
                    
                    if total_games > 0:
                        game_win_percentage = games_won / total_games
                    
                    # Update standing
                    self.db.standings.update_one(
                        {'_id': standing['_id']},
                        {'$set': {
                            'match_win_percentage': match_win_percentage,
                            'game_win_percentage': game_win_percentage
                        }}
                    )
            
            # Calculate opponents' win percentages
            for standing in standings:
                player_id = standing['player_id']
                
                # Get all opponents
                matches = list(self.db.matches.find({
                    'tournament_id': tournament_id,
                    '$or': [
                        {'player1_id': player_id},
                        {'player2_id': player_id}
                    ],
                    'status': 'completed'
                }))
                
                opponent_ids = []
                for match in matches:
                    if match['player1_id'] == player_id and match.get('player2_id'):
                        opponent_ids.append(match['player2_id'])
                    elif match['player2_id'] == player_id:
                        opponent_ids.append(match['player1_id'])
                
                # Get opponents' standings
                opponent_standings = list(self.db.standings.find({
                    'tournament_id': tournament_id,
                    'player_id': {'$in': opponent_ids}
                }))
                
                # Calculate opponents' match win percentage
                if opponent_standings:
                    omw = sum(s['match_win_percentage'] for s in opponent_standings) / len(opponent_standings)
                    ogw = sum(s['game_win_percentage'] for s in opponent_standings) / len(opponent_standings)
                    
                    # Update standing
                    self.db.standings.update_one(
                        {'_id': standing['_id']},
                        {'$set': {
                            'opponents_match_win_percentage': omw,
                            'opponents_game_win_percentage': ogw
                        }}
                    )
            
            return True
        except Exception as e:
            print(f"Error updating win percentages: {e}")
            return False
