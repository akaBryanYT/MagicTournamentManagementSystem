"""
Player API routes for the Tournament Management System.
"""

from flask import Blueprint, request, jsonify
from app.services.player_service import PlayerService

bp = Blueprint('players', __name__, url_prefix='/api/players')
player_service = PlayerService()

@bp.route('', methods=['GET'])
def get_players():
    """Get all players."""
    players = player_service.get_all_players()
    return jsonify(players), 200

@bp.route('/<player_id>', methods=['GET'])
def get_player(player_id):
    """Get player by ID."""
    player = player_service.get_player_by_id(player_id)
    if player:
        return jsonify(player), 200
    return jsonify({'error': 'Player not found'}), 404

@bp.route('', methods=['POST'])
def create_player():
    """Create a new player."""
    try:
        data = request.get_json()
        print(f"Received player data: {data}")
        
        # Validate required fields
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create player
        player_id = player_service.create_player(data)
        if player_id:
            return jsonify({'id': player_id, 'message': 'Player created successfully'}), 201
        return jsonify({'error': 'Failed to create player'}), 500
    except Exception as e:
        print(f"Error in create_player route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@bp.route('/<player_id>', methods=['PUT'])
def update_player(player_id):
    """Update player by ID."""
    data = request.get_json()
    
    # Update player
    success = player_service.update_player(player_id, data)
    if success:
        return jsonify({'message': 'Player updated successfully'}), 200
    return jsonify({'error': 'Failed to update player'}), 404

@bp.route('/<player_id>', methods=['DELETE'])
def delete_player(player_id):
    """Delete player by ID."""
    success = player_service.delete_player(player_id)
    if success:
        return jsonify({'message': 'Player deleted successfully'}), 200
    return jsonify({'error': 'Failed to delete player'}), 404

@bp.route('/search', methods=['GET'])
def search_players():
    """Search players by name or email."""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    players = player_service.search_players(query)
    return jsonify(players), 200

@bp.route('/<player_id>/tournaments', methods=['GET'])
def get_player_tournaments(player_id):
    """Get tournaments for a player."""
    tournaments = player_service.get_player_tournaments(player_id)
    return jsonify(tournaments), 200

@bp.route('/<player_id>/decks', methods=['GET'])
def get_player_decks(player_id):
    """Get decks for a player."""
    decks = player_service.get_player_decks(player_id)
    return jsonify(decks), 200
