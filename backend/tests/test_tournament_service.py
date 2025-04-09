import pytest
from app.services.tournament_service import TournamentService
from app.services.player_service import PlayerService

class TestTournamentService:
    """Test cases for the TournamentService class."""
    
    def test_create_tournament(self, app):
        """Test creating a new tournament."""
        with app.app_context():
            tournament_service = TournamentService()
            
            # Create a test tournament
            tournament_data = {
                'name': 'Test Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Test Location',
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
            
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Verify tournament was created
            assert tournament_id is not None
            
            # Retrieve the tournament and verify data
            tournament = tournament_service.get_tournament_by_id(tournament_id)
            assert tournament is not None
            assert tournament['name'] == 'Test Tournament'
            assert tournament['format'] == 'Standard'
            assert tournament['status'] == 'planned'
    
    def test_get_all_tournaments(self, app):
        """Test retrieving all tournaments."""
        with app.app_context():
            tournament_service = TournamentService()
            
            # Create multiple test tournaments
            tournament_data_list = [
                {
                    'name': 'Tournament 1',
                    'format': 'Standard',
                    'date': '2025-04-15',
                    'location': 'Location 1',
                    'status': 'planned'
                },
                {
                    'name': 'Tournament 2',
                    'format': 'Modern',
                    'date': '2025-04-20',
                    'location': 'Location 2',
                    'status': 'active'
                },
                {
                    'name': 'Tournament 3',
                    'format': 'Commander',
                    'date': '2025-04-25',
                    'location': 'Location 3',
                    'status': 'completed'
                }
            ]
            
            for tournament_data in tournament_data_list:
                tournament_service.create_tournament(tournament_data)
            
            # Retrieve all tournaments
            tournaments = tournament_service.get_all_tournaments()
            
            # Verify tournaments were retrieved
            assert len(tournaments) == 3
    
    def test_update_tournament(self, app):
        """Test updating a tournament."""
        with app.app_context():
            tournament_service = TournamentService()
            
            # Create a test tournament
            tournament_data = {
                'name': 'Original Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Original Location',
                'status': 'planned'
            }
            
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Update the tournament
            updated_data = {
                'name': 'Updated Tournament',
                'location': 'Updated Location'
            }
            
            success = tournament_service.update_tournament(tournament_id, updated_data)
            
            # Verify update was successful
            assert success is True
            
            # Retrieve the tournament and verify data was updated
            tournament = tournament_service.get_tournament_by_id(tournament_id)
            assert tournament['name'] == 'Updated Tournament'
            assert tournament['location'] == 'Updated Location'
            assert tournament['format'] == 'Standard'  # Should remain unchanged
    
    def test_tournament_lifecycle(self, app):
        """Test the tournament lifecycle (planned -> active -> completed)."""
        with app.app_context():
            tournament_service = TournamentService()
            
            # Create a test tournament
            tournament_data = {
                'name': 'Lifecycle Test Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Test Location',
                'rounds': 3,
                'time_limit': 50,
                'status': 'planned'
            }
            
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Start the tournament
            success = tournament_service.start_tournament(tournament_id)
            assert success is True
            
            # Verify tournament status is now active
            tournament = tournament_service.get_tournament_by_id(tournament_id)
            assert tournament['status'] == 'active'
            assert tournament['current_round'] == 1
            
            # Start next round
            success = tournament_service.start_next_round(tournament_id)
            assert success is True
            
            # Verify current round is updated
            tournament = tournament_service.get_tournament_by_id(tournament_id)
            assert tournament['current_round'] == 2
            
            # End the tournament
            success = tournament_service.end_tournament(tournament_id)
            assert success is True
            
            # Verify tournament status is now completed
            tournament = tournament_service.get_tournament_by_id(tournament_id)
            assert tournament['status'] == 'completed'
    
    def test_register_player(self, app):
        """Test registering a player for a tournament."""
        with app.app_context():
            tournament_service = TournamentService()
            player_service = PlayerService()
            
            # Create a test tournament
            tournament_data = {
                'name': 'Registration Test Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Test Location',
                'status': 'planned'
            }
            
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Create a test player
            player_data = {
                'name': 'Test Player',
                'email': 'test@example.com',
                'active': True
            }
            
            player_id = player_service.create_player(player_data)
            
            # Register the player for the tournament
            success = tournament_service.register_player(tournament_id, player_id)
            assert success is True
            
            # Verify player is registered
            players = tournament_service.get_tournament_players(tournament_id)
            assert len(players) == 1
            assert players[0]['id'] == player_id
            
            # Try to register the same player again (should fail)
            success = tournament_service.register_player(tournament_id, player_id)
            assert success is False
    
    def test_drop_player(self, app):
        """Test dropping a player from a tournament."""
        with app.app_context():
            tournament_service = TournamentService()
            player_service = PlayerService()
            
            # Create a test tournament
            tournament_data = {
                'name': 'Drop Test Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Test Location',
                'status': 'active'
            }
            
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Create a test player
            player_data = {
                'name': 'Drop Test Player',
                'email': 'drop@example.com',
                'active': True
            }
            
            player_id = player_service.create_player(player_data)
            
            # Register the player for the tournament
            tournament_service.register_player(tournament_id, player_id)
            
            # Drop the player from the tournament
            success = tournament_service.drop_player(tournament_id, player_id)
            assert success is True
            
            # Verify player is dropped but still in the tournament with inactive status
            players = tournament_service.get_tournament_players(tournament_id)
            assert len(players) == 1
            assert players[0]['id'] == player_id
            assert players[0]['active'] is False
