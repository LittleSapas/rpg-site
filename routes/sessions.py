from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Session, Campaign, Character
from datetime import datetime

sessions = Blueprint('sessions', __name__)

@sessions.route('/api/campaigns/<int:campaign_id>/sessions', methods=['GET'])
@login_required
def list_sessions(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    sessions = Session.query.filter_by(campaign_id=campaign_id).all()
    return jsonify([session.to_dict() for session in sessions])

@sessions.route('/api/campaigns/<int:campaign_id>/sessions', methods=['POST'])
@login_required
def create_session(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    session = Session(
        campaign_id=campaign_id,
        name=data['name'],
        displayed_fields=data.get('displayed_fields', [])
    )
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify(session.to_dict()), 201

@sessions.route('/api/sessions/<int:session_id>', methods=['PUT'])
@login_required
def update_session(session_id):
    session = Session.query.get_or_404(session_id)
    if session.campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    session.name = data.get('name', session.name)
    session.displayed_fields = data.get('displayed_fields', session.displayed_fields)
    session.is_active = data.get('is_active', session.is_active)
    
    db.session.commit()
    return jsonify(session.to_dict())

@sessions.route('/api/sessions/<int:session_id>', methods=['DELETE'])
@login_required
def delete_session(session_id):
    session = Session.query.get_or_404(session_id)
    if session.campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(session)
    db.session.commit()
    return '', 204

@sessions.route('/api/sessions/<int:session_id>/characters', methods=['GET'])
@login_required
def get_session_characters(session_id):
    session = Session.query.get_or_404(session_id)
    characters = Character.query.filter_by(campaign_id=session.campaign_id).all()
    
    character_data = []
    for character in characters:
        data = character.to_dict()
        # Filtrar apenas os campos que devem ser exibidos na sessão
        if session.displayed_fields:
            filtered_data = {}
            for field in session.displayed_fields:
                if field in data['character_data']:
                    filtered_data[field] = data['character_data'][field]
            data['character_data'] = filtered_data
        character_data.append(data)
    
    return jsonify(character_data) 