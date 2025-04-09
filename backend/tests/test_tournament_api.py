import pytest
import json
from app.services.tournament_service import TournamentService
from app.services.player_service import PlayerService

class TestTournamentAPI:
    """Test cases for the Tournament API endpoints."""
    
    def test_get_all_tournaments(self, client, app):
        """Test GET /api/tournaments endpoint."""
        with app.app_context():
            tournament_service = TournamentService()
            
            # Create test tournaments
            tournament_data_list = [
                {
                    'name': 'API Test Tournament 1',
                    'format': 'Standard',
                    'date': '2025-04-15',
                    'location': 'API Test Location 1',
                    'status': 'planned'
                },
                {
                    'name': 'API Test Tournament 2',
                    'format': 'Modern',
                    'date': '2025-04-20',
                    'location': 'API Test Location 2',
                    'status': 'active'
                }
            ]
            
            for tournament_data in tournament_data_list:
                tournament_service.create_tournament(tournament_data)
            
            # Make request to the API
            response = client.get('/api/tournaments')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'tournaments' in data
            assert len(data['tournaments']) >= 2
    
    def test_get_tournament_by_id(self, client, app):
        """Test GET /api/tournaments/<id> endpoint."""
        with app.app_context():
            tournament_service = TournamentService()
            
            # Create a test tournament
            tournament_data = {
                'name': 'API Get Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Get Location',
                'status': 'planned'
            }
            
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Make request to the API
            response = client.get(f'/api/tournaments/{tournament_id}')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['id'] == tournament_id
            assert data['name'] == 'API Get Tournament'
            assert data['format'] == 'Standard'
    
    def test_create_tournament(self, client):
        """Test POST /api/tournaments endpoint."""
        # Prepare tournament data
        tournament_data = {
            'name': 'API Create Tournament',
            'format': 'Standard',
            'date': '2025-04-15',
            'location': 'API Create Location',
            'rounds': 4,
            'time_limit': 50,
            'allow_intentional_draws': True,
            'tiebreakers': {
                'match_points': True,
                'opponents_match_win_percentage': True,
                'game_win_percentage': True,
                'opponents_game_win_percentage': True
            },
            'status': 'planned'
        }
        
        # Make request to the API
        response = client.post(
            '/api/tournaments',
            data=json.dumps(tournament_data),
            content_type='application/json'
        )
        
        # Verify response
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'id' in data
        assert data['message'] == 'Tournament created successfully'
    
    def test_update_tournament(self, client, app):
        """Test PUT /api/tournaments/<id> endpoint."""
        with app.app_context():
            tournament_service = TournamentService()
            
            # Create a test tournament
            tournament_data = {
                'name': 'API Update Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Update Location',
                'status': 'planned'
            }
            
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Prepare update data
            update_data = {
                'name': 'API Updated Tournament',
                'location': 'API Updated Location'
            }
            
            # Make request to the API
            response = client.put(
                f'/api/tournaments/{tournament_id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Tournament updated successfully'
            
            # Verify tournament was updated
            updated_tournament = tournament_service.get_tournament_by_id(tournament_id)
            assert updated_tournament['name'] == 'API Updated Tournament'
            assert updated_tournament['location'] == 'API Updated Location'
    
    def test_tournament_lifecycle_endpoints(self, client, app):
        """Test tournament lifecycle endpoints (start, next round, end)."""
        with app.app_context():
            tournament_service = TournamentService()
            
            # Create a test tournament
            tournament_data = {
                'name': 'API Lifecycle Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Lifecycle Location',
                'rounds': 3,
                'status': 'planned'
            }
            
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Test start tournament endpoint
            response = client.post(f'/api/tournaments/{tournament_id}/start')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Tournament started successfully'
            
            # Verify tournament status is now active
            tournament = tournament_service.get_tournament_by_id(tournament_id)
            assert tournament['status'] == 'active'
            assert tournament['current_round'] == 1
            
            # Test next round endpoint
            response = client.post(f'/api/tournaments/{tournament_id}/next-round')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Next round started successfully'
            
            # Verify current round is updated
            tournament = tournament_service.get_tournament_by_id(tournament_id)
            assert tournament['current_round'] == 2
            
            # Test end tournament endpoint
            response = client.post(f'/api/tournaments/{tournament_id}/end')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Tournament ended successfully'
            
            # Verify tournament status is now completed
            tournament = tournament_service.get_tournament_by_id(tournament_id)
            assert tournament['status'] == 'completed'
    
    def test_tournament_players_endpoints(self, client, app):
        """Test tournament player registration endpoints."""
        with app.app_context():
            tournament_service = TournamentService()
            player_service = PlayerService()
            
            # Create a test tournament
            tournament_data = {
                'name': 'API Players Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Players Location',
                'status': 'planned'
            }
            
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Create a test player
            player_data = {
                'name': 'API Tournament Player',
                'email': 'apitournamentplayer@example.com',
                'active': True
            }
            
            player_id = player_service.create_player(player_data)
            
            # Test get tournament players endpoint (empty)
            response = client.get(f'/api/tournaments/{tournament_id}/players')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'players' in data
            assert len(data['players']) == 0
            
            # Test register player endpoint
            response = client.post(
                f'/api/tournaments/{tournament_id}/players',
                data=json.dumps({'player_id': player_id}),
                content_type='application/json'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Player registered successfully'
            
            # Test get tournament players endpoint (with player)
            response = client.get(f'/api/tournaments/{tournament_id}/players')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'players' in data
            assert len(data['players']) == 1
            assert data['players'][0]['id'] == player_id
            
            # Test drop player endpoint
            response = client.delete(f'/api/tournaments/{tournament_id}/players/{player_id}')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Player dropped successfully'
            
            # Verify player is dropped but still in the tournament with inactive status
            response = client.get(f'/api/tournaments/{tournament_id}/players')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'players' in data
            assert len(data['players']) == 1
            assert data['players'][0]['id'] == player_id
            assert data['players'][0]['active'] is False
    
    def test_tournament_pairings_endpoint(self, client, app):
        """Test tournament pairings endpoint."""
        with app.app_context():
            # This would require setting up players and starting the tournament
            # For simplicity, we'll just test the endpoint exists and returns a 200
            tournament_service = TournamentService()
            
            # Create a test tournament
            tournament_data = {
                'name': 'API Pairings Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Pairings Location',
                'status': 'active',
                'current_round': 1
            }
            
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Make request to the API
            response = client.get(f'/api/tournaments/{tournament_id}/pairings')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'pairings' in data
    
    def test_tournament_standings_endpoint(self, client, app):
        """Test tournament standings endpoint."""
        with app.app_context():
            # This would require setting up players and matches
            # For simplicity, we'll just test the endpoint exists and returns a 200
            tournament_service = TournamentService()
            
            # Create a test tournament
            tournament_data = {
                'name': 'API Standings Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Standings Location',
                'status': 'active',
                'current_round': 1
            }
            
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Make request to the API
            response = client.get(f'/api/tournaments/{tournament_id}/standings')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'standings' in data
