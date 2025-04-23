"""
Card service for the Tournament Management System.
"""

from bson.objectid import ObjectId
from app.models.database import DatabaseConfig
from sqlalchemy import text
import requests
from urllib.parse import quote
import json

class CardService:
    """Service for card operations."""
    
    def __init__(self):
        """Initialize the card service."""
        self.db_config = DatabaseConfig()
        self.db_config.connect()
        self.db = self.db_config.db
        self.db_type = self.db_config.db_type
    
    def get_all_cards(self, page=1, limit=50):
        """Get all cards with pagination."""
        try:
            skip = (page - 1) * limit
            
            if self.db_type == 'mongodb':
                cards = list(self.db.cards.find({}).skip(skip).limit(limit))
                
                for card in cards:
                    card['id'] = str(card.pop('_id'))
                
                return cards
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT * FROM cards
                    ORDER BY name
                    LIMIT :limit OFFSET :offset
                """), {'limit': limit, 'offset': skip})
                
                cards = []
                for row in result.mappings():
                    card = dict(row)
                    card['id'] = str(card['id'])
                    
                    # Convert JSON fields
                    if card['colors']:
                        card['colors'] = json.loads(card['colors'])
                    if card['color_identity']:
                        card['color_identity'] = json.loads(card['color_identity'])
                    if card['legalities']:
                        card['legalities'] = json.loads(card['legalities'])
                    
                    cards.append(card)
                
                return cards
        except Exception as e:
            print(f"Error getting cards: {e}")
            return []
    
    def get_card_by_id(self, card_id):
        """Get card by ID."""
        try:
            if self.db_type == 'mongodb':
                card = self.db.cards.find_one({'_id': ObjectId(card_id)})
                if card:
                    card['id'] = str(card.pop('_id'))
                    return card
                return None
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT * FROM cards WHERE id = :card_id
                """), {'card_id': int(card_id)})
                
                row = result.mappings().first()
                if row:
                    card = dict(row)
                    card['id'] = str(card['id'])
                    
                    # Convert JSON fields
                    if card['colors']:
                        card['colors'] = json.loads(card['colors'])
                    if card['color_identity']:
                        card['color_identity'] = json.loads(card['color_identity'])
                    if card['legalities']:
                        card['legalities'] = json.loads(card['legalities'])
                    
                    return card
                return None
        except Exception as e:
            print(f"Error getting card: {e}")
            return None
    
    def search_cards_by_name(self, name_query):
        """Search cards by name with autocomplete."""
        try:
            if self.db_type == 'mongodb':
                # Check local database first
                cards = list(self.db.cards.find({'name': {'$regex': name_query, '$options': 'i'}}).limit(20))
                
                if cards:
                    for card in cards:
                        card['id'] = str(card.pop('_id'))
                    return cards
                
                # If no results, use Scryfall API
                return self._search_cards_via_scryfall(name_query)
            else:
                # PostgreSQL implementation
                # Check local database first
                result = self.db.execute(text("""
                    SELECT * FROM cards
                    WHERE name ILIKE :name_query
                    ORDER BY name
                    LIMIT 20
                """), {'name_query': f'%{name_query}%'})
                
                cards = []
                for row in result.mappings():
                    card = dict(row)
                    card['id'] = str(card['id'])
                    
                    # Convert JSON fields
                    if card['colors']:
                        card['colors'] = json.loads(card['colors'])
                    if card['color_identity']:
                        card['color_identity'] = json.loads(card['color_identity'])
                    if card['legalities']:
                        card['legalities'] = json.loads(card['legalities'])
                    
                    cards.append(card)
                
                if cards:
                    return cards
                
                # If no results, use Scryfall API
                return self._search_cards_via_scryfall(name_query)
        except Exception as e:
            print(f"Error searching cards: {e}")
            return []
    
    def _search_cards_via_scryfall(self, name_query):
        """Search cards via Scryfall API."""
        try:
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
                'rarity': scryfall_data.get('rarity', ''),
                'image_uri': scryfall_data.get('image_uris', {}).get('normal', '')
            }
            
            if self.db_type == 'mongodb':
                # Store in database if it doesn't exist
                existing_card = self.db.cards.find_one({'name': card['name']})
                if not existing_card:
                    result = self.db.cards.insert_one(card)
                    card['id'] = str(result.inserted_id)
                else:
                    card['id'] = str(existing_card['_id'])
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT id FROM cards WHERE name = :name
                """), {'name': card['name']})
                
                row = result.first()
                if not row:
                    result = self.db.execute(text("""
                        INSERT INTO cards (
                            name, set_code, collector_number, mana_cost,
                            type_line, oracle_text, colors, color_identity,
                            legalities, rarity, image_uri
                        ) VALUES (
                            :name, :set_code, :collector_number, :mana_cost,
                            :type_line, :oracle_text, :colors, :color_identity,
                            :legalities, :rarity, :image_uri
                        ) RETURNING id
                    """), {
                        'name': card['name'],
                        'set_code': card['set_code'],
                        'collector_number': card['collector_number'],
                        'mana_cost': card['mana_cost'],
                        'type_line': card['type_line'],
                        'oracle_text': card['oracle_text'],
                        'colors': json.dumps(card['colors']),
                        'color_identity': json.dumps(card['color_identity']),
                        'legalities': json.dumps(card['legalities']),
                        'rarity': card['rarity'],
                        'image_uri': card['image_uri']
                    })
                    
                    self.db.commit()
                    card_id = result.scalar()
                    card['id'] = str(card_id)
                else:
                    card['id'] = str(row[0])
            
            return card
        except Exception as e:
            print(f"Error getting card details from Scryfall: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return None
    
    def get_cards_by_set(self, set_code):
        """Get cards by set code."""
        try:
            if self.db_type == 'mongodb':
                cards = list(self.db.cards.find({'set_code': set_code}))
                
                for card in cards:
                    card['id'] = str(card.pop('_id'))
                
                return cards
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT * FROM cards WHERE set_code = :set_code
                """), {'set_code': set_code})
                
                cards = []
                for row in result.mappings():
                    card = dict(row)
                    card['id'] = str(card['id'])
                    
                    # Convert JSON fields
                    if card['colors']:
                        card['colors'] = json.loads(card['colors'])
                    if card['color_identity']:
                        card['color_identity'] = json.loads(card['color_identity'])
                    if card['legalities']:
                        card['legalities'] = json.loads(card['legalities'])
                    
                    cards.append(card)
                
                return cards
        except Exception as e:
            print(f"Error getting cards by set: {e}")
            return []
    
    def get_cards_by_format(self, format_name):
        """Get cards legal in a specific format."""
        try:
            format_key = format_name.lower()
            
            if self.db_type == 'mongodb':
                cards = list(self.db.cards.find({
                    f'legalities.{format_key}': 'legal'
                }).limit(100))
                
                for card in cards:
                    card['id'] = str(card.pop('_id'))
                
                return cards
            else:
                # PostgreSQL implementation - PostgreSQL requires a different approach since
                # it can't directly query into JSON
                result = self.db.execute(text("""
                    SELECT * FROM cards 
                    WHERE legalities::jsonb ->> :format_key = 'legal'
                    LIMIT 100
                """), {'format_key': format_key})
                
                cards = []
                for row in result.mappings():
                    card = dict(row)
                    card['id'] = str(card['id'])
                    
                    # Convert JSON fields
                    if card['colors']:
                        card['colors'] = json.loads(card['colors'])
                    if card['color_identity']:
                        card['color_identity'] = json.loads(card['color_identity'])
                    if card['legalities']:
                        card['legalities'] = json.loads(card['legalities'])
                    
                    cards.append(card)
                
                return cards
        except Exception as e:
            print(f"Error getting cards by format: {e}")
            return []
    
    def create_card(self, card_data):
        """Create a new card."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                # Check if card already exists
                result = self.db.execute(text("""
                    SELECT id FROM cards
                    WHERE name = :name
                    OR (set_code = :set_code AND collector_number = :collector_number)
                """), {
                    'name': card_data['name'],
                    'set_code': card_data['set_code'],
                    'collector_number': card_data['collector_number']
                })
                
                if result.first():
                    return None
                
                # Prepare JSON fields
                colors = json.dumps(card_data.get('colors', [])) if 'colors' in card_data else None
                color_identity = json.dumps(card_data.get('color_identity', [])) if 'color_identity' in card_data else None
                legalities = json.dumps(card_data.get('legalities', {})) if 'legalities' in card_data else None
                
                # Insert card
                result = self.db.execute(text("""
                    INSERT INTO cards (
                        name, set_code, collector_number, mana_cost,
                        type_line, oracle_text, colors, color_identity,
                        legalities, rarity, image_uri
                    ) VALUES (
                        :name, :set_code, :collector_number, :mana_cost,
                        :type_line, :oracle_text, :colors, :color_identity,
                        :legalities, :rarity, :image_uri
                    ) RETURNING id
                """), {
                    'name': card_data['name'],
                    'set_code': card_data['set_code'],
                    'collector_number': card_data['collector_number'],
                    'mana_cost': card_data.get('mana_cost'),
                    'type_line': card_data.get('type_line', ''),
                    'oracle_text': card_data.get('oracle_text'),
                    'colors': colors,
                    'color_identity': color_identity,
                    'legalities': legalities,
                    'rarity': card_data.get('rarity', ''),
                    'image_uri': card_data.get('image_uri')
                })
                
                self.db.commit()
                card_id = result.scalar()
                return str(card_id)
        except Exception as e:
            print(f"Error creating card: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return None
    
    def update_card(self, card_id, card_data):
        """Update card by ID."""
        try:
            if self.db_type == 'mongodb':
                # Update card
                result = self.db.cards.update_one(
                    {'_id': ObjectId(card_id)},
                    {'$set': card_data}
                )
                
                return result.modified_count > 0
            else:
                # PostgreSQL implementation
                # Prepare JSON fields if provided
                params = {'card_id': int(card_id)}
                
                for key, value in card_data.items():
                    if key in ['colors', 'color_identity', 'legalities'] and value is not None:
                        params[key] = json.dumps(value)
                    else:
                        params[key] = value
                
                # Build set clause
                set_clauses = []
                for key in card_data.keys():
                    set_clauses.append(f"{key} = :{key}")
                
                if not set_clauses:
                    return False
                
                query = f"""
                    UPDATE cards
                    SET {', '.join(set_clauses)}
                    WHERE id = :card_id
                """
                
                result = self.db.execute(text(query), params)
                self.db.commit()
                
                return result.rowcount > 0
        except Exception as e:
            print(f"Error updating card: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
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
            
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                for card_data in cards_data:
                    try:
                        # Check if card already exists
                        check_result = self.db.execute(text("""
                            SELECT id FROM cards
                            WHERE name = :name
                            OR (set_code = :set_code AND collector_number = :collector_number)
                        """), {
                            'name': card_data['name'],
                            'set_code': card_data['set_code'],
                            'collector_number': card_data['collector_number']
                        })
                        
                        if check_result.first():
                            result['skipped'] += 1
                            continue
                        
                        # Prepare JSON fields
                        colors = json.dumps(card_data.get('colors', [])) if 'colors' in card_data else None
                        color_identity = json.dumps(card_data.get('color_identity', [])) if 'color_identity' in card_data else None
                        legalities = json.dumps(card_data.get('legalities', {})) if 'legalities' in card_data else None
                        
                        # Insert card
                        self.db.execute(text("""
                            INSERT INTO cards (
                                name, set_code, collector_number, mana_cost,
                                type_line, oracle_text, colors, color_identity,
                                legalities, rarity, image_uri
                            ) VALUES (
                                :name, :set_code, :collector_number, :mana_cost,
                                :type_line, :oracle_text, :colors, :color_identity,
                                :legalities, :rarity, :image_uri
                            )
                        """), {
                            'name': card_data['name'],
                            'set_code': card_data['set_code'],
                            'collector_number': card_data['collector_number'],
                            'mana_cost': card_data.get('mana_cost'),
                            'type_line': card_data.get('type_line', ''),
                            'oracle_text': card_data.get('oracle_text'),
                            'colors': colors,
                            'color_identity': color_identity,
                            'legalities': legalities,
                            'rarity': card_data.get('rarity', ''),
                            'image_uri': card_data.get('image_uri')
                        })
                        
                        result['imported'] += 1
                    except Exception as e:
                        result['errors'].append({
                            'card': card_data.get('name', 'Unknown'),
                            'error': str(e)
                        })
                
                self.db.commit()
            
            return result
        except Exception as e:
            print(f"Error batch importing cards: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return {
                'total': len(cards_data),
                'imported': 0,
                'skipped': 0,
                'errors': [str(e)]
            }
    
    def check_card_legality(self, card_name, format_name):
        """Check card legality in a format."""
        try:
            format_key = format_name.lower()
            
            if self.db_type == 'mongodb':
                card = self.db.cards.find_one({'name': card_name})
                if not card or 'legalities' not in card:
                    return {'legal': False, 'reason': 'Card not found in database'}
                
                if format_key in card['legalities']:
                    status = card['legalities'][format_key]
                    return {
                        'legal': status == 'legal',
                        'status': status
                    }
                
                return {'legal': False, 'reason': f'Format {format_name} not found in card legalities'}
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT legalities FROM cards WHERE name = :card_name
                """), {'card_name': card_name})
                
                row = result.first()
                if not row or not row[0]:
                    return {'legal': False, 'reason': 'Card not found in database'}
                
                legalities = json.loads(row[0])
                
                if format_key in legalities:
                    status = legalities[format_key]
                    return {
                        'legal': status == 'legal',
                        'status': status
                    }
                
                return {'legal': False, 'reason': f'Format {format_name} not found in card legalities'}
        except Exception as e:
            print(f"Error checking card legality: {e}")
            return {'legal': False, 'error': str(e)}