"""
Match service for the Tournament Management System.
"""

from datetime import datetime
from bson.objectid import ObjectId
from app.models.database import DatabaseConfig
from sqlalchemy import text
import json

class MatchService:
    """Service for match operations."""
    
    def __init__(self):
        """Initialize the match service."""
        self.db_config = DatabaseConfig()
        self.db_config.connect()
        self.db = self.db_config.db
        self.db_type = self.db_config.db_type
    
    def get_all_matches(self):
        """Get all matches."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT id, tournament_id, round, table_number, 
                           player1_id, player2_id, status, result
                    FROM matches
                """))
                
                matches = []
                for row in result.mappings():
                    match = dict(row)
                    match['id'] = str(match['id'])
                    match['tournament_id'] = str(match['tournament_id'])
                    match['player1_id'] = str(match['player1_id'])
                    if match['player2_id']:
                        match['player2_id'] = str(match['player2_id'])
                    matches.append(match)
                
                return matches
        except Exception as e:
            print(f"Error getting matches: {e}")
            return []
    
    def get_matches_by_tournament(self, tournament_id):
        """Get matches for a tournament."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT id, round, table_number, player1_id, player2_id, status, result
                    FROM matches
                    WHERE tournament_id = :tournament_id
                """), {'tournament_id': int(tournament_id)})
                
                matches = []
                for row in result.mappings():
                    match = dict(row)
                    match['id'] = str(match['id'])
                    match['tournament_id'] = tournament_id
                    match['player1_id'] = str(match['player1_id'])
                    if match['player2_id']:
                        match['player2_id'] = str(match['player2_id'])
                    matches.append(match)
                
                return matches
        except Exception as e:
            print(f"Error getting matches by tournament: {e}")
            return []
    
    def get_matches_by_tournament_and_round(self, tournament_id, round_number):
        """Get matches for a tournament and round."""
        try:
            if self.db_type == 'mongodb':
                matches = list(self.db.matches.find({
                    'tournament_id': tournament_id,
                    'round': int(round_number)
                }))
                
                for match in matches:
                    match['id'] = str(match.pop('_id'))
                
                return matches
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT m.*, 
                           p1.name as player1_name,
                           p2.name as player2_name
                    FROM matches m
                    LEFT JOIN players p1 ON m.player1_id = p1.id
                    LEFT JOIN players p2 ON m.player2_id = p2.id
                    WHERE m.tournament_id = :tournament_id AND m.round = :round_number
                """), {
                    'tournament_id': int(tournament_id),
                    'round_number': int(round_number)
                })
                
                matches = []
                for row in result.mappings():
                    match = dict(row)
                    match['id'] = str(match['id'])
                    match['tournament_id'] = str(match['tournament_id'])
                    match['player1_id'] = str(match['player1_id'])
                    if match['player2_id']:
                        match['player2_id'] = str(match['player2_id'])
                    
                    # Convert dates to ISO format strings
                    if match.get('start_time'):
                        match['start_time'] = match['start_time'].isoformat()
                    if match.get('end_time'):
                        match['end_time'] = match['end_time'].isoformat()
                    
                    matches.append(match)
                
                return matches
        except Exception as e:
            print(f"Error getting matches by tournament and round: {e}")
            return []
    
    def get_match_by_id(self, match_id):
        """Get match by ID."""
        try:
            if self.db_type == 'mongodb':
                match = self.db.matches.find_one({'_id': ObjectId(match_id)})
                if match:
                    match['id'] = str(match.pop('_id'))
                    return match
                return None
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT m.*, 
                           p1.name as player1_name,
                           p2.name as player2_name,
                           t.name as tournament_name
                    FROM matches m
                    LEFT JOIN players p1 ON m.player1_id = p1.id
                    LEFT JOIN players p2 ON m.player2_id = p2.id
                    LEFT JOIN tournaments t ON m.tournament_id = t.id
                    WHERE m.id = :match_id
                """), {'match_id': int(match_id)})
                
                row = result.mappings().first()
                if row:
                    match = dict(row)
                    match['id'] = str(match['id'])
                    match['tournament_id'] = str(match['tournament_id'])
                    match['player1_id'] = str(match['player1_id'])
                    if match['player2_id']:
                        match['player2_id'] = str(match['player2_id'])
                    
                    # Convert dates to ISO format strings
                    if match.get('start_time'):
                        match['start_time'] = match['start_time'].isoformat()
                    if match.get('end_time'):
                        match['end_time'] = match['end_time'].isoformat()
                    
                    return match
                return None
        except Exception as e:
            print(f"Error getting match: {e}")
            return None
    
    def create_match(self, match_data):
        """Create a new match."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                # Validate tournament exists
                tournament_result = self.db.execute(text("""
                    SELECT id FROM tournaments WHERE id = :tournament_id
                """), {'tournament_id': int(match_data['tournament_id'])})
                
                if not tournament_result.first():
                    return None
                
                # Validate players exist
                player1_result = self.db.execute(text("""
                    SELECT id FROM players WHERE id = :player_id
                """), {'player_id': int(match_data['player1_id'])})
                
                if not player1_result.first():
                    return None
                
                player2_id = None
                if 'player2_id' in match_data and match_data['player2_id']:
                    player2_result = self.db.execute(text("""
                        SELECT id FROM players WHERE id = :player_id
                    """), {'player_id': int(match_data['player2_id'])})
                    
                    if not player2_result.first():
                        return None
                    player2_id = int(match_data['player2_id'])
                
                # Set default values
                status = match_data.get('status', 'pending')
                player1_wins = match_data.get('player1_wins', 0)
                player2_wins = match_data.get('player2_wins', 0)
                draws = match_data.get('draws', 0)
                
                # Insert match
                result = self.db.execute(text("""
                    INSERT INTO matches 
                    (tournament_id, round, table_number, player1_id, player2_id, 
                     player1_wins, player2_wins, draws, status, result)
                    VALUES 
                    (:tournament_id, :round, :table_number, :player1_id, :player2_id, 
                     :player1_wins, :player2_wins, :draws, :status, :result)
                    RETURNING id
                """), {
                    'tournament_id': int(match_data['tournament_id']),
                    'round': int(match_data['round']),
                    'table_number': match_data.get('table_number'),
                    'player1_id': int(match_data['player1_id']),
                    'player2_id': player2_id,
                    'player1_wins': player1_wins,
                    'player2_wins': player2_wins,
                    'draws': draws,
                    'status': status,
                    'result': match_data.get('result')
                })
                
                self.db.commit()
                match_id = result.scalar()
                
                return str(match_id)
        except Exception as e:
            print(f"Error creating match: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return None
    
    def update_match(self, match_id, match_data):
        """Update match by ID."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                # Get current match
                match_result = self.db.execute(text("""
                    SELECT status FROM matches WHERE id = :match_id
                """), {'match_id': int(match_id)})
                
                row = match_result.first()
                if not row:
                    return False
                
                # Don't allow updating completed matches
                if row[0] == 'completed' and match_data.get('status') != 'completed':
                    return False
                
                # Build update query
                set_clauses = []
                params = {'match_id': int(match_id)}
                
                for key, value in match_data.items():
                    if key in ['player1_id', 'player2_id', 'tournament_id', 'round', 'table_number']:
                        if value is not None:
                            set_clauses.append(f"{key} = :{key}")
                            params[key] = int(value)
                    else:
                        set_clauses.append(f"{key} = :{key}")
                        params[key] = value
                
                if not set_clauses:
                    return False
                
                query = f"""
                    UPDATE matches
                    SET {', '.join(set_clauses)}
                    WHERE id = :match_id
                """
                
                result = self.db.execute(text(query), params)
                self.db.commit()
                
                return result.rowcount > 0
        except Exception as e:
            print(f"Error updating match: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False
    
    def submit_match_result(self, match_id, player1_wins, player2_wins, draws):
        """Submit result for a match."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                # Get match
                match_result = self.db.execute(text("""
                    SELECT tournament_id, player1_id, player2_id, status
                    FROM matches
                    WHERE id = :match_id
                """), {'match_id': int(match_id)})
                
                row = match_result.first()
                if not row or row[3] == 'completed':
                    return False
                
                tournament_id, player1_id, player2_id, status = row
                
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
                self.db.execute(text("""
                    UPDATE matches
                    SET player1_wins = :player1_wins,
                        player2_wins = :player2_wins,
                        draws = :draws,
                        result = :result,
                        status = 'completed',
                        end_time = CURRENT_TIMESTAMP
                    WHERE id = :match_id
                """), {
                    'match_id': int(match_id),
                    'player1_wins': player1_wins,
                    'player2_wins': player2_wins,
                    'draws': draws,
                    'result': result
                })
                
                # Update standings for player 1
                standing_result = self.db.execute(text("""
                    SELECT id FROM standings
                    WHERE tournament_id = :tournament_id AND player_id = :player_id
                """), {
                    'tournament_id': tournament_id,
                    'player_id': player1_id
                })
                
                row = standing_result.first()
                if row:
                    self.db.execute(text("""
                        UPDATE standings
                        SET matches_played = matches_played + 1,
                            match_points = match_points + :match_points,
                            game_points = game_points + :game_points
                        WHERE id = :id
                    """), {
                        'id': row[0],
                        'match_points': match_points_player1,
                        'game_points': player1_wins
                    })
                else:
                    self.db.execute(text("""
                        INSERT INTO standings
                        (tournament_id, player_id, matches_played, match_points, game_points, active)
                        VALUES
                        (:tournament_id, :player_id, 1, :match_points, :game_points, TRUE)
                    """), {
                        'tournament_id': tournament_id,
                        'player_id': player1_id,
                        'match_points': match_points_player1,
                        'game_points': player1_wins
                    })
                
                # Update standings for player 2 (if not a bye)
                if player2_id:
                    standing_result = self.db.execute(text("""
                        SELECT id FROM standings
                        WHERE tournament_id = :tournament_id AND player_id = :player_id
                    """), {
                        'tournament_id': tournament_id,
                        'player_id': player2_id
                    })
                    
                    row = standing_result.first()
                    if row:
                        self.db.execute(text("""
                            UPDATE standings
                            SET matches_played = matches_played + 1,
                                match_points = match_points + :match_points,
                                game_points = game_points + :game_points
                            WHERE id = :id
                        """), {
                            'id': row[0],
                            'match_points': match_points_player2,
                            'game_points': player2_wins
                        })
                    else:
                        self.db.execute(text("""
                            INSERT INTO standings
                            (tournament_id, player_id, matches_played, match_points, game_points, active)
                            VALUES
                            (:tournament_id, :player_id, 1, :match_points, :game_points, TRUE)
                        """), {
                            'tournament_id': tournament_id,
                            'player_id': player2_id,
                            'match_points': match_points_player2,
                            'game_points': player2_wins
                        })
                
                # Update win percentages for all players in the tournament
                self._update_win_percentages_sql(tournament_id)
                
                self.db.commit()
                return True
        except Exception as e:
            print(f"Error submitting match result: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False
    
    def start_match(self, match_id):
        """Start a match."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                # Get match
                match_result = self.db.execute(text("""
                    SELECT status FROM matches WHERE id = :match_id
                """), {'match_id': int(match_id)})
                
                row = match_result.first()
                if not row or row[0] != 'pending':
                    return False
                
                # Update match
                self.db.execute(text("""
                    UPDATE matches
                    SET status = 'in_progress',
                        start_time = CURRENT_TIMESTAMP
                    WHERE id = :match_id
                """), {'match_id': int(match_id)})
                
                self.db.commit()
                return True
        except Exception as e:
            print(f"Error starting match: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False
    
    def end_match(self, match_id):
        """End a match without submitting result."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                # Get match
                match_result = self.db.execute(text("""
                    SELECT status FROM matches WHERE id = :match_id
                """), {'match_id': int(match_id)})
                
                row = match_result.first()
                if not row or row[0] == 'completed':
                    return False
                
                # Update match
                self.db.execute(text("""
                    UPDATE matches
                    SET status = 'completed',
                        end_time = CURRENT_TIMESTAMP
                    WHERE id = :match_id
                """), {'match_id': int(match_id)})
                
                self.db.commit()
                return True
        except Exception as e:
            print(f"Error ending match: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False
    
    def draw_match(self, match_id):
        """Mark a match as intentional draw."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                # Get match
                match_result = self.db.execute(text("""
                    SELECT tournament_id, player1_id, player2_id, status
                    FROM matches
                    WHERE id = :match_id
                """), {'match_id': int(match_id)})
                
                row = match_result.first()
                if not row or row[3] == 'completed' or not row[2]:
                    return False
                
                tournament_id, player1_id, player2_id, status = row
                
                # Update match
                self.db.execute(text("""
                    UPDATE matches
                    SET player1_wins = 0,
                        player2_wins = 0,
                        draws = 1,
                        result = 'draw',
                        status = 'completed',
                        end_time = CURRENT_TIMESTAMP
                    WHERE id = :match_id
                """), {'match_id': int(match_id)})
                
                # Update standings for both players
                for player_id in [player1_id, player2_id]:
                    standing_result = self.db.execute(text("""
                        SELECT id FROM standings
                        WHERE tournament_id = :tournament_id AND player_id = :player_id
                    """), {
                        'tournament_id': tournament_id,
                        'player_id': player_id
                    })
                    
                    row = standing_result.first()
                    if row:
                        self.db.execute(text("""
                            UPDATE standings
                            SET matches_played = matches_played + 1,
                                match_points = match_points + 1,
                                game_points = game_points + 0
                            WHERE id = :id
                        """), {'id': row[0]})
                    else:
                        self.db.execute(text("""
                            INSERT INTO standings
                            (tournament_id, player_id, matches_played, match_points, game_points, active)
                            VALUES
                            (:tournament_id, :player_id, 1, 1, 0, TRUE)
                        """), {
                            'tournament_id': tournament_id,
                            'player_id': player_id
                        })
                
                # Update win percentages for all players in the tournament
                self._update_win_percentages_sql(tournament_id)
                
                self.db.commit()
                return True
        except Exception as e:
            print(f"Error marking match as draw: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False
    
    def _update_win_percentages(self, tournament_id):
        """Update win percentages for all players in a tournament (MongoDB)."""
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
    
    def _update_win_percentages_sql(self, tournament_id):
        """Update win percentages for all players in a tournament (PostgreSQL)."""
        try:
            # Update match win percentages
            self.db.execute(text("""
                UPDATE standings
                SET match_win_percentage = 
                    CASE 
                        WHEN matches_played > 0 THEN CAST(match_points AS FLOAT) / (matches_played * 3)
                        ELSE 0 
                    END
                WHERE tournament_id = :tournament_id
            """), {'tournament_id': int(tournament_id)})
            
            # Update game win percentages
            # First get all completed matches
            result = self.db.execute(text("""
                SELECT s.id, s.player_id,
                       SUM(CASE WHEN m.player1_id = s.player_id THEN m.player1_wins ELSE m.player2_wins END) as games_won,
                       SUM(m.player1_wins + m.player2_wins + m.draws) as total_games
                FROM standings s
                JOIN matches m ON (m.player1_id = s.player_id OR m.player2_id = s.player_id)
                WHERE s.tournament_id = :tournament_id
                  AND m.tournament_id = :tournament_id
                  AND m.status = 'completed'
                GROUP BY s.id, s.player_id
            """), {'tournament_id': int(tournament_id)})
            
            # Update each player's game win percentage
            for row in result:
                standing_id, player_id, games_won, total_games = row
                
                if total_games > 0:
                    game_win_percentage = games_won / total_games
                    
                    self.db.execute(text("""
                        UPDATE standings
                        SET game_win_percentage = :game_win_percentage
                        WHERE id = :standing_id
                    """), {
                        'standing_id': standing_id,
                        'game_win_percentage': game_win_percentage
                    })
            
            # Calculate opponents' match win percentage
            result = self.db.execute(text("""
                WITH player_opponents AS (
                    SELECT 
                        s.id as standing_id,
                        s.player_id,
                        CASE 
                            WHEN m.player1_id = s.player_id THEN m.player2_id
                            ELSE m.player1_id
                        END as opponent_id
                    FROM standings s
                    JOIN matches m ON (m.player1_id = s.player_id OR m.player2_id = s.player_id)
                    WHERE s.tournament_id = :tournament_id
                      AND m.tournament_id = :tournament_id
                      AND m.status = 'completed'
                      AND m.player1_id IS NOT NULL
                      AND m.player2_id IS NOT NULL
                )
                SELECT 
                    po.standing_id,
                    AVG(s.match_win_percentage) as avg_opponent_match_win,
                    AVG(s.game_win_percentage) as avg_opponent_game_win
                FROM player_opponents po
                JOIN standings s ON s.player_id = po.opponent_id AND s.tournament_id = :tournament_id
                GROUP BY po.standing_id
            """), {'tournament_id': int(tournament_id)})
            
            # Update each player's opponents win percentages
            for row in result:
                standing_id, omw, ogw = row
                
                self.db.execute(text("""
                    UPDATE standings
                    SET opponents_match_win_percentage = :omw,
                        opponents_game_win_percentage = :ogw
                    WHERE id = :standing_id
                """), {
                    'standing_id': standing_id,
                    'omw': omw,
                    'ogw': ogw
                })
            
            # Update standings rankings
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
                      AND active = TRUE
                )
                UPDATE standings
                SET rank = rs.rank_num
                FROM ranked_standings rs
                WHERE standings.id = rs.id
            """), {'tournament_id': int(tournament_id)})
            
            return True
        except Exception as e:
            print(f"Error updating win percentages in SQL: {e}")
            self.db.rollback()
            return False