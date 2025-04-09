import pytest
import json
from app.services.match_service import MatchService
from app.services.player_service import PlayerService
from app.services.tournament_service import TournamentService

class TestMatchAPI:
    """Test cases for the Match API endpoints."""
    
    def test_get_all_matches(self, client, app):
        """Test GET /api/matches endpoint."""
        with app.app_context():
            match_service = MatchService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test players
            player1_id = player_service.create_player({
                'name': 'API Match Test Player 1',
                'email': 'apimatchtest1@example.com',
                'active': True
            })
            
            player2_id = player_service.create_player({
                'name': 'API Match Test Player 2',
                'email': 'apimatchtest2@example.com',
                'active': True
            })
            
            # Create a test tournament
            tournament_id = tournament_service.create_tournament({
                'name': 'API Match Test Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Match Test Location',
                'status': 'active',
                'current_round': 1
            })
            
            # Create test matches
            match_data_list = [
                {
                    'tournament_id': tournament_id,
                    'round': 1,
                    'table_number': 1,
                    'player1_id': player1_id,
                    'player2_id': player2_id,
                    'status': 'in_progress'
                },
                {
                    'tournament_id': tournament_id,
                    'round': 1,
                    'table_number': 2,
                    'player1_id': player2_id,
                    'player2_id': player1_id,
                    'status': 'pending'
                }
            ]
            
            for match_data in match_data_list:
                match_service.create_match(match_data)
            
            # Make request to the API
            response = client.get('/api/matches')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'matches' in data
            assert len(data['matches']) >= 2
    
    def test_get_match_by_id(self, client, app):
        """Test GET /api/matches/<id> endpoint."""
        with app.app_context():
            match_service = MatchService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test players
            player1_id = player_service.create_player({
                'name': 'API Get Match Player 1',
                'email': 'apigetmatch1@example.com',
                'active': True
            })
            
            player2_id = player_service.create_player({
                'name': 'API Get Match Player 2',
                'email': 'apigetmatch2@example.com',
                'active': True
            })
            
            # Create a test tournament
            tournament_id = tournament_service.create_tournament({
                'name': 'API Get Match Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Get Match Location',
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
            
            # Make request to the API
            response = client.get(f'/api/matches/{match_id}')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['id'] == match_id
            assert data['tournament_id'] == tournament_id
            assert data['player1_id'] == player1_id
            assert data['player2_id'] == player2_id
    
    def test_submit_match_result(self, client, app):
        """Test POST /api/matches/<id>/result endpoint."""
        with app.app_context():
            match_service = MatchService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test players
            player1_id = player_service.create_player({
                'name': 'API Result Match Player 1',
                'email': 'apiresultmatch1@example.com',
                'active': True
            })
            
            player2_id = player_service.create_player({
                'name': 'API Result Match Player 2',
                'email': 'apiresultmatch2@example.com',
                'active': True
            })
            
            # Create a test tournament
            tournament_id = tournament_service.create_tournament({
                'name': 'API Result Match Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Result Match Location',
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
            
            # Prepare result data
            result_data = {
                'player1_wins': 2,
                'player2_wins': 1,
                'draws': 0
            }
            
            # Make request to the API
            response = client.post(
                f'/api/matches/{match_id}/result',
                data=json.dumps(result_data),
                content_type='application/json'
            )
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Match result submitted successfully'
            
            # Verify match result was recorded
            match = match_service.get_match_by_id(match_id)
            assert match['player1_wins'] == 2
            assert match['player2_wins'] == 1
            assert match['draws'] == 0
            assert match['result'] == 'win'  # Player 1 won
            assert match['status'] == 'completed'
    
    def test_submit_intentional_draw(self, client, app):
        """Test POST /api/matches/<id>/intentional-draw endpoint."""
        with app.app_context():
            match_service = MatchService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test players
            player1_id = player_service.create_player({
                'name': 'API Draw Match Player 1',
                'email': 'apidrawmatch1@example.com',
                'active': True
            })
            
            player2_id = player_service.create_player({
                'name': 'API Draw Match Player 2',
                'email': 'apidrawmatch2@example.com',
                'active': True
            })
            
            # Create a test tournament with intentional draws allowed
            tournament_id = tournament_service.create_tournament({
                'name': 'API Draw Match Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Draw Match Location',
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
            
            # Make request to the API
            response = client.post(f'/api/matches/{match_id}/intentional-draw')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Intentional draw submitted successfully'
            
            # Verify draw was recorded
            match = match_service.get_match_by_id(match_id)
            assert match['player1_wins'] == 0
            assert match['player2_wins'] == 0
            assert match['draws'] == 1
            assert match['result'] == 'draw'
            assert match['status'] == 'completed'
    
    def test_get_tournament_round_matches(self, client, app):
        """Test GET /api/tournaments/<id>/rounds/<round>/matches endpoint."""
        with app.app_context():
            match_service = MatchService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test players
            player1_id = player_service.create_player({
                'name': 'API Round Match Player 1',
                'email': 'apiroundmatch1@example.com',
                'active': True
            })
            
            player2_id = player_service.create_player({
                'name': 'API Round Match Player 2',
                'email': 'apiroundmatch2@example.com',
                'active': True
            })
            
            # Create a test tournament
            tournament_id = tournament_service.create_tournament({
                'name': 'API Round Match Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Round Match Location',
                'status': 'active',
                'current_round': 1
            })
            
            # Create test matches for round 1
            match_data_list = [
                {
                    'tournament_id': tournament_id,
                    'round': 1,
                    'table_number': 1,
                    'player1_id': player1_id,
                    'player2_id': player2_id,
                    'status': 'in_progress'
                },
                {
                    'tournament_id': tournament_id,
                    'round': 1,
                    'table_number': 2,
                    'player1_id': player2_id,
                    'player2_id': player1_id,
                    'status': 'pending'
                }
            ]
            
            for match_data in match_data_list:
                match_service.create_match(match_data)
            
            # Make request to the API
            response = client.get(f'/api/tournaments/{tournament_id}/rounds/1/matches')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'matches' in data
            assert len(data['matches']) == 2
    
    def test_get_player_matches(self, client, app):
        """Test GET /api/players/<id>/matches endpoint."""
        with app.app_context():
            match_service = MatchService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test players
            player1_id = player_service.create_player({
                'name': 'API Player Match Player 1',
                'email': 'apiplayermatch1@example.com',
                'active': True
            })
            
            player2_id = player_service.create_player({
                'name': 'API Player Match Player 2',
                'email': 'apiplayermatch2@example.com',
                'active': True
            })
            
            # Create a test tournament
            tournament_id = tournament_service.create_tournament({
                'name': 'API Player Match Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Player Match Location',
                'status': 'active',
                'current_round': 2
            })
            
            # Create multiple matches for player 1
            match_data_list = [
                {
                    'tournament_id': tournament_id,
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
                    'tournament_id': tournament_id,
                    'round': 2,
                    'table_number': 1,
                    'player1_id': player1_id,
                    'player2_id': player2_id,
                    'status': 'in_progress'
                }
            ]
            
            for match_data in match_data_list:
                match_service.create_match(match_data)
            
            # Make request to the API
            response = client.get(f'/api/players/{player1_id}/matches')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'matches' in data
            assert len(data['matches']) == 2
            
            # Test with tournament filter
            response = client.get(f'/api/players/{player1_id}/matches?tournament_id={tournament_id}')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'matches' in data
            assert len(data['matches']) == 2
