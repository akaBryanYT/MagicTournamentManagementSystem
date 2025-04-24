"""
Deck service for the Tournament Management System.
"""

from datetime import datetime
from bson.objectid import ObjectId
from app.models.database import DatabaseConfig
from sqlalchemy import text
import json
import requests
import re
from collections import defaultdict

class DeckService:
    """Service for deck operations."""
    
    def __init__(self):
        """Initialize the deck service."""
        self.db_config = DatabaseConfig()
        self.db_config.connect()
        self.db = self.db_config.db
        self.db_type = self.db_config.db_type
    
    def get_all_decks(self):
        """Get all decks."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT d.id, d.name, d.player_id, d.tournament_id,
                           d.format, d.validation_status, p.name as player_name
                    FROM decks d
                    JOIN players p ON d.player_id = p.id
                """))
                
                decks = []
                for row in result.mappings():
                    deck = dict(row)
                    deck['id'] = str(deck['id'])
                    deck['player_id'] = str(deck['player_id'])
                    deck['tournament_id'] = str(deck['tournament_id'])
                    decks.append(deck)
                
                return decks
        except Exception as e:
            print(f"Error getting decks: {e}")
            return []
    
    def get_decks_by_player(self, player_id):
        """Get decks for a player."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT d.id, d.name, d.tournament_id, d.format, d.validation_status,
                           t.name as tournament_name
                    FROM decks d
                    JOIN tournaments t ON d.tournament_id = t.id
                    WHERE d.player_id = :player_id
                """), {'player_id': int(player_id)})
                
                decks = []
                for row in result.mappings():
                    deck = dict(row)
                    deck['id'] = str(deck['id'])
                    deck['tournament_id'] = str(deck['tournament_id'])
                    decks.append(deck)
                
                return decks
        except Exception as e:
            print(f"Error getting player decks: {e}")
            return []
    
    def get_decks_by_tournament(self, tournament_id):
        """Get decks for a tournament."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT d.id, d.name, d.player_id, d.format, d.validation_status,
                           p.name as player_name
                    FROM decks d
                    JOIN players p ON d.player_id = p.id
                    WHERE d.tournament_id = :tournament_id
                """), {'tournament_id': int(tournament_id)})
                
                decks = []
                for row in result.mappings():
                    deck = dict(row)
                    deck['id'] = str(deck['id'])
                    deck['player_id'] = str(deck['player_id'])
                    decks.append(deck)
                
                return decks
        except Exception as e:
            print(f"Error getting tournament decks: {e}")
            return []
    
    def get_decks_by_player_and_tournament(self, player_id, tournament_id):
        """Get decks for a player in a tournament."""
        try:
            if self.db_type == 'mongodb':
                decks = list(self.db.decks.find({
                    'player_id': player_id,
                    'tournament_id': tournament_id
                }))
                
                for deck in decks:
                    deck['id'] = str(deck.pop('_id'))
                
                return decks
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT d.*
                    FROM decks d
                    WHERE d.player_id = :player_id AND d.tournament_id = :tournament_id
                """), {
                    'player_id': int(player_id),
                    'tournament_id': int(tournament_id)
                })
                
                decks = []
                for row in result.mappings():
                    deck = dict(row)
                    deck['id'] = str(deck['id'])
                    deck['player_id'] = str(deck['player_id'])
                    deck['tournament_id'] = str(deck['tournament_id'])
                    
                    # Convert JSON fields
                    if deck.get('validation_errors'):
                        deck['validation_errors'] = json.loads(deck['validation_errors'])
                    
                    # Get deck cards
                    deck_cards = self._get_deck_cards_sql(deck['id'])
                    deck['main_deck'] = [c for c in deck_cards if not c['is_sideboard']]
                    deck['sideboard'] = [c for c in deck_cards if c['is_sideboard']]
                    
                    decks.append(deck)
                
                return decks
        except Exception as e:
            print(f"Error getting player tournament decks: {e}")
            return []
    
    def get_deck_by_id(self, deck_id):
        """Get deck by ID."""
        try:
            if self.db_type == 'mongodb':
                deck = self.db.decks.find_one({'_id': ObjectId(deck_id)})
                if deck:
                    deck['id'] = str(deck.pop('_id'))
                    return deck
                return None
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    SELECT d.*, p.name as player_name, t.name as tournament_name
                    FROM decks d
                    JOIN players p ON d.player_id = p.id
                    JOIN tournaments t ON d.tournament_id = t.id
                    WHERE d.id = :deck_id
                """), {'deck_id': int(deck_id)})
                
                row = result.mappings().first()
                if row:
                    deck = dict(row)
                    deck['id'] = str(deck['id'])
                    deck['player_id'] = str(deck['player_id'])
                    deck['tournament_id'] = str(deck['tournament_id'])
                    
                    # Convert timestamps to ISO format
                    if deck.get('created_at'):
                        deck['created_at'] = deck['created_at'].isoformat()
                    if deck.get('updated_at'):
                        deck['updated_at'] = deck['updated_at'].isoformat()
                    
                    # Convert JSON fields
                    if deck.get('validation_errors'):
                        deck['validation_errors'] = json.loads(deck['validation_errors'])
                    
                    # Get deck cards
                    deck_cards = self._get_deck_cards_sql(deck['id'])
                    deck['main_deck'] = [c for c in deck_cards if not c['is_sideboard']]
                    deck['sideboard'] = [c for c in deck_cards if c['is_sideboard']]
                    
                    return deck
                return None
        except Exception as e:
            print(f"Error getting deck: {e}")
            return None
    
    def _get_deck_cards_sql(self, deck_id):
        """Get cards for a deck (PostgreSQL)."""
        try:
            result = self.db.execute(text("""
                SELECT dc.quantity, dc.is_sideboard, c.name
                FROM deck_cards dc
                JOIN cards c ON dc.card_id = c.id
                WHERE dc.deck_id = :deck_id
            """), {'deck_id': int(deck_id)})
            
            cards = []
            for row in result:
                quantity, is_sideboard, name = row
                cards.append({
                    'quantity': quantity,
                    'name': name,
                    'is_sideboard': is_sideboard
                })
            
            return cards
        except Exception as e:
            print(f"Error getting deck cards: {e}")
            return []
       
    # ------------------------------------------------------------
    #  PRIVATE ─ text-to-cards helper
    # ------------------------------------------------------------
    def _parse_deck_text(self, deck_text):
        """
        Converts a raw decklist string into main/side arrays.
        Returns (main_list, side_list) where each list item is
        {'name': str, 'quantity': int}.
        """
        line_re = re.compile(
            r'^(\d+)[xX]?\s+([^(]+)\s*(?:\([A-Za-z0-9]{2,5}\))?.*$'
        )

        main, side = defaultdict(int), defaultdict(int)
        in_side = False

        for raw in deck_text.splitlines():
            l = raw.strip()
            if not l:
                continue
            low = l.lower()

            if (
                low.startswith('sb:') or
                (low.startswith('//') and 'sideboard' in low) or
                low == 'sideboard'
            ):
                in_side = True
                if low.startswith('sb:'):
                    l = l[3:].strip()  # allow “SB: 2 Force of Will”
                if not l:
                    continue

            if low.startswith('//') or low.startswith('#') or \
               low in ('commander', 'companion') or 'maybeboard' in low:
                continue

            m = line_re.match(l)
            if not m:
                continue

            qty = int(m.group(1))
            name = m.group(2).strip()

            (side if in_side else main)[name] += qty

        main_list = [{'name': n, 'quantity': q} for n, q in main.items()]
        side_list = [{'name': n, 'quantity': q} for n, q in side.items()]
        return main_list, side_list

       
    def import_deck_from_moxfield(self, player_id, tournament_id, moxfield_url, format_name, name=None):
        """Import a deck from Moxfield URL."""
        try:
            # Validate URL format
            if not moxfield_url or 'moxfield.com/decks/' not in moxfield_url:
                print("Invalid Moxfield URL format")
                return None
            
            # Extract deck ID from URL
            deck_id = moxfield_url.split('moxfield.com/decks/')[1].split('/')[0].split('?')[0]
            
            # Fetch deck data from Moxfield API
            api_url = f"https://api.moxfield.com/v2/decks/all/{deck_id}"
            response = requests.get(api_url)
            
            if response.status_code != 200:
                print(f"Error fetching deck from Moxfield: {response.status_code}")
                return None
            
            deck_data = response.json()
            
            # Process main deck
            main_deck = []
            for card_name, card_info in deck_data.get('mainboard', {}).items():
                main_deck.append({
                    'name': card_name,
                    'quantity': card_info.get('quantity', 1)
                })
            
            # Process sideboard
            sideboard = []
            for card_name, card_info in deck_data.get('sideboard', {}).items():
                sideboard.append({
                    'name': card_name,
                    'quantity': card_info.get('quantity', 1)
                })
            
            # Create deck
            deck_name = name or deck_data.get('name', 'Imported Moxfield Deck')
            
            if self.db_type == 'mongodb':
                deck_data = {
                    'name': deck_name,
                    'player_id': player_id,
                    'tournament_id': tournament_id,
                    'format': format_name,
                    'main_deck': main_deck,
                    'sideboard': sideboard,
                    'validation_status': 'pending',
                    'created_at': datetime.utcnow().isoformat(),
                    'updated_at': datetime.utcnow().isoformat()
                }
                
                result = self.db.decks.insert_one(deck_data)
                return str(result.inserted_id)
            else:
                # PostgreSQL implementation
                result = self.db.execute(text("""
                    INSERT INTO decks (
                        name, player_id, tournament_id, format,
                        created_at, updated_at, validation_status
                    ) VALUES (
                        :name, :player_id, :tournament_id, :format,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 'pending'
                    ) RETURNING id
                """), {
                    'name': deck_name,
                    'player_id': int(player_id),
                    'tournament_id': int(tournament_id),
                    'format': format_name
                })
                
                deck_id = result.scalar()
                
                # Insert deck cards
                if main_deck:
                    self._insert_deck_cards_sql(deck_id, main_deck, False)
                
                if sideboard:
                    self._insert_deck_cards_sql(deck_id, sideboard, True)
                
                self.db.commit()
                return str(deck_id)
        except Exception as e:
            print(f"Error importing deck from Moxfield: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return None
    
    def import_deck_from_text(self, player_id, tournament_id, deck_text,
                              format_name='standard', name=None):
        """Import a deck from a pasted text list."""
        main_deck, sideboard = self._parse_deck_text(deck_text)
        if not main_deck:
            print("No main-deck cards found while parsing text import")
            return None

        deck_data = {
            'name': name or 'Imported Deck',
            'player_id': player_id,
            'tournament_id': tournament_id,
            'format': format_name,
            'main_deck': main_deck,
            'sideboard': sideboard,
            'validation_status': 'pending'
        }
        # Delegate to the existing create-deck logic so we stay DRY
        return self.create_deck(deck_data)

    
    def create_deck(self, deck_data):
        """Create a new deck."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                # Validate player exists
                player_result = self.db.execute(text("""
                    SELECT name FROM players WHERE id = :player_id
                """), {'player_id': int(deck_data['player_id'])})
                
                player = player_result.first()
                if not player:
                    return None
                
                # Validate tournament exists
                tournament_result = self.db.execute(text("""
                    SELECT id FROM tournaments WHERE id = :tournament_id
                """), {'tournament_id': int(deck_data['tournament_id'])})
                
                if not tournament_result.first():
                    return None
                
                # Set default name if not provided
                if 'name' not in deck_data or not deck_data['name']:
                    deck_data['name'] = f"{player[0]}'s Deck"
                
                # Set default validation status
                validation_status = deck_data.get('validation_status', 'pending')
                
                # Convert validation errors to JSON if provided
                validation_errors = None
                if 'validation_errors' in deck_data and deck_data['validation_errors']:
                    validation_errors = json.dumps(deck_data['validation_errors'])
                
                # Insert deck
                result = self.db.execute(text("""
                    INSERT INTO decks (
                        name, player_id, tournament_id, format,
                        created_at, updated_at, validation_status, validation_errors
                    ) VALUES (
                        :name, :player_id, :tournament_id, :format,
                        CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, :validation_status, :validation_errors
                    ) RETURNING id
                """), {
                    'name': deck_data['name'],
                    'player_id': int(deck_data['player_id']),
                    'tournament_id': int(deck_data['tournament_id']),
                    'format': deck_data.get('format', 'unknown'),
                    'validation_status': validation_status,
                    'validation_errors': validation_errors
                })
                
                deck_id = result.scalar()
                
                # Insert deck cards
                if 'main_deck' in deck_data and deck_data['main_deck']:
                    self._insert_deck_cards_sql(deck_id, deck_data['main_deck'], False)
                
                if 'sideboard' in deck_data and deck_data['sideboard']:
                    self._insert_deck_cards_sql(deck_id, deck_data['sideboard'], True)
                
                self.db.commit()
                return str(deck_id)
        except Exception as e:
            print(f"Error creating deck: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return None
    
    def _insert_deck_cards_sql(self, deck_id, cards, is_sideboard):
        """Insert cards for a deck (PostgreSQL)."""
        try:
            for card in cards:
                # Get or create card
                card_result = self.db.execute(text("""
                    SELECT id FROM cards WHERE name = :name
                """), {'name': card['name']})
                
                card_row = card_result.first()
                if card_row:
                    card_id = card_row[0]
                else:
                    # Card doesn't exist, create a minimal record
                    new_card_result = self.db.execute(text("""
                        INSERT INTO cards (name, type_line)
                        VALUES (:name, 'Unknown')
                        RETURNING id
                    """), {'name': card['name']})
                    
                    card_id = new_card_result.scalar()
                
                # Insert deck card
                self.db.execute(text("""
                    INSERT INTO deck_cards (deck_id, card_id, quantity, is_sideboard)
                    VALUES (:deck_id, :card_id, :quantity, :is_sideboard)
                """), {
                    'deck_id': deck_id,
                    'card_id': card_id,
                    'quantity': card['quantity'],
                    'is_sideboard': is_sideboard
                })
        except Exception as e:
            print(f"Error inserting deck cards: {e}")
            raise
    
    def update_deck(self, deck_id, deck_data):
        """Update deck by ID."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                # Get current deck
                deck_result = self.db.execute(text("""
                    SELECT id FROM decks WHERE id = :deck_id
                """), {'deck_id': int(deck_id)})
                
                if not deck_result.first():
                    return False
                
                # Remove fields that shouldn't be updated
                protected_fields = ['created_at', 'player_id', 'tournament_id']
                update_data = {k: v for k, v in deck_data.items() if k not in protected_fields}
                
                if not update_data:
                    return False
                
                # Handle JSON fields
                if 'validation_errors' in update_data and update_data['validation_errors'] is not None:
                    update_data['validation_errors'] = json.dumps(update_data['validation_errors'])
                
                # Build set clause
                set_clauses = []
                params = {'deck_id': int(deck_id)}
                
                for key, value in update_data.items():
                    set_clauses.append(f"{key} = :{key}")
                    params[key] = value
                
                # Add updated timestamp
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                
                query = f"""
                    UPDATE decks
                    SET {', '.join(set_clauses)}
                    WHERE id = :deck_id
                """
                
                result = self.db.execute(text(query), params)
                
                # Update deck cards if provided
                if 'main_deck' in deck_data or 'sideboard' in deck_data:
                    # Delete existing cards
                    self.db.execute(text("""
                        DELETE FROM deck_cards WHERE deck_id = :deck_id
                    """), {'deck_id': int(deck_id)})
                    
                    # Insert new cards
                    if 'main_deck' in deck_data and deck_data['main_deck']:
                        self._insert_deck_cards_sql(int(deck_id), deck_data['main_deck'], False)
                    
                    if 'sideboard' in deck_data and deck_data['sideboard']:
                        self._insert_deck_cards_sql(int(deck_id), deck_data['sideboard'], True)
                
                self.db.commit()
                return result.rowcount > 0
        except Exception as e:
            print(f"Error updating deck: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False
    
    def delete_deck(self, deck_id):
        """Delete deck by ID."""
        try:
            if self.db_type == 'mongodb':
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
            else:
                # PostgreSQL implementation
                # Get deck and tournament status
                deck_result = self.db.execute(text("""
                    SELECT d.id, t.status
                    FROM decks d
                    JOIN tournaments t ON d.tournament_id = t.id
                    WHERE d.id = :deck_id
                """), {'deck_id': int(deck_id)})
                
                row = deck_result.first()
                if not row:
                    return False
                
                # Check if tournament is active
                if row[1] == 'active':
                    return False
                
                # Delete deck cards first (foreign key constraint)
                self.db.execute(text("""
                    DELETE FROM deck_cards WHERE deck_id = :deck_id
                """), {'deck_id': int(deck_id)})
                
                # Delete deck
                result = self.db.execute(text("""
                    DELETE FROM decks WHERE id = :deck_id
                """), {'deck_id': int(deck_id)})
                
                self.db.commit()
                return result.rowcount > 0
        except Exception as e:
            print(f"Error deleting deck: {e}")
            if self.db_type == 'postgresql':
                self.db.rollback()
            return False