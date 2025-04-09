import pytest
import json
from app.services.player_service import PlayerService

class TestPlayerAPI:
    """Test cases for the Player API endpoints."""
    
    def test_get_all_players(self, client, app):
        """Test GET /api/players endpoint."""
        with app.app_context():
            player_service = PlayerService()
            
            # Create test players
            player_data_list = [
                {
                    'name': 'API Test Player 1',
                    'email': 'apitest1@example.com',
                    'active': True
                },
                {
                    'name': 'API Test Player 2',
                    'email': 'apitest2@example.com',
                    'active': True
                }
            ]
            
            for player_data in player_data_list:
                player_service.create_player(player_data)
            
            # Make request to the API
            response = client.get('/api/players')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'players' in data
            assert len(data['players']) >= 2
    
    def test_get_player_by_id(self, client, app):
        """Test GET /api/players/<id> endpoint."""
        with app.app_context():
            player_service = PlayerService()
            
            # Create a test player
            player_data = {
                'name': 'API Get Player',
                'email': 'apigetplayer@example.com',
                'active': True
            }
            
            player_id = player_service.create_player(player_data)
            
            # Make request to the API
            response = client.get(f'/api/players/{player_id}')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['id'] == player_id
            assert data['name'] == 'API Get Player'
            assert data['email'] == 'apigetplayer@example.com'
    
    def test_create_player(self, client):
        """Test POST /api/players endpoint."""
        # Prepare player data
        player_data = {
            'name': 'API Create Player',
            'email': 'apicreate@example.com',
            'phone': '555-123-4567',
            'active': True
        }
        
        # Make request to the API
        response = client.post(
            '/api/players',
            data=json.dumps(player_data),
            content_type='application/json'
        )
        
        # Verify response
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'id' in data
        assert data['message'] == 'Player created successfully'
    
    def test_update_player(self, client, app):
        """Test PUT /api/players/<id> endpoint."""
        with app.app_context():
            player_service = PlayerService()
            
            # Create a test player
            player_data = {
                'name': 'API Update Player',
                'email': 'apiupdate@example.com',
                'active': True
            }
            
            player_id = player_service.create_player(player_data)
            
            # Prepare update data
            update_data = {
                'name': 'API Updated Player',
                'email': 'apiupdated@example.com'
            }
            
            # Make request to the API
            response = client.put(
                f'/api/players/{player_id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Player updated successfully'
            
            # Verify player was updated
            updated_player = player_service.get_player_by_id(player_id)
            assert updated_player['name'] == 'API Updated Player'
            assert updated_player['email'] == 'apiupdated@example.com'
    
    def test_delete_player(self, client, app):
        """Test DELETE /api/players/<id> endpoint."""
        with app.app_context():
            player_service = PlayerService()
            
            # Create a test player
            player_data = {
                'name': 'API Delete Player',
                'email': 'apidelete@example.com',
                'active': True
            }
            
            player_id = player_service.create_player(player_data)
            
            # Make request to the API
            response = client.delete(f'/api/players/{player_id}')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Player deleted successfully'
            
            # Verify player was deleted
            deleted_player = player_service.get_player_by_id(player_id)
            assert deleted_player is None
    
    def test_get_player_tournaments(self, client, app):
        """Test GET /api/players/<id>/tournaments endpoint."""
        with app.app_context():
            # This would require setting up tournaments and registering the player
            # For simplicity, we'll just test the endpoint exists and returns a 200
            player_service = PlayerService()
            
            # Create a test player
            player_data = {
                'name': 'API Tournament Player',
                'email': 'apitournament@example.com',
                'active': True
            }
            
            player_id = player_service.create_player(player_data)
            
            # Make request to the API
            response = client.get(f'/api/players/{player_id}/tournaments')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'tournaments' in data
    
    def test_get_player_decks(self, client, app):
        """Test GET /api/players/<id>/decks endpoint."""
        with app.app_context():
            # This would require setting up decks for the player
            # For simplicity, we'll just test the endpoint exists and returns a 200
            player_service = PlayerService()
            
            # Create a test player
            player_data = {
                'name': 'API Deck Player',
                'email': 'apideck@example.com',
                'active': True
            }
            
            player_id = player_service.create_player(player_data)
            
            # Make request to the API
            response = client.get(f'/api/players/{player_id}/decks')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'decks' in data
