import pytest
from app.services.player_service import PlayerService

class TestPlayerService:
    """Test cases for the PlayerService class."""
    
    def test_create_player(self, app):
        """Test creating a new player."""
        with app.app_context():
            player_service = PlayerService()
            
            # Create a test player
            player_data = {
                'name': 'Test Player',
                'email': 'test@example.com',
                'phone': '555-123-4567',
                'dci_number': '12345678',
                'active': True
            }
            
            player_id = player_service.create_player(player_data)
            
            # Verify player was created
            assert player_id is not None
            
            # Retrieve the player and verify data
            player = player_service.get_player_by_id(player_id)
            assert player is not None
            assert player['name'] == 'Test Player'
            assert player['email'] == 'test@example.com'
            assert player['phone'] == '555-123-4567'
            assert player['dci_number'] == '12345678'
            assert player['active'] is True
    
    def test_get_all_players(self, app):
        """Test retrieving all players."""
        with app.app_context():
            player_service = PlayerService()
            
            # Create multiple test players
            player_data_list = [
                {
                    'name': 'Player 1',
                    'email': 'player1@example.com',
                    'active': True
                },
                {
                    'name': 'Player 2',
                    'email': 'player2@example.com',
                    'active': True
                },
                {
                    'name': 'Player 3',
                    'email': 'player3@example.com',
                    'active': False
                }
            ]
            
            for player_data in player_data_list:
                player_service.create_player(player_data)
            
            # Retrieve all players
            players = player_service.get_all_players()
            
            # Verify players were retrieved
            assert len(players) == 3
    
    def test_update_player(self, app):
        """Test updating a player."""
        with app.app_context():
            player_service = PlayerService()
            
            # Create a test player
            player_data = {
                'name': 'Original Name',
                'email': 'original@example.com',
                'active': True
            }
            
            player_id = player_service.create_player(player_data)
            
            # Update the player
            updated_data = {
                'name': 'Updated Name',
                'email': 'updated@example.com'
            }
            
            success = player_service.update_player(player_id, updated_data)
            
            # Verify update was successful
            assert success is True
            
            # Retrieve the player and verify data was updated
            player = player_service.get_player_by_id(player_id)
            assert player['name'] == 'Updated Name'
            assert player['email'] == 'updated@example.com'
            assert player['active'] is True  # Should remain unchanged
    
    def test_delete_player(self, app):
        """Test deleting a player."""
        with app.app_context():
            player_service = PlayerService()
            
            # Create a test player
            player_data = {
                'name': 'Player to Delete',
                'email': 'delete@example.com',
                'active': True
            }
            
            player_id = player_service.create_player(player_data)
            
            # Delete the player
            success = player_service.delete_player(player_id)
            
            # Verify deletion was successful
            assert success is True
            
            # Try to retrieve the deleted player
            player = player_service.get_player_by_id(player_id)
            assert player is None
    
    def test_toggle_player_status(self, app):
        """Test activating/deactivating a player."""
        with app.app_context():
            player_service = PlayerService()
            
            # Create a test player
            player_data = {
                'name': 'Status Test Player',
                'email': 'status@example.com',
                'active': True
            }
            
            player_id = player_service.create_player(player_data)
            
            # Deactivate the player
            success = player_service.toggle_player_status(player_id, False)
            
            # Verify status change was successful
            assert success is True
            
            # Retrieve the player and verify status was updated
            player = player_service.get_player_by_id(player_id)
            assert player['active'] is False
            
            # Reactivate the player
            success = player_service.toggle_player_status(player_id, True)
            
            # Verify status change was successful
            assert success is True
            
            # Retrieve the player and verify status was updated
            player = player_service.get_player_by_id(player_id)
            assert player['active'] is True
