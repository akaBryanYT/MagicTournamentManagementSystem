"""
Tournament API routes for the Tournament Management System.
"""

from flask import Blueprint, request, jsonify
from app.services.tournament_service import TournamentService

bp = Blueprint('tournaments', __name__, url_prefix='/api/tournaments')
tournament_service = TournamentService()

@bp.route('', methods=['GET'])
def get_tournaments():
    """Get all tournaments."""
    tournaments = tournament_service.get_all_tournaments()
    return jsonify(tournaments), 200

@bp.route('/<tournament_id>', methods=['GET'])
def get_tournament(tournament_id):
    """Get tournament by ID."""
    tournament = tournament_service.get_tournament_by_id(tournament_id)
    if tournament:
        return jsonify(tournament), 200
    return jsonify({'error': 'Tournament not found'}), 404

@bp.route('', methods=['POST'])
def create_tournament():
    """Create a new tournament."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['name', 'format', 'date']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create tournament
    tournament_id = tournament_service.create_tournament(data)
    if tournament_id:
        return jsonify({'id': tournament_id, 'message': 'Tournament created successfully'}), 201
    return jsonify({'error': 'Failed to create tournament'}), 500

@bp.route('/<tournament_id>', methods=['PUT'])
def update_tournament(tournament_id):
    """Update tournament by ID."""
    data = request.get_json()
    
    # Update tournament
    success = tournament_service.update_tournament(tournament_id, data)
    if success:
        return jsonify({'message': 'Tournament updated successfully'}), 200
    return jsonify({'error': 'Failed to update tournament'}), 404

@bp.route('/<tournament_id>', methods=['DELETE'])
def delete_tournament(tournament_id):
    """Delete tournament by ID."""
    success = tournament_service.delete_tournament(tournament_id)
    if success:
        return jsonify({'message': 'Tournament deleted successfully'}), 200
    return jsonify({'error': 'Failed to delete tournament'}), 404

@bp.route('/<tournament_id>/players', methods=['GET'])
def get_tournament_players(tournament_id):
    """Get players for a tournament."""
    players = tournament_service.get_tournament_players(tournament_id)
    return jsonify(players), 200

@bp.route('/<tournament_id>/players', methods=['POST'])
def register_player(tournament_id):
    """Register a player for a tournament."""
    data = request.get_json()
    
    # Validate required fields
    if 'player_id' not in data:
        return jsonify({'error': 'Missing required field: player_id'}), 400
    
    # Register player
    success = tournament_service.register_player(tournament_id, data['player_id'])
    if success:
        return jsonify({'message': 'Player registered successfully'}), 200
    return jsonify({'error': 'Failed to register player'}), 500

@bp.route('/<tournament_id>/players/<player_id>', methods=['DELETE'])
def drop_player(tournament_id, player_id):
    """Drop a player from a tournament."""
    success = tournament_service.drop_player(tournament_id, player_id)
    if success:
        return jsonify({'message': 'Player dropped successfully'}), 200
    return jsonify({'error': 'Failed to drop player'}), 404

@bp.route('/<tournament_id>/rounds', methods=['GET'])
def get_tournament_rounds(tournament_id):
    """Get rounds for a tournament."""
    rounds = tournament_service.get_tournament_rounds(tournament_id)
    return jsonify(rounds), 200

@bp.route('/<tournament_id>/rounds/<round_number>', methods=['GET'])
def get_round_pairings(tournament_id, round_number):
    """Get pairings for a specific round."""
    pairings = tournament_service.get_round_pairings(tournament_id, round_number)
    return jsonify(pairings), 200

@bp.route('/<tournament_id>/rounds/next', methods=['POST'])
def create_next_round(tournament_id):
    """Create pairings for the next round."""
    pairings = tournament_service.create_next_round(tournament_id)
    if pairings:
        return jsonify(pairings), 201
    return jsonify({'error': 'Failed to create next round'}), 500

@bp.route('/<tournament_id>/standings', methods=['GET'])
def get_tournament_standings(tournament_id):
    """Get standings for a tournament."""
    standings = tournament_service.get_tournament_standings(tournament_id)
    return jsonify(standings), 200

@bp.route('/<tournament_id>/start', methods=['POST'])
def start_tournament(tournament_id):
    """Start a tournament."""
    success = tournament_service.start_tournament(tournament_id)
    if success:
        return jsonify({'message': 'Tournament started successfully'}), 200
    return jsonify({'error': 'Failed to start tournament'}), 500

@bp.route('/<tournament_id>/end', methods=['POST'])
def end_tournament(tournament_id):
    """End a tournament."""
    success = tournament_service.end_tournament(tournament_id)
    if success:
        return jsonify({'message': 'Tournament ended successfully'}), 200
    return jsonify({'error': 'Failed to end tournament'}), 500
