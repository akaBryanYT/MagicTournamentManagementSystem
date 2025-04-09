"""
Match API routes for the Tournament Management System.
"""

from flask import Blueprint, request, jsonify
from app.services.match_service import MatchService

bp = Blueprint('matches', __name__, url_prefix='/api/matches')
match_service = MatchService()

@bp.route('', methods=['GET'])
def get_matches():
    """Get all matches."""
    tournament_id = request.args.get('tournament_id')
    round_number = request.args.get('round')
    
    if tournament_id and round_number:
        matches = match_service.get_matches_by_tournament_and_round(tournament_id, round_number)
    elif tournament_id:
        matches = match_service.get_matches_by_tournament(tournament_id)
    else:
        matches = match_service.get_all_matches()
    
    return jsonify(matches), 200

@bp.route('/<match_id>', methods=['GET'])
def get_match(match_id):
    """Get match by ID."""
    match = match_service.get_match_by_id(match_id)
    if match:
        return jsonify(match), 200
    return jsonify({'error': 'Match not found'}), 404

@bp.route('', methods=['POST'])
def create_match():
    """Create a new match."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['tournament_id', 'round', 'player1_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Create match
    match_id = match_service.create_match(data)
    if match_id:
        return jsonify({'id': match_id, 'message': 'Match created successfully'}), 201
    return jsonify({'error': 'Failed to create match'}), 500

@bp.route('/<match_id>', methods=['PUT'])
def update_match(match_id):
    """Update match by ID."""
    data = request.get_json()
    
    # Update match
    success = match_service.update_match(match_id, data)
    if success:
        return jsonify({'message': 'Match updated successfully'}), 200
    return jsonify({'error': 'Failed to update match'}), 404

@bp.route('/<match_id>/result', methods=['POST'])
def submit_match_result(match_id):
    """Submit result for a match."""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['player1_wins', 'player2_wins', 'draws']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    # Submit result
    success = match_service.submit_match_result(
        match_id, 
        data['player1_wins'], 
        data['player2_wins'], 
        data['draws']
    )
    
    if success:
        return jsonify({'message': 'Match result submitted successfully'}), 200
    return jsonify({'error': 'Failed to submit match result'}), 500

@bp.route('/<match_id>/start', methods=['POST'])
def start_match(match_id):
    """Start a match."""
    success = match_service.start_match(match_id)
    if success:
        return jsonify({'message': 'Match started successfully'}), 200
    return jsonify({'error': 'Failed to start match'}), 500

@bp.route('/<match_id>/end', methods=['POST'])
def end_match(match_id):
    """End a match."""
    success = match_service.end_match(match_id)
    if success:
        return jsonify({'message': 'Match ended successfully'}), 200
    return jsonify({'error': 'Failed to end match'}), 500

@bp.route('/<match_id>/draw', methods=['POST'])
def draw_match(match_id):
    """Mark a match as intentional draw."""
    success = match_service.draw_match(match_id)
    if success:
        return jsonify({'message': 'Match marked as intentional draw'}), 200
    return jsonify({'error': 'Failed to mark match as intentional draw'}), 500
