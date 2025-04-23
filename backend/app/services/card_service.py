"""
Card service for the Tournament Management System.
"""

from bson.objectid import ObjectId
from app.models.database import DatabaseConfig

class CardService:
    """Service for card operations."""
    
    def __init__(self):
        """Initialize the card service."""
        self.db_config = DatabaseConfig()
        self.db_config.connect()
        self.db = self.db_config.db
    
    def get_all_cards(self, page=1, limit=50):
        """Get all cards with pagination."""
        try:
            skip = (page - 1) * limit
            cards = list(self.db.cards.find({}).skip(skip).limit(limit))
            
            for card in cards:
                card['id'] = str(card.pop('_id'))
            
            return cards
        except Exception as e:
            print(f"Error getting cards: {e}")
            return []
    
    def get_card_by_id(self, card_id):
        """Get card by ID."""
        try:
            card = self.db.cards.find_one({'_id': ObjectId(card_id)})
            if card:
                card['id'] = str(card.pop('_id'))
                return card
            return None
        except Exception as e:
            print(f"Error getting card: {e}")
            return None
    
    def search_cards_by_name(self, name_query):
        """Search cards by name with autocomplete from Scryfall."""
        try:
            import requests
            
            # Use Scryfall API for autocomplete
            api_url = f"https://api.scryfall.com/cards/autocomplete?q={name_query}"
            response = requests.get(api_url)
            
            if response.status_code != 200:
                print(f"Error from Scryfall API: {response.status_code}")
                return []
            
            data = response.json()
            cards = []
            
            # Get full card data for each match
            for card_name in data.get('data', [])[:20]:  # Limit to 20 results
                card_data = self.get_card_details_from_scryfall(card_name)
                if card_data:
                    cards.append(card_data)
            
            return cards
        except Exception as e:
            print(f"Error searching cards via Scryfall: {e}")
            return []

    def get_card_details_from_scryfall(self, card_name):
        """Get detailed card information from Scryfall."""
        try:
            import requests
            from urllib.parse import quote
            
            encoded_name = quote(card_name)
            api_url = f"https://api.scryfall.com/cards/named?exact={encoded_name}"
            response = requests.get(api_url)
            
            if response.status_code != 200:
                # Try fuzzy search if exact match fails
                api_url = f"https://api.scryfall.com/cards/named?fuzzy={encoded_name}"
                response = requests.get(api_url)
                
                if response.status_code != 200:
                    return None
            
            scryfall_data = response.json()
            
            # Map Scryfall data to our card model
            card = {
                'name': scryfall_data.get('name', ''),
                'set_code': scryfall_data.get('set', '').upper(),
                'collector_number': scryfall_data.get('collector_number', ''),
                'mana_cost': scryfall_data.get('mana_cost', ''),
                'type_line': scryfall_data.get('type_line', ''),
                'oracle_text': scryfall_data.get('oracle_text', ''),
                'colors': scryfall_data.get('colors', []),
                'color_identity': scryfall_data.get('color_identity', []),
                'legalities': scryfall_data.get('legalities', {}),
                'image_uri': scryfall_data.get('image_uris', {}).get('normal', '')
            }
            
            # Store in database if it doesn't exist
            existing_card = self.db.cards.find_one({'name': card['name']})
            if not existing_card:
                result = self.db.cards.insert_one(card)
                card['id'] = str(result.inserted_id)
            else:
                card['id'] = str(existing_card['_id'])
            
            return card
        except Exception as e:
            print(f"Error getting card details from Scryfall: {e}")
            return None
    
    def get_cards_by_set(self, set_code):
        """Get cards by set code."""
        try:
            cards = list(self.db.cards.find({'set_code': set_code}))
            
            for card in cards:
                card['id'] = str(card.pop('_id'))
            
            return cards
        except Exception as e:
            print(f"Error getting cards by set: {e}")
            return []
    
    def get_cards_by_format(self, format_name):
        """Get cards legal in a specific format."""
        try:
            format_key = format_name.lower()
            cards = list(self.db.cards.find({
                f'legalities.{format_key}': 'legal'
            }).limit(100))
            
            for card in cards:
                card['id'] = str(card.pop('_id'))
            
            return cards
        except Exception as e:
            print(f"Error getting cards by format: {e}")
            return []
    
    def create_card(self, card_data):
        """Create a new card."""
        try:
            # Check if card already exists
            existing_card = self.db.cards.find_one({
                '$or': [
                    {'name': card_data['name']},
                    {
                        'set_code': card_data['set_code'],
                        'collector_number': card_data['collector_number']
                    }
                ]
            })
            
            if existing_card:
                return None
            
            # Insert card
            result = self.db.cards.insert_one(card_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error creating card: {e}")
            return None
    
    def update_card(self, card_id, card_data):
        """Update card by ID."""
        try:
            # Update card
            result = self.db.cards.update_one(
                {'_id': ObjectId(card_id)},
                {'$set': card_data}
            )
            
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating card: {e}")
            return False
    
    def batch_import_cards(self, cards_data):
        """Batch import cards."""
        try:
            result = {
                'total': len(cards_data),
                'imported': 0,
                'skipped': 0,
                'errors': []
            }
            
            for card_data in cards_data:
                try:
                    # Check if card already exists
                    existing_card = self.db.cards.find_one({
                        '$or': [
                            {'name': card_data['name']},
                            {
                                'set_code': card_data['set_code'],
                                'collector_number': card_data['collector_number']
                            }
                        ]
                    })
                    
                    if existing_card:
                        result['skipped'] += 1
                        continue
                    
                    # Insert card
                    self.db.cards.insert_one(card_data)
                    result['imported'] += 1
                except Exception as e:
                    result['errors'].append({
                        'card': card_data.get('name', 'Unknown'),
                        'error': str(e)
                    })
            
            return result
        except Exception as e:
            print(f"Error batch importing cards: {e}")
            return {
                'total': len(cards_data),
                'imported': 0,
                'skipped': 0,
                'errors': [str(e)]
            }
    
    def check_card_legality(self, card_name, format_name):
        """Check card legality in a format."""
        try:
            card = self.db.cards.find_one({'name': card_name})
            if not card or 'legalities' not in card:
                return {'legal': False, 'reason': 'Card not found in database'}
            
            format_key = format_name.lower()
            if format_key in card['legalities']:
                status = card['legalities'][format_key]
                return {
                    'legal': status == 'legal',
                    'status': status
                }
            
            return {'legal': False, 'reason': f'Format {format_name} not found in card legalities'}
        except Exception as e:
            print(f"Error checking card legality: {e}")
            return {'legal': False, 'error': str(e)}
