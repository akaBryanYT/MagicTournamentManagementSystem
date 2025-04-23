"""
Deck service for the Tournament Management System.
"""

from datetime import datetime
from bson.objectid import ObjectId
from app.models.database import DatabaseConfig

class DeckService:
    """Service for deck operations."""
    
    def __init__(self):
        """Initialize the deck service."""
        self.db_config = DatabaseConfig()
        self.db_config.connect()
        self.db = self.db_config.db
    
    def get_all_decks(self):
        """Get all decks."""
        decks = list(self.db.decks.find({}, {
            '_id': 1, 
            'name': 1, 
            'player_id': 1, 
            'tournament_id': 1,
            'format': 1,
            'validation_status': 1
        }))
        
        for deck in decks:
            deck['id'] = str(deck.pop('_id'))
        
        return decks
    
    def get_decks_by_player(self, player_id):
        """Get decks for a player."""
        decks = list(self.db.decks.find({'player_id': player_id}, {
            '_id': 1, 
            'name': 1, 
            'tournament_id': 1,
            'format': 1,
            'validation_status': 1
        }))
        
        for deck in decks:
            deck['id'] = str(deck.pop('_id'))
        
        return decks
    
    def get_decks_by_tournament(self, tournament_id):
        """Get decks for a tournament."""
        decks = list(self.db.decks.find({'tournament_id': tournament_id}, {
            '_id': 1, 
            'name': 1, 
            'player_id': 1,
            'format': 1,
            'validation_status': 1
        }))
        
        for deck in decks:
            deck['id'] = str(deck.pop('_id'))
            
            # Get player name
            player = self.db.players.find_one({'_id': ObjectId(deck['player_id'])})
            deck['player_name'] = player['name'] if player else 'Unknown'
        
        return decks
    
    def get_decks_by_player_and_tournament(self, player_id, tournament_id):
        """Get decks for a player in a tournament."""
        decks = list(self.db.decks.find({
            'player_id': player_id,
            'tournament_id': tournament_id
        }))
        
        for deck in decks:
            deck['id'] = str(deck.pop('_id'))
        
        return decks
    
    def get_deck_by_id(self, deck_id):
        """Get deck by ID."""
        try:
            deck = self.db.decks.find_one({'_id': ObjectId(deck_id)})
            if deck:
                deck['id'] = str(deck.pop('_id'))
                return deck
            return None
        except Exception as e:
            print(f"Error getting deck: {e}")
            return None
    
    def create_deck(self, deck_data):
        """Create a new deck."""
        try:
            # Validate player exists
            player = self.db.players.find_one({'_id': ObjectId(deck_data['player_id'])})
            if not player:
                return None
            
            # Validate tournament exists
            tournament = self.db.tournaments.find_one({'_id': ObjectId(deck_data['tournament_id'])})
            if not tournament:
                return None
            
            # Add timestamps
            deck_data['created_at'] = datetime.utcnow().isoformat()
            deck_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Set default validation status
            if 'validation_status' not in deck_data:
                deck_data['validation_status'] = 'pending'
            
            # Set default name if not provided
            if 'name' not in deck_data:
                deck_data['name'] = f"{player['name']}'s Deck"
            
            # Insert deck
            result = self.db.decks.insert_one(deck_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating deck: {e}")
            return None
    
    def update_deck(self, deck_id, deck_data):
        """Update deck by ID."""
        try:
            # Get current deck
            current_deck = self.db.decks.find_one({'_id': ObjectId(deck_id)})
            if not current_deck:
                return False
            
            # Remove fields that shouldn't be updated
            protected_fields = ['created_at', 'player_id', 'tournament_id']
            for field in protected_fields:
                if field in deck_data:
                    del deck_data[field]
            
            # Add updated timestamp
            deck_data['updated_at'] = datetime.utcnow().isoformat()
            
            # Update deck
            result = self.db.decks.update_one(
                {'_id': ObjectId(deck_id)},
                {'$set': deck_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating deck: {e}")
            return False
    
    def delete_deck(self, deck_id):
        """Delete deck by ID."""
        try:
            # Get deck
            deck = self.db.decks.find_one({'_id': ObjectId(deck_id)})
            if not deck:
                return False
            
            # Check if tournament is active
            tournament = self.db.tournaments.find_one({'_id': ObjectId(deck['tournament_id'])})
            if tournament and tournament['status'] == 'active':
                return False
            
            # Delete deck
            result = self.db.decks.delete_one({'_id': ObjectId(deck_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting deck: {e}")
            return False

    def import_deck_from_moxfield(self, moxfield_url, player_id, tournament_id, name=None):
        """Import a deck from Moxfield URL."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            # Extract deck ID from URL
            # Example: https://www.moxfield.com/decks/abc123
            deck_id = moxfield_url.split('/')[-1]
            
            # Use Moxfield API to get deck data
            api_url = f"https://api.moxfield.com/v2/decks/all/{deck_id}"
            response = requests.get(api_url)
            
            if response.status_code != 200:
                print(f"Error from Moxfield API: {response.status_code}")
                return None
            
            deck_data = response.json()
            
            # Extract deck information
            deck_name = name or deck_data.get('name', 'Imported Deck')
            format_name = deck_data.get('format', 'standard').lower()
            
            # Extract main deck cards
            main_deck = []
            for card_name, card_info in deck_data.get('mainboard', {}).items():
                main_deck.append({
                    'name': card_name,
                    'quantity': card_info.get('quantity', 1)
                })
            
            # Extract sideboard cards
            sideboard = []
            for card_name, card_info in deck_data.get('sideboard', {}).items():
                sideboard.append({
                    'name': card_name,
                    'quantity': card_info.get('quantity', 1)
                })
            
            # Create deck object
            deck_data = {
                'name': deck_name,
                'format': format_name,
                'player_id': player_id,
                'tournament_id': tournament_id,
                'main_deck': main_deck,
                'sideboard': sideboard,
                'validation_status': 'pending',
                'created_at': datetime.utcnow().isoformat(),
                'updated_at': datetime.utcnow().isoformat()
            }
            
            # Insert deck
            result = self.db.decks.insert_one(deck_data)
            return str(result.inserted_id)
        
        except Exception as e:
            print(f"Error importing deck from Moxfield: {e}")
            return None
    
    def validate_deck(self, deck_id, format_name):
        """Validate a deck against format rules."""
        try:
            # Get deck
            deck = self.db.decks.find_one({'_id': ObjectId(deck_id)})
            if not deck:
                return {'valid': False, 'errors': ['Deck not found']}
            
            # Initialize validation result
            validation_result = {
                'valid': True,
                'errors': [],
                'warnings': []
            }
            
            # Get format rules
            format_rules = self._get_format_rules(format_name)
            
            # Check deck size
            main_deck_size = sum(card['quantity'] for card in deck['main_deck'])
            if main_deck_size < format_rules['min_deck_size']:
                validation_result['valid'] = False
                validation_result['errors'].append(
                    f"Deck contains {main_deck_size} cards, but format requires at least {format_rules['min_deck_size']}"
                )
            
            if format_rules['max_deck_size'] > 0 and main_deck_size > format_rules['max_deck_size']:
                validation_result['valid'] = False
                validation_result['errors'].append(
                    f"Deck contains {main_deck_size} cards, but format allows at most {format_rules['max_deck_size']}"
                )
            
            # Check sideboard size
            if 'sideboard' in deck:
                sideboard_size = sum(card['quantity'] for card in deck['sideboard'])
                if sideboard_size > format_rules['max_sideboard_size']:
                    validation_result['valid'] = False
                    validation_result['errors'].append(
                        f"Sideboard contains {sideboard_size} cards, but format allows at most {format_rules['max_sideboard_size']}"
                    )
            
            # Check card limits
            card_counts = {}
            for card in deck['main_deck']:
                card_name = card['name']
                if card_name not in card_counts:
                    card_counts[card_name] = 0
                card_counts[card_name] += card['quantity']
            
            if 'sideboard' in deck:
                for card in deck['sideboard']:
                    card_name = card['name']
                    if card_name not in card_counts:
                        card_counts[card_name] = 0
                    card_counts[card_name] += card['quantity']
            
            for card_name, count in card_counts.items():
                # Check if card is legal in format
                card = self.db.cards.find_one({'name': card_name})
                if card and 'legalities' in card:
                    if format_name.lower() in card['legalities'] and card['legalities'][format_name.lower()] != 'legal':
                        validation_result['valid'] = False
                        validation_result['errors'].append(
                            f"Card '{card_name}' is not legal in {format_name}"
                        )
                
                # Check card quantity limits
                if card_name == 'Plains' or card_name == 'Island' or card_name == 'Swamp' or card_name == 'Mountain' or card_name == 'Forest':
                    continue  # Basic lands have no limit
                
                if count > format_rules['max_card_count']:
                    validation_result['valid'] = False
                    validation_result['errors'].append(
                        f"Deck contains {count} copies of '{card_name}', but format allows at most {format_rules['max_card_count']}"
                    )
            
            # Update deck validation status
            self.db.decks.update_one(
                {'_id': ObjectId(deck_id)},
                {'$set': {
                    'validation_status': 'valid' if validation_result['valid'] else 'invalid',
                    'validation_errors': validation_result['errors']
                }}
            )
            
            return validation_result
        except Exception as e:
            print(f"Error validating deck: {e}")
            return {'valid': False, 'errors': [str(e)]}
    
    def export_deck_to_text(self, deck_id):
        """Export a deck to text format."""
        try:
            # Get deck
            deck = self.db.decks.find_one({'_id': ObjectId(deck_id)})
            if not deck:
                return None
            
            # Format main deck
            deck_text = "// Main Deck\n"
            for card in deck['main_deck']:
                deck_text += f"{card['quantity']} {card['name']}\n"
            
            # Format sideboard
            if 'sideboard' in deck and deck['sideboard']:
                deck_text += "\n// Sideboard\n"
                for card in deck['sideboard']:
                    deck_text += f"{card['quantity']} {card['name']}\n"
            
            return deck_text
        except Exception as e:
            print(f"Error exporting deck: {e}")
            return None
    
    def _parse_deck_text(self, deck_text):
        """Parse deck text into structured format."""
        try:
            lines = deck_text.strip().split('\n')
            main_deck = []
            sideboard = []
            
            # Determine if there's a sideboard section
            in_sideboard = False
            for line in lines:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('//'):
                    if line.lower().find('sideboard') >= 0:
                        in_sideboard = True
                    continue
                
                # Parse card line
                parts = line.split(' ', 1)
                if len(parts) != 2:
                    continue
                
                try:
                    quantity = int(parts[0])
                    card_name = parts[1].strip()
                    
                    card_entry = {
                        'name': card_name,
                        'quantity': quantity
                    }
                    
                    if in_sideboard:
                        sideboard.append(card_entry)
                    else:
                        main_deck.append(card_entry)
                except ValueError:
                    # Skip lines that don't start with a number
                    continue
            
            return main_deck, sideboard
        except Exception as e:
            print(f"Error parsing deck text: {e}")
            return [], []
    
    def _get_format_rules(self, format_name):
        """Get rules for a specific format."""
        format_name = format_name.lower()
        
        # Default rules
        default_rules = {
            'min_deck_size': 60,
            'max_deck_size': 0,  # 0 means no maximum
            'max_sideboard_size': 15,
            'max_card_count': 4
        }
        
        # Format-specific rules
        format_rules = {
            'standard': default_rules,
            'modern': default_rules,
            'legacy': default_rules,
            'vintage': {
                'min_deck_size': 60,
                'max_deck_size': 0,
                'max_sideboard_size': 15,
                'max_card_count': 4  # Some cards are restricted to 1
            },
            'commander': {
                'min_deck_size': 100,
                'max_deck_size': 100,
                'max_sideboard_size': 0,
                'max_card_count': 1
            },
            'brawl': {
                'min_deck_size': 60,
                'max_deck_size': 60,
                'max_sideboard_size': 0,
                'max_card_count': 1
            },
            'draft': {
                'min_deck_size': 40,
                'max_deck_size': 0,
                'max_sideboard_size': 0,  # Unlimited sideboard in limited formats
                'max_card_count': 0  # No limit on card counts in limited formats
            },
            'sealed': {
                'min_deck_size': 40,
                'max_deck_size': 0,
                'max_sideboard_size': 0,
                'max_card_count': 0
            }
        }
        
        return format_rules.get(format_name, default_rules)
