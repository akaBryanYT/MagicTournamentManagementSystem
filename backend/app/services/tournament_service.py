"""
Tournament service for the Tournament Management System.
"""

from datetime import datetime
from bson.objectid import ObjectId
from app.models.database import DatabaseConfig
from app.services.swiss_pairing import SwissPairingService
from sqlalchemy import text
import json

class TournamentService:
    """Service for tournament operations."""
    
    def __init__(self):
        """Initialize the tournament service."""
        self.db_config = DatabaseConfig()
        self.db_config.connect()
        self.db = self.db_config.db
        self.db_type = self.db_config.db_type
        self.swiss_pairing = SwissPairingService()

    def get_all_tournaments(self, page=1, limit=20, status=None, sort=None):
        """Get all tournaments with optional filtering."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                # Build where clause
                where_clause = "1=1"
                params = {
                    'page': page,
                    'limit': limit,
                    'offset': (page - 1) * limit
                }
                
                if status:
                    where_clause += " AND status = :status"
                    params['status'] = status
                
                # Build order by clause
                order_by = "created_at DESC"
                if sort == 'date':
                    order_by = "date DESC"
                
                try:
                    # Get total count
                    count_result = self.db.execute(text(f"""
                        SELECT COUNT(*) FROM tournaments
                        WHERE {where_clause}
                    """), params)
                    total = count_result.scalar()
                    
                    # Execute query
                    result = self.db.execute(text(f"""
                        SELECT t.id, t.name, t.format, 
                               COALESCE(t.structure, 'swiss') as structure, 
                               t.date, t.status, t.rounds, t.current_round,
                               (SELECT COUNT(*) FROM tournament_players tp WHERE tp.tournament_id = t.id) AS player_count
                        FROM tournaments t
                        WHERE {where_clause}
                        ORDER BY {order_by}
                        LIMIT :limit OFFSET :offset
                    """), params)
                    
                    # Process results
                    tournaments = []
                    for row in result.mappings():
                        tournament = dict(row)
                        tournament['id'] = str(tournament['id'])
                        tournament['date'] = tournament['date'].isoformat() if tournament['date'] else None
                        tournaments.append(tournament)
                    
                    return {
                        'tournaments': tournaments,
                        'total': total,
                        'page': page,
                        'limit': limit
                    }
                except Exception as e:
                    print(f"Error in database query: {e}")
                    self.db.rollback()  # Make sure to rollback transaction on error
                    raise
        except Exception as e:
            print(f"Error getting tournaments: {e}")
            if self.db_type == 'postgresql':
                try:
                    self.db.rollback()  # Extra safety to ensure rollback
                except:
                    pass  # Ignore if rollback fails
            return {
                'tournaments': [],
                'total': 0,
                'page': page,
                'limit': limit
            }
    
    def get_tournament_by_id(self, tournament_id):
        """Get tournament by ID."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT t.*,
                           (SELECT array_agg(player_id) FROM tournament_players WHERE tournament_id = t.id) AS players,
                           (SELECT array_agg(id) FROM matches WHERE tournament_id = t.id) AS matches
                    FROM tournaments t
                    WHERE t.id = :tournament_id
                """), {'tournament_id': int(tournament_id)})
                
                row = result.mappings().first()
                if row:
                    tournament = dict(row)
                    tournament['id'] = str(tournament['id'])
                    tournament['date'] = tournament['date'].isoformat() if tournament['date'] else None
                    tournament['created_at'] = tournament['created_at'].isoformat() if tournament['created_at'] else None
                    tournament['updated_at'] = tournament['updated_at'].isoformat() if tournament['updated_at'] else None
                    
                    # Convert JSON fields
                    if tournament['tiebreakers']:
                        tournament['tiebreakers'] = tournament['tiebreakers'] 
                    if tournament['time_limits']:
                        tournament['time_limits'] = tournament['time_limits']
                    if tournament['format_config']:
                        tournament['format_config'] = tournament['format_config']
                    if tournament['structure_config']:
                        tournament['structure_config'] = tournament['structure_config']
                    
                    # Convert player IDs to strings
                    if tournament['players']:
                        tournament['players'] = [str(p) for p in tournament['players']]
                    else:
                        tournament['players'] = []
                    
                    # Convert match IDs to strings
                    if tournament['matches']:
                        tournament['matches'] = [str(m) for m in tournament['matches']]
                    else:
                        tournament['matches'] = []
                    
                    return tournament
                return None
        except Exception as e:
            print(f"Error getting tournament: {e}")
            return None
    
    def create_tournament(self, tournament_data):
        """Create a new tournament."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                # Convert JSON fields
                tiebreakers = tournament_data.get('tiebreakers', {
                    'match_points': True,
                    'opponents_match_win_percentage': True,
                    'game_win_percentage': True,
                    'opponents_game_win_percentage': True
                })
                
                time_limits = tournament_data.get('time_limits', {})
                
                # Set default structure-specific configuration
                structure_type = tournament_data.get('structure', 'swiss').lower()
                structure_config = tournament_data.get('structure_config', {})
                if not structure_config:
                    if structure_type == 'swiss':
                        structure_config = {
                            'allow_intentional_draws': True,
                            'allow_byes': True,
                            'use_seeds_for_byes': False
                        }
                    elif structure_type == 'single_elimination':
                        structure_config = {
                            'seeded': True,
                            'third_place_match': True
                        }
                    elif structure_type == 'double_elimination':
                        structure_config = {
                            'seeded': True,
                            'grand_finals_modifier': 'none'
                        }
                
                # Set format-specific configuration
                game_format = tournament_data.get('format', '').lower()
                format_config = tournament_data.get('format_config', {})
                if not format_config:
                    if game_format == 'draft':
                        format_config = {
                            'pod_size': 8,
                            'packs_per_player': 3
                        }
                    elif game_format == 'commander':
                        format_config = {
                            'pod_size': 4,
                            'point_system': 'standard'
                        }
                
                # Set default rounds
                rounds = tournament_data.get('rounds', 0)
                
                # Insert tournament
                result = self.db.execute(text("""
                    INSERT INTO tournaments 
                    (name, format, structure, date, location, status, rounds, current_round, 
                     created_at, updated_at, tiebreakers, time_limits, format_config, structure_config)
                    VALUES 
                    (:name, :format, :structure, :date, :location, 'planned', :rounds, 0, 
                     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, :tiebreakers, :time_limits, :format_config, :structure_config)
                    RETURNING id
                """), {
                    'name': tournament_data['name'],
                    'format': tournament_data['format'],
                    'structure': tournament_data.get('structure', 'swiss'),
                    'date': tournament_data['date'],
                    'location': tournament_data.get('location', ''),
                    'rounds': rounds,
                    'tiebreakers': json.dumps(tiebreakers),
                    'time_limits': json.dumps(time_limits),
                    'format_config': json.dumps(format_config),
                    'structure_config': json.dumps(structure_config)
                })
                
                self.db.commit()
                tournament_id = result.scalar()
                return str(tournament_id)
        except Exception as e:
            print(f"Error creating tournament: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return None
    
    def update_tournament(self, tournament_id, tournament_data):
        """Update tournament by ID."""
        try:
            if self.db_type == 'mongodb':
                # Check if tournament exists
                tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
                if not tournament:
                    return False
                
                # Update timestamp
                tournament_data['updated_at'] = datetime.utcnow().isoformat()
                
                # Remove fields that shouldn't be updated
                protected_fields = ['_id', 'id', 'created_at', 'players', 'matches']
                for field in protected_fields:
                    if field in tournament_data:
                        del tournament_data[field]
                
                # Update tournament
                result = self.db.tournaments.update_one(
                    {'_id': ObjectId(tournament_id)},
                    {'$set': tournament_data}
                )
                
                return result.modified_count > 0
            else:
                # PostgreSQL implementation
                # Check if tournament exists
                result = self.db.execute(text("""
                    SELECT id FROM tournaments WHERE id = :tournament_id
                """), {'tournament_id': int(tournament_id)})
                
                if not result.first():
                    return False
                
                # Remove fields that shouldn't be updated
                protected_fields = ['id', 'created_at']
                update_data = {k: v for k, v in tournament_data.items() if k not in protected_fields}
                
                if not update_data:
                    return False
                
                # Handle JSON fields
                for json_field in ['tiebreakers', 'time_limits', 'format_config', 'structure_config']:
                    if json_field in update_data and update_data[json_field] is not None:
                        update_data[json_field] = json.dumps(update_data[json_field])
                
                # Build set clause
                set_clauses = []
                params = {'tournament_id': int(tournament_id)}
                
                for key, value in update_data.items():
                    set_clauses.append(f"{key} = :{key}")
                    params[key] = value
                
                # Add updated timestamp
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                
                query = f"""
                    UPDATE tournaments
                    SET {', '.join(set_clauses)}
                    WHERE id = :tournament_id
                """
                
                result = self.db.execute(text(query), params)
                self.db.commit()
                
                return result.rowcount > 0
        except Exception as e:
            print(f"Error updating tournament: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False
    
    def delete_tournament(self, tournament_id):
        """Delete tournament by ID."""
        try:
            if self.db_type == 'mongodb':
                # Check if tournament exists
                tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
                if not tournament:
                    return False
                
                # Check if tournament has matches
                if len(tournament.get('matches', [])) > 0:
                    return False
                
                # Delete tournament
                result = self.db.tournaments.delete_one({'_id': ObjectId(tournament_id)})
                return result.deleted_count > 0
            else:
                # PostgreSQL implementation
                # Check if tournament has matches
                result = self.db.execute(text("""
                    SELECT COUNT(*) FROM matches WHERE tournament_id = :tournament_id
                """), {'tournament_id': int(tournament_id)})
                
                if result.scalar() > 0:
                    return False
                
                # Delete tournament players junction
                self.db.execute(text("""
                    DELETE FROM tournament_players WHERE tournament_id = :tournament_id
                """), {'tournament_id': int(tournament_id)})
                
                # Delete standings
                self.db.execute(text("""
                    DELETE FROM standings WHERE tournament_id = :tournament_id
                """), {'tournament_id': int(tournament_id)})
                
                # Delete tournament
                result = self.db.execute(text("""
                    DELETE FROM tournaments WHERE id = :tournament_id
                """), {'tournament_id': int(tournament_id)})
                
                self.db.commit()
                return result.rowcount > 0
        except Exception as e:
            print(f"Error deleting tournament: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False
    
    def get_tournament_players(self, tournament_id):
        """Get players for a tournament."""
        try:
            if self.db_type == 'mongodb':
                tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
                if not tournament:
                    return []
                
                player_ids = tournament.get('players', [])
                if not player_ids:
                    return []
                
                # Convert string IDs to ObjectIds
                player_obj_ids = [ObjectId(pid) if isinstance(pid, str) else pid for pid in player_ids]
                
                # Get player documents
                players = list(self.db.players.find({'_id': {'$in': player_obj_ids}}))
                
                # Convert ObjectIds to strings
                for player in players:
                    player['id'] = str(player.pop('_id'))
                
                return players
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT p.id, p.name, p.email, p.phone, p.dci_number, p.active
                    FROM players p
                    JOIN tournament_players tp ON p.id = tp.player_id
                    WHERE tp.tournament_id = :tournament_id
                """), {'tournament_id': int(tournament_id)})
                
                players = []
                for row in result.mappings():
                    player = dict(row)
                    player['id'] = str(player['id'])
                    players.append(player)
                
                return players
        except Exception as e:
            print(f"Error getting tournament players: {e}")
            return []
    
    def register_player(self, tournament_id, player_id):
        """Register a player for a tournament."""
        try:
            if self.db_type == 'mongodb':
                # Check if tournament and player exist
                tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
                player = self.db.players.find_one({'_id': ObjectId(player_id)})
                
                if not tournament or not player:
                    return False
                
                # Check if player is already registered
                if player_id in tournament.get('players', []):
                    return True
                
                # Register player
                result = self.db.tournaments.update_one(
                    {'_id': ObjectId(tournament_id)},
                    {'$addToSet': {'players': player_id}}
                )
                
                # Create standing for player if not exists
                standing = self.db.standings.find_one({
                    'tournament_id': tournament_id,
                    'player_id': player_id
                })
                
                if not standing:
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
                        'rank': 0,
                        'active': True
                    })
                
                return result.modified_count > 0
            else:
                # PostgreSQL implementation
                # Check if tournament and player exist
                tournament_result = self.db.execute(text("""
                    SELECT id FROM tournaments WHERE id = :tournament_id
                """), {'tournament_id': int(tournament_id)})
                
                player_result = self.db.execute(text("""
                    SELECT id FROM players WHERE id = :player_id
                """), {'player_id': int(player_id)})
                
                if not tournament_result.first() or not player_result.first():
                    return False
                
                # Check if player is already registered
                junction_result = self.db.execute(text("""
                    SELECT 1 FROM tournament_players
                    WHERE tournament_id = :tournament_id AND player_id = :player_id
                """), {
                    'tournament_id': int(tournament_id),
                    'player_id': int(player_id)
                })
                
                if junction_result.first():
                    return True
                
                # Register player
                self.db.execute(text("""
                    INSERT INTO tournament_players (tournament_id, player_id)
                    VALUES (:tournament_id, :player_id)
                """), {
                    'tournament_id': int(tournament_id),
                    'player_id': int(player_id)
                })
                
                # Create standing for player if not exists
                standing_result = self.db.execute(text("""
                    SELECT id FROM standings
                    WHERE tournament_id = :tournament_id AND player_id = :player_id
                """), {
                    'tournament_id': int(tournament_id),
                    'player_id': int(player_id)
                })
                
                if not standing_result.first():
                    self.db.execute(text("""
                        INSERT INTO standings (
                            tournament_id, player_id, matches_played, match_points,
                            game_points, match_win_percentage, game_win_percentage,
                            opponents_match_win_percentage, opponents_game_win_percentage,
                            rank, active
                        ) VALUES (
                            :tournament_id, :player_id, 0, 0,
                            0, 0.0, 0.0,
                            0.0, 0.0,
                            0, TRUE
                        )
                    """), {
                        'tournament_id': int(tournament_id),
                        'player_id': int(player_id)
                    })
                
                self.db.commit()
                return True
        except Exception as e:
            print(f"Error registering player: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False
    
    def drop_player(self, tournament_id, player_id):
        """Drop a player from a tournament."""
        try:
            if self.db_type == 'mongodb':
                # Update standing to mark player as inactive
                result = self.db.standings.update_one(
                    {
                        'tournament_id': tournament_id,
                        'player_id': player_id
                    },
                    {'$set': {'active': False}}
                )
                
                return result.modified_count > 0
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    UPDATE standings
                    SET active = FALSE
                    WHERE tournament_id = :tournament_id AND player_id = :player_id
                """), {
                    'tournament_id': int(tournament_id),
                    'player_id': int(player_id)
                })
                
                self.db.commit()
                return result.rowcount > 0
        except Exception as e:
            print(f"Error dropping player: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False
    
    def reinstatePlayer(self, tournament_id, player_id):
        """Reinstate a dropped player."""
        try:
            if self.db_type == 'mongodb':
                # Update standing to mark player as active
                result = self.db.standings.update_one(
                    {
                        'tournament_id': tournament_id,
                        'player_id': player_id
                    },
                    {'$set': {'active': True}}
                )
                
                return result.modified_count > 0
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    UPDATE standings
                    SET active = TRUE
                    WHERE tournament_id = :tournament_id AND player_id = :player_id
                """), {
                    'tournament_id': int(tournament_id),
                    'player_id': int(player_id)
                })
                
                self.db.commit()
                return result.rowcount > 0
        except Exception as e:
            print(f"Error reinstating player: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False
    
    def get_tournament_rounds(self, tournament_id):
        """Get rounds for a tournament."""
        try:
            if self.db_type == 'mongodb':
                tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
                if not tournament:
                    return []
                
                rounds = []
                for i in range(1, tournament.get('current_round', 0) + 1):
                    rounds.append({
                        'round_number': i,
                        'completed': self._is_round_completed_mongo(tournament_id, i)
                    })
                
                return rounds
            else:
                # PostgreSQL implementation
                # Get tournament current round
                tournament_result = self.db.execute(text("""
                    SELECT current_round FROM tournaments WHERE id = :tournament_id
                """), {'tournament_id': int(tournament_id)})
                
                row = tournament_result.first()
                if not row:
                    return []
                
                current_round = row[0]
                
                # Build rounds data
                rounds = []
                for i in range(1, current_round + 1):
                    # Check if round is completed
                    round_completed = self._is_round_completed_sql(int(tournament_id), i)
                    
                    rounds.append({
                        'round_number': i,
                        'completed': round_completed
                    })
                
                return rounds
        except Exception as e:
            print(f"Error getting tournament rounds: {e}")
            return []
    
    def _is_round_completed_mongo(self, tournament_id, round_number):
        """Check if all matches in a round are completed (MongoDB)."""
        try:
            # Count total matches in the round
            total_matches = self.db.matches.count_documents({
                'tournament_id': tournament_id,
                'round': round_number
            })
            
            # Count completed matches in the round
            completed_matches = self.db.matches.count_documents({
                'tournament_id': tournament_id,
                'round': round_number,
                'status': 'completed'
            })
            
            return total_matches > 0 and total_matches == completed_matches
        except Exception as e:
            print(f"Error checking if round is completed: {e}")
            return False
    
    def _is_round_completed_sql(self, tournament_id, round_number):
        """Check if all matches in a round are completed (PostgreSQL)."""
        try:
            result = self.db.execute(text("""
                SELECT 
                    COUNT(*) as total_matches,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_matches
                FROM matches
                WHERE tournament_id = :tournament_id AND round = :round
            """), {
                'tournament_id': tournament_id,
                'round': round_number
            })
            
            row = result.first()
            if not row or row[0] == 0:
                return False
            
            total_matches, completed_matches = row
            return total_matches == completed_matches
        except Exception as e:
            print(f"Error checking if round is completed: {e}")
            return False
    
    def get_round_pairings(self, tournament_id, round_number):
        """Get pairings for a specific round."""
        try:
            if self.db_type == 'mongodb':
                # Get matches for the round
                matches = list(self.db.matches.find({
                    'tournament_id': tournament_id,
                    'round': int(round_number)
                }))
                
                # Get player names
                pairings = []
                for match in matches:
                    match_id = str(match.pop('_id'))
                    
                    # Get player 1 name
                    player1 = self.db.players.find_one({'_id': ObjectId(match['player1_id'])})
                    player1_name = player1['name'] if player1 else 'Unknown'
                    
                    # Get player 2 name (if not a bye)
                    player2_name = 'BYE'
                    if 'player2_id' in match and match['player2_id']:
                        player2 = self.db.players.find_one({'_id': ObjectId(match['player2_id'])})
                        player2_name = player2['name'] if player2 else 'Unknown'
                    
                    pairings.append({
                        'match_id': match_id,
                        'table_number': match.get('table_number', 0),
                        'player1_id': match['player1_id'],
                        'player1_name': player1_name,
                        'player2_id': match.get('player2_id'),
                        'player2_name': player2_name,
                        'status': match.get('status', 'pending'),
                        'result': match.get('result'),
                        'player1_wins': match.get('player1_wins', 0),
                        'player2_wins': match.get('player2_wins', 0),
                        'draws': match.get('draws', 0)
                    })
                
                return pairings
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT 
                        m.id, m.table_number, m.status, m.result,
                        m.player1_id, p1.name as player1_name,
                        m.player2_id, p2.name as player2_name,
                        m.player1_wins, m.player2_wins, m.draws
                    FROM matches m
                    LEFT JOIN players p1 ON m.player1_id = p1.id
                    LEFT JOIN players p2 ON m.player2_id = p2.id
                    WHERE m.tournament_id = :tournament_id AND m.round = :round
                    ORDER BY m.table_number
                """), {
                    'tournament_id': int(tournament_id),
                    'round': int(round_number)
                })
                
                pairings = []
                for row in result.mappings():
                    pairings.append({
                        'match_id': str(row['id']),
                        'table_number': row['table_number'] or 0,
                        'player1_id': str(row['player1_id']),
                        'player1_name': row['player1_name'],
                        'player2_id': str(row['player2_id']) if row['player2_id'] else None,
                        'player2_name': row['player2_name'] if row['player2_id'] else 'BYE',
                        'status': row['status'],
                        'result': row['result'],
                        'player1_wins': row['player1_wins'] or 0,
                        'player2_wins': row['player2_wins'] or 0,
                        'draws': row['draws'] or 0
                    })
                
                return pairings
        except Exception as e:
            print(f"Error getting round pairings: {e}")
            return []
    
    def create_next_round(self, tournament_id):
        """Create pairings for the next round."""
        try:
            if self.db_type == 'mongodb':
                # Get tournament
                tournament = self.db.tournaments.find_one({'_id': ObjectId(tournament_id)})
                if not tournament:
                    return False
                
                # Check if tournament is active
                if tournament['status'] != 'active':
                    return False
                
                # Check if all matches in the current round are completed
                current_round = tournament.get('current_round', 0)
                if current_round > 0:
                    if not self._is_round_completed_mongo(tournament_id, current_round):
                        return False
                
                # Get active players (using standings)
                standings = list(self.db.standings.find({
                    'tournament_id': tournament_id,
                    'active': True
                }).sort([
                    ('match_points', -1),
                    ('opponents_match_win_percentage', -1),
                    ('game_win_percentage', -1),
                    ('opponents_game_win_percentage', -1)
                ]))
                
                player_ids = [s['player_id'] for s in standings]
                
                if not player_ids:
                    return False
                
                # Get previous matches
                previous_matches = list(self.db.matches.find({
                    'tournament_id': tournament_id
                }))
                
                # Create pairings using Swiss algorithm
                next_round = current_round + 1
                structure = tournament.get('structure', 'swiss')
                
                if structure == 'swiss':
                    # Use Swiss pairing algorithm
                    use_seeds = tournament.get('structure_config', {}).get('use_seeds_for_byes', False)
                    pairings = self.swiss_pairing.create_pairings(player_ids, previous_matches, use_seeds)
                    
                    # Create matches from pairings
                    for i, pairing in enumerate(pairings):
                        match_data = {
                            'tournament_id': tournament_id,
                            'round': next_round,
                            'table_number': i + 1,
                            'player1_id': pairing[0],
                            'player1_wins': 0,
                            'player2_wins': 0,
                            'draws': 0,
                            'status': 'pending'
                        }
                        
                        # Set player2 or bye
                        if len(pairing) > 1:
                            match_data['player2_id'] = pairing[1]
                        else:
                            # This is a bye
                            match_data['result'] = 'win'  # Player 1 wins automatically
                            match_data['status'] = 'completed'
                            match_data['player1_wins'] = 2
                            
                            # Update standings for player with bye
                            self.db.standings.update_one(
                                {
                                    'tournament_id': tournament_id,
                                    'player_id': pairing[0]
                                },
                                {'$inc': {
                                    'matches_played': 1,
                                    'match_points': 3,  # Win = 3 points
                                    'game_points': 2    # 2-0 win
                                }}
                            )
                        
                        # Create match
                        match_id = self.db.matches.insert_one(match_data).inserted_id
                        
                        # Update tournament matches list
                        self.db.tournaments.update_one(
                            {'_id': ObjectId(tournament_id)},
                            {'$push': {'matches': str(match_id)}}
                        )
                else:
                    # TODO: Implement other tournament structures (single/double elimination)
                    pass
                
                # Update tournament round
                self.db.tournaments.update_one(
                    {'_id': ObjectId(tournament_id)},
                    {'$set': {'current_round': next_round}}
                )
                
                # Return new pairings
                return self.get_round_pairings(tournament_id, next_round)
            else:
                # PostgreSQL implementation
                # Get tournament
                tournament_result = self.db.execute(text("""
                    SELECT status, current_round, structure, structure_config
                    FROM tournaments
                    WHERE id = :tournament_id
                """), {'tournament_id': int(tournament_id)})
                
                row = tournament_result.first()
                if not row:
                    return False
                
                status, current_round, structure, structure_config = row
                
                # Check if tournament is active
                if status != 'active':
                    return False
                
                # Check if all matches in current round are completed
                if current_round > 0:
                    if not self._is_round_completed_sql(int(tournament_id), current_round):
                        return False
                
                # Get active players (using standings)
                standings_result = self.db.execute(text("""
                    SELECT player_id
                    FROM standings
                    WHERE tournament_id = :tournament_id AND active = TRUE
                    ORDER BY match_points DESC,
                             opponents_match_win_percentage DESC,
                             game_win_percentage DESC,
                             opponents_game_win_percentage DESC
                """), {'tournament_id': int(tournament_id)})
                
                player_ids = [str(row[0]) for row in standings_result]
                
                if not player_ids:
                    return False
                
                # Get previous matches
                matches_result = self.db.execute(text("""
                    SELECT id, player1_id, player2_id, result, status
                    FROM matches
                    WHERE tournament_id = :tournament_id
                """), {'tournament_id': int(tournament_id)})
                
                previous_matches = [dict(row._mapping) for row in matches_result]
                
                # Extract structure config
                if structure_config:
                    structure_config = json.loads(structure_config)
                else:
                    structure_config = {}
                
                # Create pairings using Swiss algorithm
                next_round = current_round + 1
                
                if structure.lower() == 'swiss':
                    # Use Swiss pairing algorithm
                    use_seeds = structure_config.get('use_seeds_for_byes', False)
                    pairings = self.swiss_pairing.create_pairings(player_ids, previous_matches, use_seeds)
                    
                    # Create matches from pairings
                    for i, pairing in enumerate(pairings):
                        player1_id = int(pairing[0])
                        player2_id = int(pairing[1]) if len(pairing) > 1 else None
                        
                        # Prepare match data
                        if player2_id:
                            # Regular match
                            self.db.execute(text("""
                                INSERT INTO matches (
                                    tournament_id, round, table_number,
                                    player1_id, player2_id,
                                    player1_wins, player2_wins, draws,
                                    status
                                ) VALUES (
                                    :tournament_id, :round, :table_number,
                                    :player1_id, :player2_id,
                                    0, 0, 0,
                                    'pending'
                                )
                            """), {
                                'tournament_id': int(tournament_id),
                                'round': next_round,
                                'table_number': i + 1,
                                'player1_id': player1_id,
                                'player2_id': player2_id
                            })
                        else:
                            # Bye match
                            self.db.execute(text("""
                                INSERT INTO matches (
                                    tournament_id, round, table_number,
                                    player1_id, player2_id,
                                    player1_wins, player2_wins, draws,
                                    status, result
                                ) VALUES (
                                    :tournament_id, :round, :table_number,
                                    :player1_id, NULL,
                                    2, 0, 0,
                                    'completed', 'win'
                                )
                            """), {
                                'tournament_id': int(tournament_id),
                                'round': next_round,
                                'table_number': i + 1,
                                'player1_id': player1_id
                            })
                            
                            # Update standings for player with bye
                            self.db.execute(text("""
                                UPDATE standings
                                SET matches_played = matches_played + 1,
                                    match_points = match_points + 3,
                                    game_points = game_points + 2
                                WHERE tournament_id = :tournament_id AND player_id = :player_id
                            """), {
                                'tournament_id': int(tournament_id),
                                'player_id': player1_id
                            })
                else:
                    # TODO: Implement other tournament structures (single/double elimination)
                    pass
                
                # Update tournament round
                self.db.execute(text("""
                    UPDATE tournaments
                    SET current_round = :next_round
                    WHERE id = :tournament_id
                """), {
                    'tournament_id': int(tournament_id),
                    'next_round': next_round
                })
                
                self.db.commit()
                
                # Return new pairings
                return self.get_round_pairings(tournament_id, next_round)
        except Exception as e:
            print(f"Error creating next round: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return []
    
    def get_standings(self, tournament_id):
        """Get standings for a tournament."""
        try:
            if self.db_type == 'mongodb':
                # Get standings
                standings = list(self.db.standings.find({
                    'tournament_id': tournament_id
                }).sort([
                    ('match_points', -1),
                    ('opponents_match_win_percentage', -1),
                    ('game_win_percentage', -1),
                    ('opponents_game_win_percentage', -1)
                ]))
                
                # Add player names
                for i, standing in enumerate(standings):
                    player = self.db.players.find_one({'_id': ObjectId(standing['player_id'])})
                    standing['player_name'] = player['name'] if player else 'Unknown'
                    
                    # Add rank if not present
                    if 'rank' not in standing or standing['rank'] == 0:
                        standing['rank'] = i + 1
                    
                    # Add MongoDB ID
                    standing['id'] = str(standing.pop('_id'))
                
                return standings
            else:
                # PostgreSQL implementation
                # Update rankings first to ensure they're current
                self.db.execute(text("""
                    WITH ranked_standings AS (
                        SELECT 
                            id,
                            ROW_NUMBER() OVER (
                                ORDER BY 
                                    match_points DESC,
                                    opponents_match_win_percentage DESC,
                                    game_win_percentage DESC,
                                    opponents_game_win_percentage DESC
                            ) as rank_num
                        FROM standings
                        WHERE tournament_id = :tournament_id
                    )
                    UPDATE standings
                    SET rank = rs.rank_num
                    FROM ranked_standings rs
                    WHERE standings.id = rs.id
                """), {'tournament_id': int(tournament_id)})
                
                self.db.commit()
                
                # Get standings with player names
                result = self.db.execute(text("""
                    SELECT s.*, p.name as player_name
                    FROM standings s
                    JOIN players p ON s.player_id = p.id
                    WHERE s.tournament_id = :tournament_id
                    ORDER BY s.rank
                """), {'tournament_id': int(tournament_id)})
                
                standings = []
                for row in result.mappings():
                    standing = dict(row)
                    standing['id'] = str(standing['id'])
                    standing['player_id'] = str(standing['player_id'])
                    standing['tournament_id'] = str(standing['tournament_id'])
                    standings.append(standing)
                
                return standings
        except Exception as e:
            print(f"Error getting standings: {e}")
            return []
    
    def update_standings(self, tournament_id, standings_data):
        """Update standings manually."""
        try:
            if self.db_type == 'mongodb':
                for standing_data in standings_data:
                    standing_id = standing_data.pop('id', None)
                    if not standing_id:
                        continue
                    
                    # Update standing
                    self.db.standings.update_one(
                        {'_id': ObjectId(standing_id)},
                        {'$set': standing_data}
                    )
                
                return True
            else:
                # PostgreSQL implementation
                for standing_data in standings_data:
                    standing_id = standing_data.pop('id', None)
                    if not standing_id:
                        continue
                    
                    # Build set clause
                    set_clauses = []
                    params = {'standing_id': int(standing_id)}
                    
                    for key, value in standing_data.items():
                        if key not in ['tournament_id', 'player_id']:  # Don't update these
                            set_clauses.append(f"{key} = :{key}")
                            params[key] = value
                    
                    if not set_clauses:
                        continue
                    
                    query = f"""
                        UPDATE standings
                        SET {', '.join(set_clauses)}
                        WHERE id = :standing_id
                    """
                    
                    self.db.execute(text(query), params)
                
                self.db.commit()
                return True
        except Exception as e:
            print(f"Error updating standings: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False
    
    def start_tournament(self, tournament_id):
        """Start a tournament."""
        try:
            if self.db_type == 'mongodb':
                # Check if tournament exists and is in planned state
                tournament = self.db.tournaments.find_one({
                    '_id': ObjectId(tournament_id),
                    'status': 'planned'
                })
                
                if not tournament:
                    return False
                
                # Check if there are at least 2 players
                players = tournament.get('players', [])
                if len(players) < 2:
                    return False
                
                # Determine rounds based on number of players if not set
                rounds = tournament.get('rounds', 0)
                if rounds == 0:
                    rounds = self._calculate_rounds(len(players))
                
                # Update tournament
                self.db.tournaments.update_one(
                    {'_id': ObjectId(tournament_id)},
                    {'$set': {
                        'status': 'active',
                        'rounds': rounds,
                        'current_round': 0
                    }}
                )
                
                # Create initial standings for all players
                for player_id in players:
                    existing = self.db.standings.find_one({
                        'tournament_id': tournament_id,
                        'player_id': player_id
                    })
                    
                    if not existing:
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
                            'rank': 0,
                            'active': True
                        })
                
                return True
            else:
                # PostgreSQL implementation
                # Check if tournament exists and is in planned state
                tournament_result = self.db.execute(text("""
                    SELECT t.id,
                           (SELECT COUNT(*) FROM tournament_players WHERE tournament_id = t.id) as player_count
                    FROM tournaments t
                    WHERE t.id = :tournament_id AND t.status = 'planned'
                """), {'tournament_id': int(tournament_id)})
                
                row = tournament_result.first()
                if not row:
                    return False
                
                player_count = row[1]
                
                # Check if there are at least 2 players
                if player_count < 2:
                    return False
                
                # Get tournament rounds
                rounds_result = self.db.execute(text("""
                    SELECT rounds FROM tournaments WHERE id = :tournament_id
                """), {'tournament_id': int(tournament_id)})
                
                rounds = rounds_result.scalar()
                
                # Determine rounds based on number of players if not set
                if rounds == 0:
                    rounds = self._calculate_rounds(player_count)
                
                # Update tournament
                self.db.execute(text("""
                    UPDATE tournaments
                    SET status = 'active',
                        rounds = :rounds,
                        current_round = 0
                    WHERE id = :tournament_id
                """), {
                    'tournament_id': int(tournament_id),
                    'rounds': rounds
                })
                
                # Create initial standings for all players
                self.db.execute(text("""
                    INSERT INTO standings (
                        tournament_id, player_id, matches_played, match_points,
                        game_points, match_win_percentage, game_win_percentage,
                        opponents_match_win_percentage, opponents_game_win_percentage,
                        rank, active
                    )
                    SELECT 
                        :tournament_id, player_id, 0, 0, 
                        0, 0.0, 0.0, 
                        0.0, 0.0, 
                        0, TRUE
                    FROM tournament_players
                    WHERE tournament_id = :tournament_id
                    AND NOT EXISTS (
                        SELECT 1 FROM standings 
                        WHERE tournament_id = :tournament_id 
                        AND player_id = tournament_players.player_id
                    )
                """), {'tournament_id': int(tournament_id)})
                
                self.db.commit()
                return True
        except Exception as e:
            print(f"Error starting tournament: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False
    
    def _calculate_rounds(self, player_count):
        """Calculate recommended number of rounds based on player count."""
        if player_count <= 8:
            return 3
        elif player_count <= 16:
            return 4
        elif player_count <= 32:
            return 5
        elif player_count <= 64:
            return 6
        elif player_count <= 128:
            return 7
        else:
            return 8
    
    def end_tournament(self, tournament_id):
        """End a tournament."""
        try:
            if self.db_type == 'mongodb':
                # Check if tournament exists and is active
                tournament = self.db.tournaments.find_one({
                    '_id': ObjectId(tournament_id),
                    'status': 'active'
                })
                
                if not tournament:
                    return False
                
                # Update tournament
                self.db.tournaments.update_one(
                    {'_id': ObjectId(tournament_id)},
                    {'$set': {'status': 'completed'}}
                )
                
                return True
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    UPDATE tournaments
                    SET status = 'completed'
                    WHERE id = :tournament_id AND status = 'active'
                """), {'tournament_id': int(tournament_id)})
                
                self.db.commit()
                return result.rowcount > 0
        except Exception as e:
            print(f"Error ending tournament: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False