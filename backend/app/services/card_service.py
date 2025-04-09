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
        """Search cards by name with autocomplete."""
        try:
            cards = list(self.db.cards.find({
                'name': {'$regex': name_query, '$options': 'i'}
            }).limit(20))
            
            for card in cards:
                card['id'] = str(card.pop('_id'))
            
            return cards
        except Exception as e:
            print(f"Error searching cards: {e}")
            return []
    
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
