import pytest
from app.services.swiss_pairing import SwissPairingService
from app.services.tournament_service import TournamentService
from app.services.player_service import PlayerService

class TestSwissPairingService:
    """Test cases for the SwissPairingService class."""
    
    def test_initial_pairings(self, app):
        """Test generating initial pairings for round 1."""
        with app.app_context():
            swiss_service = SwissPairingService()
            tournament_service = TournamentService()
            player_service = PlayerService()
            
            # Create a test tournament
            tournament_data = {
                'name': 'Swiss Pairing Test Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Test Location',
                'rounds': 3,
                'status': 'planned'
            }
            
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Create and register 8 test players
            player_ids = []
            for i in range(8):
                player_data = {
                    'name': f'Player {i+1}',
                    'email': f'player{i+1}@example.com',
                    'active': True
                }
                
                player_id = player_service.create_player(player_data)
                player_ids.append(player_id)
                tournament_service.register_player(tournament_id, player_id)
            
            # Start the tournament
            tournament_service.start_tournament(tournament_id)
            
            # Generate pairings for round 1
            pairings = swiss_service.generate_pairings(tournament_id, 1)
            
            # Verify pairings
            assert len(pairings) == 4  # 8 players = 4 matches
            
            # Check that each player appears exactly once
            paired_players = []
            for pairing in pairings:
                paired_players.append(pairing['player1_id'])
                paired_players.append(pairing['player2_id'])
            
            assert len(paired_players) == 8
            assert len(set(paired_players)) == 8  # No duplicates
            
            # Verify all player IDs are in the pairings
            for player_id in player_ids:
                assert player_id in paired_players
    
    def test_subsequent_pairings(self, app):
        """Test generating pairings for round 2 based on round 1 results."""
        with app.app_context():
            swiss_service = SwissPairingService()
            tournament_service = TournamentService()
            player_service = PlayerService()
            
            # Create a test tournament
            tournament_data = {
                'name': 'Swiss Pairing Test Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Test Location',
                'rounds': 3,
                'status': 'planned'
            }
            
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Create and register 8 test players
            player_ids = []
            for i in range(8):
                player_data = {
                    'name': f'Player {i+1}',
                    'email': f'player{i+1}@example.com',
                    'active': True
                }
                
                player_id = player_service.create_player(player_data)
                player_ids.append(player_id)
                tournament_service.register_player(tournament_id, player_id)
            
            # Start the tournament
            tournament_service.start_tournament(tournament_id)
            
            # Generate pairings for round 1
            round1_pairings = swiss_service.generate_pairings(tournament_id, 1)
            
            # Submit results for round 1
            # Players 0, 2, 4, 6 win their matches
            for i, pairing in enumerate(round1_pairings):
                match_id = pairing['match_id']
                # Even indexed players win
                if i % 2 == 0:
                    swiss_service.submit_match_result(match_id, 2, 0, 0)  # 2-0 win
                else:
                    swiss_service.submit_match_result(match_id, 0, 2, 0)  # 0-2 loss
            
            # Start round 2
            tournament_service.start_next_round(tournament_id)
            
            # Generate pairings for round 2
            round2_pairings = swiss_service.generate_pairings(tournament_id, 2)
            
            # Verify pairings
            assert len(round2_pairings) == 4  # 8 players = 4 matches
            
            # Check that each player appears exactly once
            paired_players = []
            for pairing in round2_pairings:
                paired_players.append(pairing['player1_id'])
                paired_players.append(pairing['player2_id'])
            
            assert len(paired_players) == 8
            assert len(set(paired_players)) == 8  # No duplicates
            
            # Verify players with same record are paired together
            # Winners should play winners, losers should play losers
            winners = [player_ids[0], player_ids[2], player_ids[4], player_ids[6]]
            losers = [player_ids[1], player_ids[3], player_ids[5], player_ids[7]]
            
            for pairing in round2_pairings:
                player1_id = pairing['player1_id']
                player2_id = pairing['player2_id']
                
                # Both players should be in the same group (winners or losers)
                assert (player1_id in winners and player2_id in winners) or \
                       (player1_id in losers and player2_id in losers)
    
    def test_standings_calculation(self, app):
        """Test calculating standings after matches."""
        with app.app_context():
            swiss_service = SwissPairingService()
            tournament_service = TournamentService()
            player_service = PlayerService()
            
            # Create a test tournament
            tournament_data = {
                'name': 'Standings Test Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Test Location',
                'rounds': 3,
                'status': 'planned'
            }
            
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Create and register 4 test players
            player_ids = []
            for i in range(4):
                player_data = {
                    'name': f'Player {i+1}',
                    'email': f'player{i+1}@example.com',
                    'active': True
                }
                
                player_id = player_service.create_player(player_data)
                player_ids.append(player_id)
                tournament_service.register_player(tournament_id, player_id)
            
            # Start the tournament
            tournament_service.start_tournament(tournament_id)
            
            # Generate pairings for round 1
            round1_pairings = swiss_service.generate_pairings(tournament_id, 1)
            
            # Submit results for round 1
            # Player 0 beats Player 1 (2-0)
            # Player 2 and Player 3 draw (1-1-1)
            swiss_service.submit_match_result(round1_pairings[0]['match_id'], 2, 0, 0)
            swiss_service.submit_match_result(round1_pairings[1]['match_id'], 1, 1, 1)
            
            # Calculate standings
            standings = swiss_service.calculate_standings(tournament_id)
            
            # Verify standings
            assert len(standings) == 4
            
            # Sort standings by rank
            standings.sort(key=lambda x: x['rank'])
            
            # Player 0 should be first (3 match points)
            assert standings[0]['player_id'] == player_ids[0]
            assert standings[0]['match_points'] == 3
            assert standings[0]['rank'] == 1
            
            # Players 2 and 3 should be tied for second (1 match point each)
            assert standings[1]['match_points'] == 1
            assert standings[2]['match_points'] == 1
            assert (standings[1]['player_id'] == player_ids[2] and standings[2]['player_id'] == player_ids[3]) or \
                   (standings[1]['player_id'] == player_ids[3] and standings[2]['player_id'] == player_ids[2])
            
            # Player 1 should be last (0 match points)
            assert standings[3]['player_id'] == player_ids[1]
            assert standings[3]['match_points'] == 0
            assert standings[3]['rank'] == 4
    
    def test_tiebreakers(self, app):
        """Test tiebreaker calculations."""
        with app.app_context():
            swiss_service = SwissPairingService()
            tournament_service = TournamentService()
            player_service = PlayerService()
            
            # Create a test tournament
            tournament_data = {
                'name': 'Tiebreaker Test Tournament',
                'format': 'Standard',
                'date': '2025-04-15',
                'location': 'Test Location',
                'rounds': 3,
                'status': 'planned',
                'tiebreakers': {
                    'match_points': True,
                    'opponents_match_win_percentage': True,
                    'game_win_percentage': True,
                    'opponents_game_win_percentage': True
                }
            }
            
            tournament_id = tournament_service.create_tournament(tournament_data)
            
            # Create and register 4 test players
            player_ids = []
            for i in range(4):
                player_data = {
                    'name': f'Player {i+1}',
                    'email': f'player{i+1}@example.com',
                    'active': True
                }
                
                player_id = player_service.create_player(player_data)
                player_ids.append(player_id)
                tournament_service.register_player(tournament_id, player_id)
            
            # Start the tournament and play 2 rounds
            tournament_service.start_tournament(tournament_id)
            
            # Generate pairings for round 1
            round1_pairings = swiss_service.generate_pairings(tournament_id, 1)
            
            # Submit results for round 1
            # Player 0 beats Player 1 (2-1)
            # Player 2 beats Player 3 (2-0)
            swiss_service.submit_match_result(round1_pairings[0]['match_id'], 2, 1, 0)
            swiss_service.submit_match_result(round1_pairings[1]['match_id'], 2, 0, 0)
            
            # Start round 2
            tournament_service.start_next_round(tournament_id)
            
            # Generate pairings for round 2
            round2_pairings = swiss_service.generate_pairings(tournament_id, 2)
            
            # Submit results for round 2
            # Player 0 beats Player 2 (2-1)
            # Player 3 beats Player 1 (2-0)
            swiss_service.submit_match_result(round2_pairings[0]['match_id'], 2, 1, 0)
            swiss_service.submit_match_result(round2_pairings[1]['match_id'], 0, 2, 0)
            
            # Calculate standings
            standings = swiss_service.calculate_standings(tournament_id)
            
            # Verify standings
            assert len(standings) == 4
            
            # Sort standings by rank
            standings.sort(key=lambda x: x['rank'])
            
            # Player 0 should be first (6 match points, 2-0 record)
            assert standings[0]['player_id'] == player_ids[0]
            assert standings[0]['match_points'] == 6
            assert standings[0]['rank'] == 1
            
            # Player 2 should be second (3 match points, 1-1 record)
            assert standings[1]['player_id'] == player_ids[2]
            assert standings[1]['match_points'] == 3
            assert standings[1]['rank'] == 2
            
            # Player 3 should be third (3 match points, 1-1 record)
            # Player 2 has better tiebreakers (played against Player 0)
            assert standings[2]['player_id'] == player_ids[3]
            assert standings[2]['match_points'] == 3
            assert standings[2]['rank'] == 3
            
            # Player 1 should be last (0 match points, 0-2 record)
            assert standings[3]['player_id'] == player_ids[1]
            assert standings[3]['match_points'] == 0
            assert standings[3]['rank'] == 4
            
            # Verify tiebreakers are calculated
            for standing in standings:
                assert 'opponents_match_win_percentage' in standing
                assert 'game_win_percentage' in standing
                assert 'opponents_game_win_percentage' in standing
