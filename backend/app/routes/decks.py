"""
Deck API routes for the Tournament Management System.
"""

from flask import Blueprint, request, jsonify
from app.services.deck_service import DeckService

bp = Blueprint('decks', __name__, url_prefix='/api/decks')
deck_service = DeckService()

@bp.route('', methods=['GET'])
def get_decks():
    """Get all decks."""
    player_id = request.args.get('player_id')
    tournament_id = request.args.get('tournament_id')
    
    if player_id and tournament_id:
        decks = deck_service.get_decks_by_player_and_tournament(player_id, tournament_id)
    elif player_id:
        decks = deck_service.get_decks_by_player(player_id)
    elif tournament_id:
        decks = deck_service.get_decks_by_tournament(tournament_id)
    else:
        decks = deck_service.get_all_decks()
    
    return jsonify(decks), 200

@bp.route('/<deck_id>', methods=['GET'])
def get_deck(deck_id):
    """Get deck by ID."""
    deck = deck_service.get_deck_by_id(deck_id)
    if deck:
        return jsonify(deck), 200
    return jsonify({'error': 'Deck not found'}), 404

@bp.route('', methods=['POST'])
def create_deck():
    """Create a new deck."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['player_id', 'tournament_id', 'main_deck']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create deck
    deck_id = deck_service.create_deck(data)
    if deck_id:
        return jsonify({'id': deck_id, 'message': 'Deck created successfully'}), 201
    return jsonify({'error': 'Failed to create deck'}), 500

@bp.route('/<deck_id>', methods=['PUT'])
def update_deck(deck_id):
    """Update deck by ID."""
    data = request.get_json()
    
    # Update deck
    success = deck_service.update_deck(deck_id, data)
    if success:
        return jsonify({'message': 'Deck updated successfully'}), 200
    return jsonify({'error': 'Failed to update deck'}), 404

@bp.route('/<deck_id>', methods=['DELETE'])
def delete_deck(deck_id):
    """Delete deck by ID."""
    success = deck_service.delete_deck(deck_id)
    if success:
        return jsonify({'message': 'Deck deleted successfully'}), 200
    return jsonify({'error': 'Failed to delete deck'}), 404

@bp.route('/import', methods=['POST'])
def import_deck():
    """Import a deck from text format."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['player_id', 'tournament_id', 'deck_text', 'format']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Import deck
    deck_id = deck_service.import_deck_from_text(
        data['player_id'],
        data['tournament_id'],
        data['deck_text'],
        data['format'],
        data.get('name', 'Imported Deck')
    )
    
    if deck_id:
        return jsonify({'id': deck_id, 'message': 'Deck imported successfully'}), 201
    return jsonify({'error': 'Failed to import deck'}), 500

@bp.route('/<deck_id>/validate', methods=['POST'])
def validate_deck(deck_id):
    """Validate a deck against format rules."""
    format_name = request.args.get('format')
    if not format_name:
        return jsonify({'error': 'Format parameter is required'}), 400
    
    validation_result = deck_service.validate_deck(deck_id, format_name)
    return jsonify(validation_result), 200

@bp.route('/<deck_id>/export', methods=['GET'])
def export_deck(deck_id):
    """Export a deck to text format."""
    deck_text = deck_service.export_deck_to_text(deck_id)
    if deck_text:
        return jsonify({'deck_text': deck_text}), 200
    return jsonify({'error': 'Failed to export deck'}), 404
