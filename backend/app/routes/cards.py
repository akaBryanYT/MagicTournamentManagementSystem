"""
Card API routes for the Tournament Management System.
"""

from flask import Blueprint, request, jsonify
from app.services.card_service import CardService

bp = Blueprint('cards', __name__, url_prefix='/api/cards')
card_service = CardService()

@bp.route('', methods=['GET'])
def get_cards():
    """Get cards with optional filtering."""
    name = request.args.get('name')
    set_code = request.args.get('set')
    format_name = request.args.get('format')
    
    if name:
        cards = card_service.search_cards_by_name(name)
    elif set_code:
        cards = card_service.get_cards_by_set(set_code)
    elif format_name:
        cards = card_service.get_cards_by_format(format_name)
    else:
        # Pagination is important for card database
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        cards = card_service.get_all_cards(page, limit)
    
    return jsonify(cards), 200

@bp.route('/<card_id>', methods=['GET'])
def get_card(card_id):
    """Get card by ID."""
    card = card_service.get_card_by_id(card_id)
    if card:
        return jsonify(card), 200
    return jsonify({'error': 'Card not found'}), 404

@bp.route('/search', methods=['GET'])
def search_cards():
    """Search cards by name with autocomplete."""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    cards = card_service.search_cards_by_name(query)
    return jsonify(cards), 200

@bp.route('', methods=['POST'])
def create_card():
    """Create a new card."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'set_code', 'collector_number']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create card
    card_id = card_service.create_card(data)
    if card_id:
        return jsonify({'id': card_id, 'message': 'Card created successfully'}), 201
    return jsonify({'error': 'Failed to create card'}), 500

@bp.route('/<card_id>', methods=['PUT'])
def update_card(card_id):
    """Update card by ID."""
    data = request.get_json()
    
    # Update card
    success = card_service.update_card(card_id, data)
    if success:
        return jsonify({'message': 'Card updated successfully'}), 200
    return jsonify({'error': 'Failed to update card'}), 404

@bp.route('/batch', methods=['POST'])
def batch_import_cards():
    """Batch import cards."""
    data = request.get_json()
    
    # Validate required fields
    if 'cards' not in data or not isinstance(data['cards'], list):
        return jsonify({'error': 'Missing or invalid cards array'}), 400
    
    # Import cards
    result = card_service.batch_import_cards(data['cards'])
    return jsonify(result), 200

@bp.route('/legality', methods=['GET'])
def check_card_legality():
    """Check card legality in a format."""
    card_name = request.args.get('card')
    format_name = request.args.get('format')
    
    if not card_name or not format_name:
        return jsonify({'error': 'Both card and format parameters are required'}), 400
    
    legality = card_service.check_card_legality(card_name, format_name)
    return jsonify(legality), 200
