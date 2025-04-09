"""
Tournament service for the Tournament Management System.
"""

from datetime import datetime
from bson.objectid import ObjectId
from app.models.database import DatabaseConfig
from app.services.swiss_pairing import SwissPairingService

class TournamentService:
    """Service for tournament operations."""
    
    def __init__(self):
        """Initialize the tournament service."""
        self.db_config = DatabaseConfig()
        self.db_config.connect()
        self.db = self.db_config.db
        self.swiss_pairing = SwissPairingService()
    
    def get_all_tournaments(self):
        """Get all tournaments."""
        tournaments = list(self.db.tournaments.find({}, {
            '_id': 1, 
            'name': 1, 
            'format': 1, 
            'date': 1, 
            'status': 1,
            'rounds': 1,
            'current_round': 1
        }))
        
        for tournament in tournaments:
            tournament['id'] = str(tournament.pop('_id'))
        
        return tournaments
    
    def get_tournament_by_id(self, tournament_id):
        """Get tournament by ID."""
        try:
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if tournament:
                tournament['id'] = str(tournament.pop('_id'))
                # Convert player IDs to strings
                if 'players' in tournament:
                    tournament['players'] = [str(p) for p in tournament['players']]
                # Convert match IDs to strings
                if 'matches' in tournament:
                    tournament['matches'] = [str(m) for m in tournament['matches']]
                return tournament
            return None
        except Exception as e:
            print(f"Error getting tournament: {e}")
            return None
    
    def create_tournament(self, tournament_data):
        """Create a new tournament."""
        try:
            # Add timestamps
            tournament_data['created_at'] = datetime.utcnow().isoformat()
            tournament_data['updated_at'] = datetime.utcnow().isoformat()
            tournament_data['status'] = 'planned'
            tournament_data['current_round'] = 0
            tournament_data['players'] = []
            tournament_data['matches'] = []
            
            # Set default rounds based on format
            if 'rounds' not in tournament_data:
                tournament_data['rounds'] = 0  # Will be calculated based on player count
            
            # Set default tiebreakers
            if 'tiebreakers' not in tournament_data:
                tournament_data['tiebreakers'] = {
                    'match_points': 1,
                    'opponents_match_win_percentage': 2,
                    'game_win_percentage': 3,
                    'opponents_game_win_percentage': 4
                }
            
            # Set default time limits
            if 'time_limits' not in tournament_data:
                tournament_data['time_limits'] = {
                    'round_time_minutes': 50,
                    'extra_time_minutes': 10
                }
            
            # Set format-specific configuration
            if 'format_config' not in tournament_data:
                format_name = tournament_data.get('format', '').lower()
                if format_name == 'swiss':
                    tournament_data['format_config'] = {
                        'allow_intentional_draws': True,
                        'allow_byes': True
                    }
                elif format_name == 'draft':
                    tournament_data['format_config'] = {
                        'pod_size': 8,
                        'packs_per_player': 3
                    }
                elif format_name == 'commander':
                    tournament_data['format_config'] = {
                        'pod_size': 4,
                        'point_system': 'standard'
                    }
            
            # Insert tournament
            result = self.db.tournaments.insert_one(tournament_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating tournament: {e}")
            return None
    
    def update_tournament(self, tournament_id, tournament_data):
        """Update tournament by ID."""
        try:
            # Get current tournament
            current_tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not current_tournament:
                return False
            
            # Don't allow updating active tournaments
            if current_tournament['status'] == 'active' and 'status' in tournament_data:
                if tournament_data['status'] != 'active' and tournament_data['status'] != 'completed':
                    return False
            
            # Remove fields that shouldn't be updated
            protected_fields = ['created_at', 'players', 'matches']
            for field in protected_fields:
                if field in tournament_data:
                    del tournament_data[field]
            
            # Add updated timestamp
            tournament_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Update tournament
            result = self.db.tournaments.update_one(
                {'_id': ObjectId(tournament_id)},
                {'$set': tournament_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating tournament: {e}")
            return False
    
    def delete_tournament(self, tournament_id):
        """Delete tournament by ID."""
        try:
            # Check if tournament is active
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if tournament and tournament['status'] == 'active':
                return False
            
            # Delete tournament
            result = self.db.tournaments.delete_one({'_id': ObjectId(tournament_id)})
            
            # Delete related matches
            self.db.matches.delete_many({'tournament_id': tournament_id})
            
            # Delete related standings
            self.db.standings.delete_many({'tournament_id': tournament_id})
            
            # Update player records
            self.db.players.update_many(
                {'tournaments': tournament_id},
                {'$pull': {'tournaments': tournament_id}}
            )
            
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting tournament: {e}")
            return False
    
    def get_tournament_players(self, tournament_id):
        """Get players for a tournament."""
        try:
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament or 'players' not in tournament:
                return []
            
            player_ids = [ObjectId(p_id) for p_id in tournament['players']]
            players = list(self.db.players.find({
                '_id': {'$in': player_ids}
            }, {'_id': 1, 'name': 1, 'email': 1}))
            
            for player in players:
                player['id'] = str(player.pop('_id'))
            
            return players
        except Exception as e:
            print(f"Error getting tournament players: {e}")
            return []
    
    def register_player(self, tournament_id, player_id):
        """Register a player for a tournament."""
        try:
            # Check if tournament exists and is not completed
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament or tournament['status'] == 'completed':
                return False
            
            # Check if player exists
            player = self.db.players.find_one({'_id': ObjectId(player_id)})
            if not player:
                return False
            
            # Check if player is already registered
            if player_id in tournament.get('players', []):
                return True  # Already registered
            
            # Register player
            self.db.tournaments.update_one(
                {'_id': ObjectId(tournament_id)},
                {'$push': {'players': player_id}}
            )
            
            # Update player record
            self.db.players.update_one(
                {'_id': ObjectId(player_id)},
                {'$push': {'tournaments': tournament_id}}
            )
            
            # Create standing record
            self.db.standings.insert_one({
                'tournament_id': tournament_id,
                'player_id': player_id,
                'matches_played': 0,
                'match_points': 0,
                'game_points': 0,
                'match_win_percentage': 0.0,
                'game_win_percentage': 0.0,
                'opponents_match_win_percentage': 0.0,
                'opponents_game_win_percentage': 0.0,
                'active': True
            })
            
            return True
        except Exception as e:
            print(f"Error registering player: {e}")
            return False
    
    def drop_player(self, tournament_id, player_id):
        """Drop a player from a tournament."""
        try:
            # Check if tournament exists
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament:
                return False
            
            # Check if player is registered
            if player_id not in tournament.get('players', []):
                return False
            
            # If tournament is active, mark player as inactive in standings
            if tournament['status'] == 'active':
                self.db.standings.update_one(
                    {'tournament_id': tournament_id, 'player_id': player_id},
                    {'$set': {'active': False}}
                )
            else:
                # If tournament is not active, remove player completely
                self.db.tournaments.update_one(
                    {'_id': ObjectId(tournament_id)},
                    {'$pull': {'players': player_id}}
                )
                
                self.db.players.update_one(
                    {'_id': ObjectId(player_id)},
                    {'$pull': {'tournaments': tournament_id}}
                )
                
                self.db.standings.delete_one({
                    'tournament_id': tournament_id,
                    'player_id': player_id
                })
            
            return True
        except Exception as e:
            print(f"Error dropping player: {e}")
            return False
    
    def get_tournament_rounds(self, tournament_id):
        """Get rounds for a tournament."""
        try:
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament:
                return []
            
            rounds = []
            for round_num in range(1, tournament['current_round'] + 1):
                matches = list(self.db.matches.find({
                    'tournament_id': tournament_id,
                    'round': round_num
                }, {'_id': 1}))
                
                rounds.append({
                    'round': round_num,
                    'match_count': len(matches),
                    'completed': all(m.get('status') == 'completed' for m in matches)
                })
            
            return rounds
        except Exception as e:
            print(f"Error getting tournament rounds: {e}")
            return []
    
    def get_round_pairings(self, tournament_id, round_number):
        """Get pairings for a specific round."""
        try:
            matches = list(self.db.matches.find({
                'tournament_id': tournament_id,
                'round': int(round_number)
            }))
            
            pairings = []
            for match in matches:
                match['id'] = str(match.pop('_id'))
                
                # Get player names
                player1 = self.db.players.find_one({'_id': ObjectId(match['player1_id'])})
                player1_name = player1['name'] if player1 else 'Unknown'
                
                if match.get('player2_id'):
                    player2 = self.db.players.find_one({'_id': ObjectId(match['player2_id'])})
                    player2_name = player2['name'] if player2 else 'Unknown'
                else:
                    player2_name = 'BYE'
                
                pairings.append({
                    'match_id': match['id'],
                    'table_number': match.get('table_number', 0),
                    'player1_id': match['player1_id'],
                    'player1_name': player1_name,
                    'player2_id': match.get('player2_id'),
                    'player2_name': player2_name,
                    'result': match.get('result', ''),
                    'status': match.get('status', 'pending')
                })
            
            return pairings
        except Exception as e:
            print(f"Error getting round pairings: {e}")
            return []
    
    def create_next_round(self, tournament_id):
        """Create pairings for the next round."""
        try:
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament or tournament['status'] != 'active':
                return None
            
            # Check if current round is completed
            current_round = tournament['current_round']
            if current_round > 0:
                matches = list(self.db.matches.find({
                    'tournament_id': tournament_id,
                    'round': current_round
                }))
                
                if not all(m.get('status') == 'completed' for m in matches):
                    return None  # Current round not completed
            
            # Calculate next round number
            next_round = current_round + 1
            
            # Check if we've reached the maximum number of rounds
            if tournament['rounds'] > 0 and next_round > tournament['rounds']:
                return None
            
            # Get active players
            standings = list(self.db.standings.find({
                'tournament_id': tournament_id,
                'active': True
            }))
            
            # Sort standings by match points and tiebreakers
            standings.sort(key=lambda s: (
                s.get('match_points', 0),
                s.get('opponents_match_win_percentage', 0),
                s.get('game_win_percentage', 0),
                s.get('opponents_game_win_percentage', 0)
            ), reverse=True)
            
            # Get player IDs in order
            player_ids = [s['player_id'] for s in standings]
            
            # Get previous matches
            previous_matches = list(self.db.matches.find({
                'tournament_id': tournament_id
            }))
            
            # Create pairings using Swiss algorithm
            pairings = self.swiss_pairing.create_pairings(player_ids, previous_matches)
            
            # Create match documents
            match_ids = []
            table_number = 1
            
            for pair in pairings:
                player1_id = pair[0]
                player2_id = pair[1] if len(pair) > 1 else None  # BYE
                
                match_data = {
                    'tournament_id': tournament_id,
                    'round': next_round,
                    'table_number': table_number,
                    'player1_id': player1_id,
                    'player2_id': player2_id,
                    'player1_wins': 0,
                    'player2_wins': 0,
                    'draws': 0,
                    'status': 'pending',
                    'result': ''
                }
                
                # If player2 is None (BYE), automatically set result
                if player2_id is None:
                    match_data['status'] = 'completed'
                    match_data['result'] = 'bye'
                    match_data['player1_wins'] = 2
                    match_data['player2_wins'] = 0
                    
                    # Update standings for player with BYE
                    self.db.standings.update_one(
                        {'tournament_id': tournament_id, 'player_id': player1_id},
                        {'$inc': {
                            'matches_played': 1,
                            'match_points': 3,  # Win = 3 points
                            'game_points': 2    # 2-0 win
                        }}
                    )
                
                # Insert match
                result = self.db.matches.insert_one(match_data)
                match_ids.append(str(result.inserted_id))
                
                table_number += 1
            
            # Update tournament
            self.db.tournaments.update_one(
                {'_id': ObjectId(tournament_id)},
                {
                    '$set': {'current_round': next_round},
                    '$push': {'matches': {'$each': match_ids}}
                }
            )
            
            # Return pairings
            return self.get_round_pairings(tournament_id, next_round)
        except Exception as e:
            print(f"Error creating next round: {e}")
            return None
    
    def get_tournament_standings(self, tournament_id):
        """Get standings for a tournament."""
        try:
            standings = list(self.db.standings.find({
                'tournament_id': tournament_id
            }))
            
            # Sort standings by match points and tiebreakers
            standings.sort(key=lambda s: (
                s.get('match_points', 0),
                s.get('opponents_match_win_percentage', 0),
                s.get('game_win_percentage', 0),
                s.get('opponents_game_win_percentage', 0)
            ), reverse=True)
            
            # Add rank
            for i, standing in enumerate(standings):
                standing['rank'] = i + 1
                
                # Get player name
                player = self.db.players.find_one({'_id': ObjectId(standing['player_id'])})
                standing['player_name'] = player['name'] if player else 'Unknown'
                
                # Convert ID to string
                standing['id'] = str(standing.pop('_id'))
            
            return standings
        except Exception as e:
            print(f"Error getting tournament standings: {e}")
            return []
    
    def start_tournament(self, tournament_id):
        """Start a tournament."""
        try:
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament or tournament['status'] != 'planned':
                return False
            
            # Check if there are enough players
            player_count = len(tournament.get('players', []))
            if player_count < 2:
                return False
            
            # Calculate number of rounds if not specified
            if tournament['rounds'] == 0:
                # Standard formula for Swiss tournaments
                tournament['rounds'] = max(3, (player_count - 1).bit_length())
            
            # Update tournament status
            self.db.tournaments.update_one(
                {'_id': ObjectId(tournament_id)},
                {'$set': {
                    'status': 'active',
                    'rounds': tournament['rounds'],
                    'updated_at': datetime.utcnow().isoformat()
                }}
            )
            
            return True
        except Exception as e:
            print(f"Error starting tournament: {e}")
            return False
    
    def end_tournament(self, tournament_id):
        """End a tournament."""
        try:
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament or tournament['status'] != 'active':
                return False
            
            # Update tournament status
            self.db.tournaments.update_one(
                {'_id': ObjectId(tournament_id)},
                {'$set': {
                    'status': 'completed',
                    'updated_at': datetime.utcnow().isoformat()
                }}
            )
            
            return True
        except Exception as e:
            print(f"Error ending tournament: {e}")
            return False
