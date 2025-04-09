import pytest
import json
from app.services.deck_service import DeckService
from app.services.player_service import PlayerService
from app.services.tournament_service import TournamentService

class TestDeckAPI:
    """Test cases for the Deck API endpoints."""
    
    def test_get_all_decks(self, client, app):
        """Test GET /api/decks endpoint."""
        with app.app_context():
            deck_service = DeckService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test player and tournament
            player_id = player_service.create_player({
                'name': 'API Deck Test Player',
                'email': 'apidecktest@example.com',
                'active': True
            })
            
            tournament_id = tournament_service.create_tournament({
                'name': 'API Deck Test Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Deck Test Location',
                'status': 'planned'
            })
            
            # Create test decks
            deck_data_list = [
                {
                    'name': 'API Test Deck 1',
                    'format': 'Standard',
                    'player_id': player_id,
                    'tournament_id': tournament_id,
                    'main_deck': [{'name': 'Card', 'quantity': 60}],
                    'sideboard': []
                },
                {
                    'name': 'API Test Deck 2',
                    'format': 'Modern',
                    'player_id': player_id,
                    'tournament_id': tournament_id,
                    'main_deck': [{'name': 'Card', 'quantity': 60}],
                    'sideboard': []
                }
            ]
            
            for deck_data in deck_data_list:
                deck_service.create_deck(deck_data)
            
            # Make request to the API
            response = client.get('/api/decks')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'decks' in data
            assert len(data['decks']) >= 2
    
    def test_get_deck_by_id(self, client, app):
        """Test GET /api/decks/<id> endpoint."""
        with app.app_context():
            deck_service = DeckService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test player and tournament
            player_id = player_service.create_player({
                'name': 'API Get Deck Player',
                'email': 'apigetdeck@example.com',
                'active': True
            })
            
            tournament_id = tournament_service.create_tournament({
                'name': 'API Get Deck Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Get Deck Location',
                'status': 'planned'
            })
            
            # Create a test deck
            deck_data = {
                'name': 'API Get Deck',
                'format': 'Standard',
                'player_id': player_id,
                'tournament_id': tournament_id,
                'main_deck': [
                    {'name': 'Mountain', 'quantity': 20},
                    {'name': 'Lightning Bolt', 'quantity': 4}
                ],
                'sideboard': [
                    {'name': 'Smash to Smithereens', 'quantity': 3}
                ]
            }
            
            deck_id = deck_service.create_deck(deck_data)
            
            # Make request to the API
            response = client.get(f'/api/decks/{deck_id}')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['id'] == deck_id
            assert data['name'] == 'API Get Deck'
            assert data['format'] == 'Standard'
            assert len(data['main_deck']) == 2
            assert len(data['sideboard']) == 1
    
    def test_create_deck(self, client, app):
        """Test POST /api/decks endpoint."""
        with app.app_context():
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test player and tournament
            player_id = player_service.create_player({
                'name': 'API Create Deck Player',
                'email': 'apicreatedeck@example.com',
                'active': True
            })
            
            tournament_id = tournament_service.create_tournament({
                'name': 'API Create Deck Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Create Deck Location',
                'status': 'planned'
            })
            
            # Prepare deck data
            deck_data = {
                'name': 'API Create Deck',
                'format': 'Standard',
                'player_id': player_id,
                'tournament_id': tournament_id,
                'main_deck': [
                    {'name': 'Mountain', 'quantity': 20},
                    {'name': 'Lightning Bolt', 'quantity': 4}
                ],
                'sideboard': [
                    {'name': 'Smash to Smithereens', 'quantity': 3}
                ]
            }
            
            # Make request to the API
            response = client.post(
                '/api/decks',
                data=json.dumps(deck_data),
                content_type='application/json'
            )
            
            # Verify response
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'id' in data
            assert data['message'] == 'Deck created successfully'
    
    def test_update_deck(self, client, app):
        """Test PUT /api/decks/<id> endpoint."""
        with app.app_context():
            deck_service = DeckService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test player and tournament
            player_id = player_service.create_player({
                'name': 'API Update Deck Player',
                'email': 'apiupdatedeck@example.com',
                'active': True
            })
            
            tournament_id = tournament_service.create_tournament({
                'name': 'API Update Deck Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Update Deck Location',
                'status': 'planned'
            })
            
            # Create a test deck
            deck_data = {
                'name': 'API Update Deck',
                'format': 'Standard',
                'player_id': player_id,
                'tournament_id': tournament_id,
                'main_deck': [
                    {'name': 'Mountain', 'quantity': 20},
                    {'name': 'Lightning Bolt', 'quantity': 4}
                ],
                'sideboard': []
            }
            
            deck_id = deck_service.create_deck(deck_data)
            
            # Prepare update data
            update_data = {
                'name': 'API Updated Deck',
                'main_deck': [
                    {'name': 'Mountain', 'quantity': 18},
                    {'name': 'Lightning Bolt', 'quantity': 4},
                    {'name': 'Shock', 'quantity': 2}
                ]
            }
            
            # Make request to the API
            response = client.put(
                f'/api/decks/{deck_id}',
                data=json.dumps(update_data),
                content_type='application/json'
            )
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Deck updated successfully'
            
            # Verify deck was updated
            updated_deck = deck_service.get_deck_by_id(deck_id)
            assert updated_deck['name'] == 'API Updated Deck'
            assert len(updated_deck['main_deck']) == 3
    
    def test_validate_deck(self, client, app):
        """Test POST /api/decks/<id>/validate endpoint."""
        with app.app_context():
            deck_service = DeckService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test player and tournament
            player_id = player_service.create_player({
                'name': 'API Validate Deck Player',
                'email': 'apivalidatedeck@example.com',
                'active': True
            })
            
            tournament_id = tournament_service.create_tournament({
                'name': 'API Validate Deck Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Validate Deck Location',
                'status': 'planned'
            })
            
            # Create a test deck (valid Standard deck)
            deck_data = {
                'name': 'API Validate Deck',
                'format': 'Standard',
                'player_id': player_id,
                'tournament_id': tournament_id,
                'main_deck': [{'name': 'Card', 'quantity': 60}],
                'sideboard': [{'name': 'Sideboard Card', 'quantity': 15}]
            }
            
            deck_id = deck_service.create_deck(deck_data)
            
            # Make request to the API
            response = client.post(f'/api/decks/{deck_id}/validate')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['valid'] is True
            assert 'errors' in data
    
    def test_import_deck(self, client, app):
        """Test POST /api/decks/import endpoint."""
        with app.app_context():
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test player and tournament
            player_id = player_service.create_player({
                'name': 'API Import Deck Player',
                'email': 'apiimportdeck@example.com',
                'active': True
            })
            
            tournament_id = tournament_service.create_tournament({
                'name': 'API Import Deck Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Import Deck Location',
                'status': 'planned'
            })
            
            # Prepare import data
            import_data = {
                'name': 'API Imported Deck',
                'format': 'Standard',
                'player_id': player_id,
                'tournament_id': tournament_id,
                'deck_text': """
                // Main Deck
                20 Mountain
                4 Lightning Bolt
                
                // Sideboard
                3 Smash to Smithereens
                """
            }
            
            # Make request to the API
            response = client.post(
                '/api/decks/import',
                data=json.dumps(import_data),
                content_type='application/json'
            )
            
            # Verify response
            assert response.status_code == 201
            data = json.loads(response.data)
            assert 'id' in data
            assert data['message'] == 'Deck imported successfully'
    
    def test_export_deck(self, client, app):
        """Test GET /api/decks/<id>/export endpoint."""
        with app.app_context():
            deck_service = DeckService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create test player and tournament
            player_id = player_service.create_player({
                'name': 'API Export Deck Player',
                'email': 'apiexportdeck@example.com',
                'active': True
            })
            
            tournament_id = tournament_service.create_tournament({
                'name': 'API Export Deck Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'API Export Deck Location',
                'status': 'planned'
            })
            
            # Create a test deck
            deck_data = {
                'name': 'API Export Deck',
                'format': 'Standard',
                'player_id': player_id,
                'tournament_id': tournament_id,
                'main_deck': [
                    {'name': 'Mountain', 'quantity': 20},
                    {'name': 'Lightning Bolt', 'quantity': 4}
                ],
                'sideboard': [
                    {'name': 'Smash to Smithereens', 'quantity': 3}
                ]
            }
            
            deck_id = deck_service.create_deck(deck_data)
            
            # Make request to the API
            response = client.get(f'/api/decks/{deck_id}/export')
            
            # Verify response
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'deck_text' in data
            assert '20 Mountain' in data['deck_text']
            assert '4 Lightning Bolt' in data['deck_text']
            assert '// Sideboard' in data['deck_text']
            assert '3 Smash to Smithereens' in data['deck_text']
