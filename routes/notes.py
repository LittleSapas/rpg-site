from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Note, Campaign
from datetime import datetime

notes = Blueprint('notes', __name__)

@notes.route('/api/campaigns/<int:campaign_id>/notes', methods=['GET'])
@login_required
def list_notes(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    category = request.args.get('category')
    query = Note.query.filter_by(campaign_id=campaign_id)
    
    if category:
        query = query.filter_by(category=category)
    
    notes = query.order_by(Note.updated_at.desc()).all()
    return jsonify([note.to_dict() for note in notes])

@notes.route('/api/campaigns/<int:campaign_id>/notes', methods=['POST'])
@login_required
def create_note(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    note = Note(
        campaign_id=campaign_id,
        title=data['title'],
        content=data['content'],
        category=data.get('category')
    )
    
    db.session.add(note)
    db.session.commit()
    
    return jsonify(note.to_dict()), 201

@notes.route('/api/notes/<int:note_id>', methods=['PUT'])
@login_required
def update_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    note.title = data.get('title', note.title)
    note.content = data.get('content', note.content)
    note.category = data.get('category', note.category)
    
    db.session.commit()
    return jsonify(note.to_dict())

@notes.route('/api/notes/<int:note_id>', methods=['DELETE'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(note)
    db.session.commit()
    return '', 204

@notes.route('/api/campaigns/<int:campaign_id>/notes/categories', methods=['GET'])
@login_required
def list_note_categories(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    categories = db.session.query(Note.category)\
        .filter(Note.campaign_id == campaign_id)\
        .filter(Note.category != None)\
        .distinct()\
        .all()
    
    return jsonify([category[0] for category in categories if category[0]]) 