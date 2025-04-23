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
    
    def get_all_tournaments(self, page=1, limit=20, status=None, sort=None):
        """Get all tournaments with optional filtering."""
        try:
            # Calculate skip for pagination
            skip = (page - 1) * limit
            
            # Build filter
            filter_query = {}
            if status:
                filter_query['status'] = status
            
            # Build sort
            sort_query = []
            if sort == 'date':
                sort_query.append(('date', -1))  # Sort by date descending
            else:
                sort_query.append(('created_at', -1))  # Default sort by creation time
            
            # Get total count
            total = self.db.tournaments.count_documents(filter_query)
            
            # Execute query
            tournaments = list(self.db.tournaments.find(
                filter_query,
                {
                    '_id': 1, 
                    'name': 1, 
                    'format': 1,
                    'structure': 1,
                    'date': 1, 
                    'status': 1,
                    'rounds': 1,
                    'current_round': 1,
                    'players': 1
                }
            ).sort(sort_query).skip(skip).limit(limit))
            
            # Process results
            for tournament in tournaments:
                tournament['id'] = str(tournament.pop('_id'))
                tournament['player_count'] = len(tournament.get('players', []))
                tournament.pop('players', None)  # Remove player IDs from response
            
            return {
                'tournaments': tournaments,
                'total': total,
                'page': page,
                'limit': limit
            }
        except Exception as e:
            print(f"Error getting tournaments: {e}")
            return {
                'tournaments': [],
                'total': 0,
                'page': page,
                'limit': limit
            }
    
    def get_tournament_by_id(self, tournament_id):
        """Get tournament by ID."""
        try:
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if tournament:
                # Convert ObjectId to string
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
            
            # Set default structure-specific configuration
            if 'structure_config' not in tournament_data:
                structure_type = tournament_data.get('structure', '').lower()
                if structure_type == 'swiss':
                    tournament_data['structure_config'] = {
                        'allow_intentional_draws': True,
                        'allow_byes': True,
                        'use_seeds_for_byes': False
                    }
                elif structure_type == 'single_elimination':
                    tournament_data['structure_config'] = {
                        'seeded': True,
                        'third_place_match': True
                    }
                elif structure_type == 'double_elimination':
                    tournament_data['structure_config'] = {
                        'seeded': True,
                        'grand_finals_modifier': 'none'  # 'none', 'reset', or 'advantage'
                    }
            
            # Set format-specific configuration (MTG format)
            if 'format_config' not in tournament_data:
                game_format = tournament_data.get('format', '').lower()
                if game_format == 'draft':
                    tournament_data['format_config'] = {
                        'pod_size': 8,
                        'packs_per_player': 3
                    }
                elif game_format == 'commander':
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
            
            player_ids = [ObjectId(p_id) if not isinstance(p_id, ObjectId) else p_id 
                         for p_id in tournament['players']]
            
            players = list(self.db.players.find({
                '_id': {'$in': player_ids}
            }, {'_id': 1, 'name': 1, 'email': 1, 'active': 1}))
            
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
    
    def reinstate_player(self, tournament_id, player_id):
        """Reinstate a dropped player."""
        try:
            # Check if tournament is active
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament or tournament['status'] != 'active':
                return False
            
            # Check if player exists in standings
            standing = self.db.standings.find_one({
                'tournament_id': tournament_id,
                'player_id': player_id
            })
            
            if not standing:
                return False
            
            # Reactivate player
            self.db.standings.update_one(
                {'tournament_id': tournament_id, 'player_id': player_id},
                {'$set': {'active': True}}
            )
            
            return True
        except Exception as e:
            print(f"Error reinstating player: {e}")
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
                }, {'_id': 1, 'status': 1}))
                
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
                match_id = str(match.pop('_id'))
                
                # Get player names
                player1 = self.db.players.find_one({'_id': ObjectId(match['player1_id'])})
                player1_name = player1['name'] if player1 else 'Unknown'
                
                if match.get('player2_id'):
                    player2 = self.db.players.find_one({'_id': ObjectId(match['player2_id'])})
                    player2_name = player2['name'] if player2 else 'Unknown'
                else:
                    player2_name = 'BYE'
                
                pairings.append({
                    'id': match_id,
                    'tournament_id': tournament_id,
                    'round': int(round_number),
                    'table_number': match.get('table_number', 0),
                    'player1_id': match['player1_id'],
                    'player1_name': player1_name,
                    'player2_id': match.get('player2_id'),
                    'player2_name': player2_name,
                    'player1_wins': match.get('player1_wins', 0),
                    'player2_wins': match.get('player2_wins', 0),
                    'draws': match.get('draws', 0),
                    'result': match.get('result', ''),
                    'status': match.get('status', 'pending'),
                    'bracket': match.get('bracket'),
                    'bracket_position': match.get('bracket_position')
                })
            
            return pairings
        except Exception as e:
            print(f"Error getting round pairings: {e}")
            return []
    
    def create_next_round(self, tournament_id):
        """Create pairings for the next round (Swiss)."""
        try:
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament or tournament['status'] != 'active' or tournament.get('structure', '').lower() != 'swiss':
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
            
            # Get structure config
            structure_config = tournament.get('structure_config', {})
            use_seeds_for_byes = structure_config.get('use_seeds_for_byes', False)
            
            # Create pairings using Swiss algorithm
            pairings = self.swiss_pairing.create_pairings(
                player_ids, 
                previous_matches,
                use_seeds_for_byes
            )
            
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
            
            # Add rank and player names
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
    
    def update_standings(self, tournament_id, standings_data):
        """Update tournament standings manually."""
        try:
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament:
                return False
            
            for standing in standings_data:
                standing_id = standing.pop('id', None)
                
                if not standing_id:
                    continue
                
                # Remove player_name as it's not stored in the database
                standing.pop('player_name', None)
                
                # Update standing
                self.db.standings.update_one(
                    {'_id': ObjectId(standing_id)},
                    {'$set': standing}
                )
            
            return True
        except Exception as e:
            print(f"Error updating standings: {e}")
            return False
    
    def start_tournament(self, tournament_id):
        """Start a tournament and create initial bracket based on structure."""
        try:
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament or tournament['status'] != 'planned':
                return False
            
            # Check if there are enough players
            player_count = len(tournament.get('players', []))
            if player_count < 2:
                return False
            
            # Get tournament structure
            structure = tournament.get('structure', 'swiss').lower()
            
            # Start tournament based on structure
            if structure == 'single_elimination':
                return self.create_single_elimination_bracket(tournament_id, tournament['players'])
            elif structure == 'double_elimination':
                return self.create_double_elimination_bracket(tournament_id, tournament['players'])
            else:  # Swiss
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
                
                # Create first round
                pairings = self.create_next_round(tournament_id)
                
                return pairings is not None
        except Exception as e:
            print(f"Error starting tournament: {e}")
            return False
    
    def create_single_elimination_bracket(self, tournament_id, player_ids):
        """Create a single elimination bracket."""
        try:
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament:
                return False
            
            # Get tournament structure config
            structure_config = tournament.get('structure_config', {})
            seeded = structure_config.get('seeded', True)
            third_place_match = structure_config.get('third_place_match', True)
            
            # Ensure player_ids are strings
            player_ids = [str(pid) if isinstance(pid, ObjectId) else pid for pid in player_ids]
            
            # Calculate number of rounds
            player_count = len(player_ids)
            rounds = (player_count - 1).bit_length()
            
            # Calculate the number of slots in the bracket (power of 2)
            bracket_size = 2 ** rounds
            
            # Arrange players according to seeding
            arranged_players = self._arrange_single_elim_seeds(player_ids, bracket_size, seeded)
            
            # Create first round matches
            round_matches = []
            for i in range(0, bracket_size, 2):
                player1_idx = i
                player2_idx = i + 1
                
                player1_id = arranged_players[player1_idx] if player1_idx < len(arranged_players) else None
                player2_id = arranged_players[player2_idx] if player2_idx < len(arranged_players) else None
                
                # Skip creating matches for double byes
                if player1_id is None and player2_id is None:
                    continue
                
                # Automatically advance players with byes
                if player1_id is not None and player2_id is None:
                    match_data = {
                        'tournament_id': tournament_id,
                        'round': 1,
                        'bracket': 'single',
                        'bracket_position': i // 2,
                        'player1_id': player1_id,
                        'player2_id': None,  # BYE
                        'player1_wins': 2,
                        'player2_wins': 0,
                        'draws': 0,
                        'status': 'completed',
                        'result': 'bye',
                        'next_match': i // 4 if rounds > 1 else None
                    }
                elif player1_id is None and player2_id is not None:
                    match_data = {
                        'tournament_id': tournament_id,
                        'round': 1,
                        'bracket': 'single',
                        'bracket_position': i // 2,
                        'player1_id': player2_id,  # Swap so the real player is player1
                        'player2_id': None,  # BYE
                        'player1_wins': 2,
                        'player2_wins': 0,
                        'draws': 0,
                        'status': 'completed',
                        'result': 'bye',
                        'next_match': i // 4 if rounds > 1 else None
                    }
                else:
                    match_data = {
                        'tournament_id': tournament_id,
                        'round': 1,
                        'bracket': 'single',
                        'bracket_position': i // 2,
                        'player1_id': player1_id,
                        'player2_id': player2_id,
                        'player1_wins': 0,
                        'player2_wins': 0,
                        'draws': 0,
                        'status': 'pending',
                        'result': '',
                        'next_match': i // 4 if rounds > 1 else None
                    }
                
                # Insert match
                result = self.db.matches.insert_one(match_data)
                round_matches.append(str(result.inserted_id))
            
            # Create placeholder matches for future rounds
            for r in range(2, rounds + 1):
                matches_in_round = 2 ** (rounds - r)
                for i in range(matches_in_round):
                    next_match = i // 2 if r < rounds else None
                    
                    match_data = {
                        'tournament_id': tournament_id,
                        'round': r,
                        'bracket': 'single',
                        'bracket_position': i,
                        'player1_id': None,  # Will be determined by previous matches
                        'player2_id': None,  # Will be determined by previous matches
                        'player1_wins': 0,
                        'player2_wins': 0,
                        'draws': 0,
                        'status': 'pending',
                        'result': '',
                        'next_match': next_match
                    }
                    
                    # For the final round, there's no next match
                    if r == rounds:
                        match_data.pop('next_match', None)
                    
                    # Insert match
                    result = self.db.matches.insert_one(match_data)
                    round_matches.append(str(result.inserted_id))
            
            # Add third-place match if configured
            if third_place_match:
                match_data = {
                    'tournament_id': tournament_id,
                    'round': rounds,
                    'bracket': 'single',
                    'bracket_position': -1,  # Special position for third-place match
                    'player1_id': None,  # Will be loser of one semifinal
                    'player2_id': None,  # Will be loser of other semifinal
                    'player1_wins': 0,
                    'player2_wins': 0,
                    'draws': 0,
                    'status': 'pending',
                    'result': '',
                    'is_third_place_match': True
                }
                
                result = self.db.matches.insert_one(match_data)
                round_matches.append(str(result.inserted_id))
            
            # Create standings for all players
            for player_id in player_ids:
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
            
            # Update tournament
            self.db.tournaments.update_one(
                {'_id': ObjectId(tournament_id)},
                {
                    '$set': {
                        'rounds': rounds,
                        'current_round': 1,
                        'bracket_size': bracket_size,
                        'status': 'active',
                        'updated_at': datetime.utcnow().isoformat()
                    },
                    '$push': {'matches': {'$each': round_matches}}
                }
            )
            
            return True
        except Exception as e:
            print(f"Error creating single elimination bracket: {e}")
            return False
    
    def _arrange_single_elim_seeds(self, player_ids, bracket_size, seeded=True):
        """
        Arrange players according to standard single elimination seeding.
        
        Args:
            player_ids: List of player IDs (already sorted by seed if seeded=True)
            bracket_size: Size of the bracket (power of 2)
            seeded: Whether to use seeding or random arrangement
        
        Returns:
            List of arranged player IDs with None for byes
        """
        if not seeded:
            import random
            # Shuffle players and fill the rest with byes
            shuffled_ids = player_ids.copy()
            random.shuffle(shuffled_ids)
            return shuffled_ids + [None] * (bracket_size - len(player_ids))
        
        # Create the seeded bracket according to standard tournament seeding
        result = [None] * bracket_size
        player_count = len(player_ids)
        
        for seed in range(player_count):
            # Calculate position in the bracket using the standard formula
            position = self._get_seed_position(seed + 1, bracket_size)
            result[position] = player_ids[seed]
        
        return result

    def _get_seed_position(self, seed, bracket_size):
        """
        Calculate the position of a seed in a standard tournament bracket.
        
        Args:
            seed: The seed number (1-indexed)
            bracket_size: Size of the bracket (power of 2)
        
        Returns:
            The position in the bracket (0-indexed)
        """
        # Standard algorithm for determining bracket position
        round_size = bracket_size
        position = seed - 1
        
        while round_size > 1:
            round_size //= 2
            position = round_size * (2 * (position // round_size) + 1) - position - 1
        
        return position
    
    def create_double_elimination_bracket(self, tournament_id, player_ids):
        """Create a double elimination bracket."""
        try:
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament:
                return False
            
            # Get tournament structure config
            structure_config = tournament.get('structure_config', {})
            seeded = structure_config.get('seeded', True)
            grand_finals_modifier = structure_config.get('grand_finals_modifier', 'none')
            
            # Ensure player_ids are strings
            player_ids = [str(pid) if isinstance(pid, ObjectId) else pid for pid in player_ids]
            
            # Calculate number of rounds for the winners bracket
            player_count = len(player_ids)
            winners_rounds = (player_count - 1).bit_length()
            
            # Calculate the number of slots in the bracket (power of 2)
            bracket_size = 2 ** winners_rounds
            
            # Arrange players according to seeding for winners bracket
            arranged_players = self._arrange_single_elim_seeds(player_ids, bracket_size, seeded)
            
            # Track all match IDs
            all_matches = []
            
            # Create winners bracket first round matches
            winners_matches = {}  # Store by bracket position for later reference
            for i in range(0, bracket_size, 2):
                player1_idx = i
                player2_idx = i + 1
                
                player1_id = arranged_players[player1_idx] if player1_idx < len(arranged_players) else None
                player2_id = arranged_players[player2_idx] if player2_idx < len(arranged_players) else None
                
                # Skip creating matches for double byes
                if player1_id is None and player2_id is None:
                    continue
                
                # Handle byes
                if player1_id is not None and player2_id is None:
                    match_data = {
                        'tournament_id': tournament_id,
                        'round': 1,
                        'bracket': 'winners',
                        'bracket_position': i // 2,
                        'player1_id': player1_id,
                        'player2_id': None,  # BYE
                        'player1_wins': 2,
                        'player2_wins': 0,
                        'draws': 0,
                        'status': 'completed',
                        'result': 'bye',
                        'winners_next_match': i // 4,
                        'losers_next_match': None
                    }
                elif player1_id is None and player2_id is not None:
                    match_data = {
                        'tournament_id': tournament_id,
                        'round': 1,
                        'bracket': 'winners',
                        'bracket_position': i // 2,
                        'player1_id': player2_id,  # Swap so the real player is player1
                        'player2_id': None,  # BYE
                        'player1_wins': 2,
                        'player2_wins': 0,
                        'draws': 0,
                        'status': 'completed',
                        'result': 'bye',
                        'winners_next_match': i // 4,
                        'losers_next_match': None
                    }
                else:
                    match_data = {
                        'tournament_id': tournament_id,
                        'round': 1,
                        'bracket': 'winners',
                        'bracket_position': i // 2,
                        'player1_id': player1_id,
                        'player2_id': player2_id,
                        'player1_wins': 0,
                        'player2_wins': 0,
                        'draws': 0,
                        'status': 'pending',
                        'result': '',
                        'winners_next_match': i // 4,
                        'losers_next_match': (i // 4) + (bracket_size // 4)  # Position in losers bracket
                    }
                
                # Insert match
                result = self.db.matches.insert_one(match_data)
                match_id = str(result.inserted_id)
                winners_matches[(1, i // 2)] = match_id
                all_matches.append(match_id)
            
            # Create placeholder matches for future winners bracket rounds
            for r in range(2, winners_rounds + 1):
                matches_in_round = 2 ** (winners_rounds - r)
                for i in range(matches_in_round):
                    if r < winners_rounds:
                        winners_next = i // 2
                        losers_next = self._calculate_losers_position(r, i, bracket_size)
                    else:
                        winners_next = None
                        losers_next = None  # Grand finals handled separately
                    
                    match_data = {
                        'tournament_id': tournament_id,
                        'round': r,
                        'bracket': 'winners',
                        'bracket_position': i,
                        'player1_id': None,
                        'player2_id': None,
                        'player1_wins': 0,
                        'player2_wins': 0,
                        'draws': 0,
                        'status': 'pending',
                        'result': '',
                        'winners_next_match': winners_next,
                        'losers_next_match': losers_next
                    }
                    
                    # Insert match
                    result = self.db.matches.insert_one(match_data)
                    match_id = str(result.inserted_id)
                    winners_matches[(r, i)] = match_id
                    all_matches.append(match_id)
            
            # Create losers bracket matches
            losers_matches = {}
            losers_rounds = winners_rounds * 2 - 1
            
            # Create all losers bracket rounds
            for r in range(1, losers_rounds + 1):
                # Determine number of matches in this round
                if r % 2 == 1:  # Odd rounds: players coming from winners bracket
                    matches_in_round = 2 ** (winners_rounds - (r // 2) - 2)
                else:  # Even rounds: consolidation matches
                    matches_in_round = 2 ** (winners_rounds - (r // 2) - 1)
                
                # No matches in this round
                if matches_in_round <= 0:
                    continue
                
                for i in range(matches_in_round):
                    # Determine next match
                    if r < losers_rounds:
                        if r % 2 == 1:  # Odd rounds
                            next_match = i + (matches_in_round // 2)
                        else:  # Even rounds
                            next_match = i // 2
                    else:
                        next_match = None  # Final round
                    
                    match_data = {
                        'tournament_id': tournament_id,
                        'round': r,
                        'bracket': 'losers',
                        'bracket_position': i,
                        'player1_id': None,
                        'player2_id': None,
                        'player1_wins': 0,
                        'player2_wins': 0,
                        'draws': 0,
                        'status': 'pending',
                        'result': '',
                        'winners_next_match': next_match,
                        'losers_next_match': None  # No lower bracket in losers
                    }
                    
                    # Insert match
                    result = self.db.matches.insert_one(match_data)
                    match_id = str(result.inserted_id)
                    losers_matches[(r, i)] = match_id
                    all_matches.append(match_id)
            
            # Create grand finals match(es)
            grand_finals_data = {
                'tournament_id': tournament_id,
                'round': winners_rounds + 1,
                'bracket': 'grand_finals',
                'bracket_position': 0,
                'player1_id': None,  # Winner of winners bracket
                'player2_id': None,  # Winner of losers bracket
                'player1_wins': 0,
                'player2_wins': 0,
                'draws': 0,
                'status': 'pending',
                'result': '',
                'winners_next_match': None,
                'losers_next_match': None
            }
            
            # Insert grand finals match
            result = self.db.matches.insert_one(grand_finals_data)
            grand_finals_id = str(result.inserted_id)
            all_matches.append(grand_finals_id)
            
            # Create reset bracket if needed
            if grand_finals_modifier == 'reset':
                reset_finals_data = {
                    'tournament_id': tournament_id,
                    'round': winners_rounds + 2,
                    'bracket': 'grand_finals',
                    'bracket_position': 1,
                    'player1_id': None,
                    'player2_id': None,
                    'player1_wins': 0,
                    'player2_wins': 0,
                    'draws': 0,
                    'status': 'pending',
                    'result': '',
                    'winners_next_match': None,
                    'losers_next_match': None,
                    'is_reset_match': True
                }
                
                result = self.db.matches.insert_one(reset_finals_data)
                all_matches.append(str(result.inserted_id))
            
            # Create standings for all players
            for player_id in player_ids:
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
            
            # Update tournament
            self.db.tournaments.update_one(
                {'_id': ObjectId(tournament_id)},
                {
                    '$set': {
                        'winners_rounds': winners_rounds,
                        'losers_rounds': losers_rounds,
                        'current_round': 1,
                        'bracket_size': bracket_size,
                        'status': 'active',
                        'updated_at': datetime.utcnow().isoformat()
                    },
                    '$push': {'matches': {'$each': all_matches}}
                }
            )
            
            return True
        except Exception as e:
            print(f"Error creating double elimination bracket: {e}")
            return False
    
    def _calculate_losers_position(self, winners_round, winners_position, bracket_size):
        """Calculate corresponding position in losers bracket."""
        # This is a simplification - actual mapping depends on bracket size and round
        if winners_round == 2:
            return winners_position + (bracket_size // 4)
        else:
            # For deeper rounds, the mapping gets more complex
            # This would need a complete implementation based on standard DE brackets
            return winners_position
    
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
    
    def advance_bracket(self, tournament_id, match_id, winner_id):
        """Advance a player in a bracket after match is completed."""
        try:
            match = self.db.matches.find_one({'_id': ObjectId(match_id)})
            if not match:
                return False
            
            # Get tournament
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament:
                return False
            
            # Check if it's a bracket tournament
            structure = tournament.get('structure', '').lower()
            if structure not in ['single_elimination', 'double_elimination']:
                return False
            
            # For single elimination
            if structure == 'single_elimination':
                next_match_position = match.get('next_match')
                if next_match_position is None:
                    # This is the final match, no advancement needed
                    return True
                
                # Find next match in bracket
                next_match = self.db.matches.find_one({
                    'tournament_id': tournament_id,
                    'round': match['round'] + 1,
                    'bracket_position': next_match_position
                })
                
                if not next_match:
                    return False
                
                # Determine which player slot to fill
                if match['bracket_position'] % 2 == 0:  # Even positions go to player1
                    self.db.matches.update_one(
                        {'_id': next_match['_id']},
                        {'$set': {'player1_id': winner_id}}
                    )
                else:  # Odd positions go to player2
                    self.db.matches.update_one(
                        {'_id': next_match['_id']},
                        {'$set': {'player2_id': winner_id}}
                    )
                
                # Handle third place match for semifinals
                if match['round'] == tournament.get('rounds', 0) - 1:
                    third_place_match = self.db.matches.find_one({
                        'tournament_id': tournament_id,
                        'is_third_place_match': True
                    })
                    
                    if third_place_match:
                        loser_id = match['player1_id'] if winner_id == match['player2_id'] else match['player2_id']
                        
                        if match['bracket_position'] % 2 == 0:
                            self.db.matches.update_one(
                                {'_id': third_place_match['_id']},
                                {'$set': {'player1_id': loser_id}}
                            )
                        else:
                            self.db.matches.update_one(
                                {'_id': third_place_match['_id']},
                                {'$set': {'player2_id': loser_id}}
                            )
            
            # For double elimination
            elif structure == 'double_elimination':
                # Handle winners bracket
                if match['bracket'] == 'winners':
                    winners_next = match.get('winners_next_match')
                    losers_next = match.get('losers_next_match')
                    
                    # Winner advances in winners bracket
                    if winners_next is not None:
                        next_match = self.db.matches.find_one({
                            'tournament_id': tournament_id,
                            'round': match['round'] + 1,
                            'bracket': 'winners',
                            'bracket_position': winners_next
                        })
                        
                        if next_match:
                            if match['bracket_position'] % 2 == 0:
                                self.db.matches.update_one(
                                    {'_id': next_match['_id']},
                                    {'$set': {'player1_id': winner_id}}
                                )
                            else:
                                self.db.matches.update_one(
                                    {'_id': next_match['_id']},
                                    {'$set': {'player2_id': winner_id}}
                                )
                    
                    # Loser goes to losers bracket
                    if losers_next is not None:
                        loser_id = match['player1_id'] if winner_id == match['player2_id'] else match['player2_id']
                        
                        losers_match = self.db.matches.find_one({
                            'tournament_id': tournament_id,
                            'bracket': 'losers',
                            'bracket_position': losers_next
                        })
                        
                        if losers_match:
                            if losers_match.get('player1_id') is None:
                                self.db.matches.update_one(
                                    {'_id': losers_match['_id']},
                                    {'$set': {'player1_id': loser_id}}
                                )
                            else:
                                self.db.matches.update_one(
                                    {'_id': losers_match['_id']},
                                    {'$set': {'player2_id': loser_id}}
                                )
                
                # Handle losers bracket advancement
                elif match['bracket'] == 'losers':
                    winners_next = match.get('winners_next_match')
                    
                    if winners_next is not None:
                        next_match = self.db.matches.find_one({
                            'tournament_id': tournament_id,
                            'bracket': 'losers',
                            'bracket_position': winners_next
                        })
                        
                        if next_match:
                            if next_match.get('player1_id') is None:
                                self.db.matches.update_one(
                                    {'_id': next_match['_id']},
                                    {'$set': {'player1_id': winner_id}}
                                )
                            else:
                                self.db.matches.update_one(
                                    {'_id': next_match['_id']},
                                    {'$set': {'player2_id': winner_id}}
                                )
                    
                    # Handle advancement to grand finals
                    elif match['round'] == tournament.get('losers_rounds', 0):
                        grand_finals = self.db.matches.find_one({
                            'tournament_id': tournament_id,
                            'bracket': 'grand_finals',
                            'bracket_position': 0
                        })
                        
                        if grand_finals:
                            self.db.matches.update_one(
                                {'_id': grand_finals['_id']},
                                {'$set': {'player2_id': winner_id}}
                            )
            
            return True
        except Exception as e:
            print(f"Error advancing bracket: {e}")
            return False
        
    def _calculate_losers_round(self, winners_round):
        """Calculate the corresponding losers bracket round."""
        # This is a simplification - actual mapping can be more complex
        # depending on the tournament structure
        losers_round = winners_round * 2 - 1
        return losers_round
    
    def update_match_result(self, match_id, result_data):
        """Update match result and advance players in brackets if needed."""
        try:
            match = self.db.matches.find_one({'_id': ObjectId(match_id)})
            if not match or match['status'] == 'completed':
                return False
            
            # Extract result data
            player1_wins = result_data.get('player1_wins', 0)
            player2_wins = result_data.get('player2_wins', 0)
            draws = result_data.get('draws', 0)
            
            # Validate result
            if player1_wins < 0 or player2_wins < 0 or draws < 0:
                return False
            
            # Determine result
            if player1_wins > player2_wins:
                result = 'win'
                match_points_player1 = 3  # Win = 3 points
                match_points_player2 = 0
                winner_id = match['player1_id']
            elif player2_wins > player1_wins:
                result = 'loss'
                match_points_player1 = 0
                match_points_player2 = 3
                winner_id = match['player2_id']
            else:
                result = 'draw'
                match_points_player1 = 1  # Draw = 1 point
                match_points_player2 = 1
                winner_id = None
            
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
            
            # Get tournament
            tournament = self.db.tournaments.find_one({'_id': ObjectId(match['tournament_id'])})
            if not tournament:
                return False
            
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
            
            # For bracket tournaments, advance the winner to the next round
            structure = tournament.get('structure', '').lower()
            if structure in ['single_elimination', 'double_elimination'] and winner_id:
                self.advance_bracket(match['tournament_id'], match_id, winner_id)
            
            return True
        except Exception as e:
            print(f"Error updating match result: {e}")
            return False
    
    def draw_match(self, match_id):
        """Mark a match as intentional draw."""
        try:
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
            
            # Update win percentages
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
    
    def generate_pairings_report(self, tournament_id, round_number=None):
        """Generate a pairings report for printing."""
        try:
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament:
                return None
            
            # If round_number is not specified, use current round
            if round_number is None:
                round_number = tournament.get('current_round', 1)
            
            # Get pairings
            pairings = self.get_round_pairings(tournament_id, round_number)
            
            # Format for report
            report = {
                'tournament_name': tournament['name'],
                'round': round_number,
                'date': tournament['date'],
                'format': tournament['format'],
                'pairings': pairings
            }
            
            return report
        except Exception as e:
            print(f"Error generating pairings report: {e}")
            return None
    
    def generate_standings_report(self, tournament_id):
        """Generate a standings report for printing."""
        try:
            tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
            if not tournament:
                return None
            
            # Get standings
            standings = self.get_tournament_standings(tournament_id)
            
            # Format for report
            report = {
                'tournament_name': tournament['name'],
                'date': tournament['date'],
                'format': tournament['format'],
                'status': tournament['status'],
                'current_round': tournament['current_round'],
                'total_rounds': tournament['rounds'],
                'standings': standings
            }
            
            return report
        except Exception as e:
            print(f"Error generating standings report: {e}")
            return None