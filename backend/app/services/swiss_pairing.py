# swiss_pairing.py

class SwissPairingService:
    """Service for Swiss pairing algorithm."""
    
    def create_pairings(self, player_ids, previous_matches, use_seeds_for_byes=False):
        """
        Create pairings for the next round using Swiss algorithm.
        
        Args:
            player_ids: List of player IDs sorted by standings (or seeds for first round)
            previous_matches: List of previous match documents
            use_seeds_for_byes: Whether to use original seeding for bye assignment
        
        Returns:
            List of pairs (tuples) of player IDs
        """
        # Create a set of previous pairings for quick lookup
        previous_pairings = set()
        for match in previous_matches:
            if match.get('player1_id') and match.get('player2_id'):
                # Store both directions to make lookup easier
                previous_pairings.add((match['player1_id'], match['player2_id']))
                previous_pairings.add((match['player2_id'], match['player1_id']))
        
        # Handle odd number of players (add BYE)
        if len(player_ids) % 2 != 0:
            # Get list of players who have had byes
            has_had_bye = set()
            for match in previous_matches:
                if match.get('player2_id') is None:
                    has_had_bye.add(match['player1_id'])
            
            # Find player for bye
            bye_player = None
            
            if use_seeds_for_byes:
                # Give bye to the lowest seed that hasn't had a bye yet
                # (higher seed value = lower seeding)
                for player_id in reversed(player_ids):
                    if player_id not in has_had_bye:
                        bye_player = player_id
                        break
            else:
                # Traditional method - find lowest ranked player who hasn't had a BYE
                for player_id in reversed(player_ids):
                    if player_id not in has_had_bye:
                        bye_player = player_id
                        break
            
            # If all players have had a BYE, give it to the lowest ranked player
            if bye_player is None:
                bye_player = player_ids[-1]
            
            # Remove the BYE player from the list
            player_ids = [p for p in player_ids if p != bye_player]
            
            # Add the BYE pairing
            pairings = [(bye_player,)]
        else:
            pairings = []
        
        # Create a copy of player_ids to work with
        remaining_players = player_ids.copy()
        
        # Pair players
        while len(remaining_players) > 0:
            # Get the highest ranked player
            player1 = remaining_players.pop(0)
            
            # Find the highest ranked player that player1 hasn't played yet
            player2 = None
            for p in remaining_players:
                if (player1, p) not in previous_pairings:
                    player2 = p
                    break
            
            # If all possible opponents have been played, pair with the highest ranked player
            if player2 is None:
                player2 = remaining_players[0]
            
            # Remove player2 from remaining players
            remaining_players.remove(player2)
            
            # Add the pairing
            pairings.append((player1, player2))
        
        return pairings