import pytest
from app.services.deck_service import DeckService
from app.services.player_service import PlayerService
from app.services.tournament_service import TournamentService

class TestDeckService:
    """Test cases for the DeckService class."""
    
    def test_create_deck(self, app):
        """Test creating a new deck."""
        with app.app_context():
            deck_service = DeckService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create a test player
            player_data = {
                'name': 'Deck Test Player',
                'email': 'decktest@example.com',
                'active': True
            }
            player_id = player_service.create_player(player_data)
            
            # Create a test tournament
            tournament_data = {
                'name': 'Deck Test Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Test Location',
                'status': 'planned'
            }
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Create a test deck
            deck_data = {
                'name': 'Test Mono Red Deck',
                'format': 'Standard',
                'player_id': player_id,
                'tournament_id': tournament_id,
                'main_deck': [
                    {'name': 'Mountain', 'quantity': 20},
                    {'name': 'Lightning Bolt', 'quantity': 4},
                    {'name': 'Goblin Guide', 'quantity': 4},
                    {'name': 'Monastery Swiftspear', 'quantity': 4},
                    {'name': 'Eidolon of the Great Revel', 'quantity': 4},
                    {'name': 'Skewer the Critics', 'quantity': 4}
                ],
                'sideboard': [
                    {'name': 'Smash to Smithereens', 'quantity': 3},
                    {'name': 'Blood Moon', 'quantity': 2}
                ]
            }
            
            deck_id = deck_service.create_deck(deck_data)
            
            # Verify deck was created
            assert deck_id is not None
            
            # Retrieve the deck and verify data
            deck = deck_service.get_deck_by_id(deck_id)
            assert deck is not None
            assert deck['name'] == 'Test Mono Red Deck'
            assert deck['format'] == 'Standard'
            assert deck['player_id'] == player_id
            assert deck['tournament_id'] == tournament_id
            assert len(deck['main_deck']) == 6
            assert len(deck['sideboard']) == 2
    
    def test_validate_standard_deck(self, app):
        """Test validating a Standard format deck."""
        with app.app_context():
            deck_service = DeckService()
            
            # Valid Standard deck (60+ cards main deck, 0-15 sideboard)
            valid_deck = {
                'format': 'Standard',
                'main_deck': [{'name': 'Card', 'quantity': 60}],
                'sideboard': [{'name': 'Sideboard Card', 'quantity': 15}]
            }
            
            # Invalid Standard deck (less than 60 cards main deck)
            invalid_deck_1 = {
                'format': 'Standard',
                'main_deck': [{'name': 'Card', 'quantity': 59}],
                'sideboard': [{'name': 'Sideboard Card', 'quantity': 15}]
            }
            
            # Invalid Standard deck (more than 15 cards sideboard)
            invalid_deck_2 = {
                'format': 'Standard',
                'main_deck': [{'name': 'Card', 'quantity': 60}],
                'sideboard': [{'name': 'Sideboard Card', 'quantity': 16}]
            }
            
            # Test valid deck
            result = deck_service.validate_deck(valid_deck)
            assert result['valid'] is True
            assert len(result['errors']) == 0
            
            # Test invalid decks
            result = deck_service.validate_deck(invalid_deck_1)
            assert result['valid'] is False
            assert len(result['errors']) > 0
            
            result = deck_service.validate_deck(invalid_deck_2)
            assert result['valid'] is False
            assert len(result['errors']) > 0
    
    def test_validate_commander_deck(self, app):
        """Test validating a Commander format deck."""
        with app.app_context():
            deck_service = DeckService()
            
            # Valid Commander deck (100 cards including commander, no sideboard)
            valid_deck = {
                'format': 'Commander',
                'main_deck': [
                    {'name': 'Commander Card', 'quantity': 1},
                    {'name': 'Other Card', 'quantity': 99}
                ],
                'sideboard': []
            }
            
            # Invalid Commander deck (less than 100 cards)
            invalid_deck_1 = {
                'format': 'Commander',
                'main_deck': [
                    {'name': 'Commander Card', 'quantity': 1},
                    {'name': 'Other Card', 'quantity': 98}
                ],
                'sideboard': []
            }
            
            # Invalid Commander deck (has sideboard)
            invalid_deck_2 = {
                'format': 'Commander',
                'main_deck': [
                    {'name': 'Commander Card', 'quantity': 1},
                    {'name': 'Other Card', 'quantity': 99}
                ],
                'sideboard': [{'name': 'Sideboard Card', 'quantity': 1}]
            }
            
            # Test valid deck
            result = deck_service.validate_deck(valid_deck)
            assert result['valid'] is True
            assert len(result['errors']) == 0
            
            # Test invalid decks
            result = deck_service.validate_deck(invalid_deck_1)
            assert result['valid'] is False
            assert len(result['errors']) > 0
            
            result = deck_service.validate_deck(invalid_deck_2)
            assert result['valid'] is False
            assert len(result['errors']) > 0
    
    def test_import_deck_from_text(self, app):
        """Test importing a deck from text format."""
        with app.app_context():
            deck_service = DeckService()
            
            deck_text = """
            // Main Deck
            20 Mountain
            4 Lightning Bolt
            4 Goblin Guide
            4 Monastery Swiftspear
            4 Eidolon of the Great Revel
            4 Skewer the Critics
            
            // Sideboard
            3 Smash to Smithereens
            2 Blood Moon
            """
            
            # Parse the deck text
            deck_data = deck_service.parse_deck_text(deck_text)
            
            # Verify parsing was successful
            assert len(deck_data['main_deck']) == 6
            assert len(deck_data['sideboard']) == 2
            
            # Verify card quantities
            main_deck_cards = {card['name']: card['quantity'] for card in deck_data['main_deck']}
            assert main_deck_cards['Mountain'] == 20
            assert main_deck_cards['Lightning Bolt'] == 4
            
            sideboard_cards = {card['name']: card['quantity'] for card in deck_data['sideboard']}
            assert sideboard_cards['Smash to Smithereens'] == 3
            assert sideboard_cards['Blood Moon'] == 2
    
    def test_export_deck_to_text(self, app):
        """Test exporting a deck to text format."""
        with app.app_context():
            deck_service = DeckService()
            
            deck_data = {
                'main_deck': [
                    {'name': 'Mountain', 'quantity': 20},
                    {'name': 'Lightning Bolt', 'quantity': 4}
                ],
                'sideboard': [
                    {'name': 'Smash to Smithereens', 'quantity': 3}
                ]
            }
            
            # Export the deck to text
            deck_text = deck_service.export_deck_to_text(deck_data)
            
            # Verify export was successful
            assert '20 Mountain' in deck_text
            assert '4 Lightning Bolt' in deck_text
            assert '// Sideboard' in deck_text
            assert '3 Smash to Smithereens' in deck_text
    
    def test_get_player_decks(self, app):
        """Test retrieving all decks for a player."""
        with app.app_context():
            deck_service = DeckService()
            player_service = PlayerService()
            tournament_service = TournamentService()
            
            # Create a test player
            player_data = {
                'name': 'Player Decks Test',
                'email': 'playerdecks@example.com',
                'active': True
            }
            player_id = player_service.create_player(player_data)
            
            # Create a test tournament
            tournament_data = {
                'name': 'Player Decks Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Test Location',
                'status': 'planned'
            }
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Create multiple decks for the player
            deck_data_list = [
                {
                    'name': 'Deck 1',
                    'format': 'Standard',
                    'player_id': player_id,
                    'tournament_id': tournament_id,
                    'main_deck': [{'name': 'Card', 'quantity': 60}],
                    'sideboard': []
                },
                {
                    'name': 'Deck 2',
                    'format': 'Modern',
                    'player_id': player_id,
                    'tournament_id': tournament_id,
                    'main_deck': [{'name': 'Card', 'quantity': 60}],
                    'sideboard': []
                }
            ]
            
            for deck_data in deck_data_list:
                deck_service.create_deck(deck_data)
            
            # Retrieve all decks for the player
            player_decks = deck_service.get_player_decks(player_id)
            
            # Verify decks were retrieved
            assert len(player_decks) == 2
            assert player_decks[0]['player_id'] == player_id
            assert player_decks[1]['player_id'] == player_id
