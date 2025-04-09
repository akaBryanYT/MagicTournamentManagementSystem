import pytest
from app.services.match_service import MatchService
from app.services.tournament_service import TournamentService
from app.services.player_service import PlayerService

class TestMatchService:
    """Test cases for the MatchService class."""
    
    def test_create_match(self, app):
        """Test creating a new match."""
        with app.app_context():
            match_service = MatchService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test players
            player1_data = {
                'name': 'Match Test Player 1',
                'email': 'matchtest1@example.com',
                'active': True
            }
            player1_id = player_service.create_player(player1_data)
            
            player2_data = {
                'name': 'Match Test Player 2',
                'email': 'matchtest2@example.com',
                'active': True
            }
            player2_id = player_service.create_player(player2_data)
            
            # Create a test tournament
            tournament_data = {
                'name': 'Match Test Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Test Location',
                'status': 'active',
                'current_round': 1
            }
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Create a test match
            match_data = {
                'tournament_id': tournament_id,
                'round': 1,
                'table_number': 1,
                'player1_id': player1_id,
                'player2_id': player2_id,
                'status': 'pending'
            }
            
            match_id = match_service.create_match(match_data)
            
            # Verify match was created
            assert match_id is not None
            
            # Retrieve the match and verify data
            match = match_service.get_match_by_id(match_id)
            assert match is not None
            assert match['tournament_id'] == tournament_id
            assert match['round'] == 1
            assert match['table_number'] == 1
            assert match['player1_id'] == player1_id
            assert match['player2_id'] == player2_id
            assert match['status'] == 'pending'
    
    def test_submit_match_result(self, app):
        """Test submitting a match result."""
        with app.app_context():
            match_service = MatchService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test players
            player1_id = player_service.create_player({
                'name': 'Result Test Player 1',
                'email': 'resulttest1@example.com',
                'active': True
            })
            
            player2_id = player_service.create_player({
                'name': 'Result Test Player 2',
                'email': 'resulttest2@example.com',
                'active': True
            })
            
            # Create a test tournament
            tournament_id = tournament_service.create_tournament({
                'name': 'Result Test Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Test Location',
                'status': 'active',
                'current_round': 1
            })
            
            # Create a test match
            match_data = {
                'tournament_id': tournament_id,
                'round': 1,
                'table_number': 1,
                'player1_id': player1_id,
                'player2_id': player2_id,
                'status': 'in_progress'
            }
            
            match_id = match_service.create_match(match_data)
            
            # Submit a match result (player 1 wins 2-1)
            result_data = {
                'player1_wins': 2,
                'player2_wins': 1,
                'draws': 0
            }
            
            success = match_service.submit_result(match_id, result_data)
            
            # Verify result submission was successful
            assert success is True
            
            # Retrieve the match and verify result was recorded
            match = match_service.get_match_by_id(match_id)
            assert match['player1_wins'] == 2
            assert match['player2_wins'] == 1
            assert match['draws'] == 0
            assert match['result'] == 'win'  # Player 1 won
            assert match['status'] == 'completed'
    
    def test_submit_intentional_draw(self, app):
        """Test submitting an intentional draw."""
        with app.app_context():
            match_service = MatchService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test players
            player1_id = player_service.create_player({
                'name': 'Draw Test Player 1',
                'email': 'drawtest1@example.com',
                'active': True
            })
            
            player2_id = player_service.create_player({
                'name': 'Draw Test Player 2',
                'email': 'drawtest2@example.com',
                'active': True
            })
            
            # Create a test tournament with intentional draws allowed
            tournament_id = tournament_service.create_tournament({
                'name': 'Draw Test Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Test Location',
                'status': 'active',
                'current_round': 1,
                'allow_intentional_draws': True
            })
            
            # Create a test match
            match_data = {
                'tournament_id': tournament_id,
                'round': 1,
                'table_number': 1,
                'player1_id': player1_id,
                'player2_id': player2_id,
                'status': 'in_progress'
            }
            
            match_id = match_service.create_match(match_data)
            
            # Submit an intentional draw
            success = match_service.submit_intentional_draw(match_id)
            
            # Verify draw submission was successful
            assert success is True
            
            # Retrieve the match and verify draw was recorded
            match = match_service.get_match_by_id(match_id)
            assert match['player1_wins'] == 0
            assert match['player2_wins'] == 0
            assert match['draws'] == 1
            assert match['result'] == 'draw'
            assert match['status'] == 'completed'
    
    def test_get_tournament_round_matches(self, app):
        """Test retrieving all matches for a tournament round."""
        with app.app_context():
            match_service = MatchService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test players
            player_ids = []
            for i in range(4):
                player_id = player_service.create_player({
                    'name': f'Round Test Player {i+1}',
                    'email': f'roundtest{i+1}@example.com',
                    'active': True
                })
                player_ids.append(player_id)
            
            # Create a test tournament
            tournament_id = tournament_service.create_tournament({
                'name': 'Round Test Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Test Location',
                'status': 'active',
                'current_round': 1
            })
            
            # Create multiple matches for the tournament
            match_data_list = [
                {
                    'tournament_id': tournament_id,
                    'round': 1,
                    'table_number': 1,
                    'player1_id': player_ids[0],
                    'player2_id': player_ids[1],
                    'status': 'completed',
                    'player1_wins': 2,
                    'player2_wins': 0,
                    'draws': 0,
                    'result': 'win'
                },
                {
                    'tournament_id': tournament_id,
                    'round': 1,
                    'table_number': 2,
                    'player1_id': player_ids[2],
                    'player2_id': player_ids[3],
                    'status': 'in_progress'
                }
            ]
            
            for match_data in match_data_list:
                match_service.create_match(match_data)
            
            # Retrieve all matches for round 1
            round_matches = match_service.get_tournament_round_matches(tournament_id, 1)
            
            # Verify matches were retrieved
            assert len(round_matches) == 2
            assert round_matches[0]['tournament_id'] == tournament_id
            assert round_matches[0]['round'] == 1
            assert round_matches[1]['tournament_id'] == tournament_id
            assert round_matches[1]['round'] == 1
    
    def test_get_player_matches(self, app):
        """Test retrieving all matches for a player."""
        with app.app_context():
            match_service = MatchService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test players
            player1_id = player_service.create_player({
                'name': 'History Test Player 1',
                'email': 'historytest1@example.com',
                'active': True
            })
            
            player2_id = player_service.create_player({
                'name': 'History Test Player 2',
                'email': 'historytest2@example.com',
                'active': True
            })
            
            # Create test tournaments
            tournament1_id = tournament_service.create_tournament({
                'name': 'History Test Tournament 1',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Test Location',
                'status': 'active',
                'current_round': 2
            })
            
            tournament2_id = tournament_service.create_tournament({
                'name': 'History Test Tournament 2',
                'format': 'Modern',
                'date': '2025-04-20',
                'location': 'Test Location',
                'status': 'active',
                'current_round': 1
            })
            
            # Create multiple matches for player 1
            match_data_list = [
                {
                    'tournament_id': tournament1_id,
                    'round': 1,
                    'table_number': 1,
                    'player1_id': player1_id,
                    'player2_id': player2_id,
                    'status': 'completed',
                    'player1_wins': 2,
                    'player2_wins': 0,
                    'draws': 0,
                    'result': 'win'
                },
                {
                    'tournament_id': tournament1_id,
                    'round': 2,
                    'table_number': 1,
                    'player1_id': player1_id,
                    'player2_id': player2_id,
                    'status': 'in_progress'
                },
                {
                    'tournament_id': tournament2_id,
                    'round': 1,
                    'table_number': 1,
                    'player1_id': player2_id,
                    'player2_id': player1_id,
                    'status': 'in_progress'
                }
            ]
            
            for match_data in match_data_list:
                match_service.create_match(match_data)
            
            # Retrieve all matches for player 1
            player_matches = match_service.get_player_matches(player1_id)
            
            # Verify matches were retrieved
            assert len(player_matches) == 3
            
            # Retrieve matches for player 1 in tournament 1
            tournament_matches = match_service.get_player_matches(player1_id, tournament1_id)
            
            # Verify filtered matches were retrieved
            assert len(tournament_matches) == 2
            assert tournament_matches[0]['tournament_id'] == tournament1_id
            assert tournament_matches[1]['tournament_id'] == tournament1_id
