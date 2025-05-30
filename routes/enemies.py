from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, Enemy, Campaign
from datetime import datetime
import os
from werkzeug.utils import secure_filename

enemies = Blueprint('enemies', __name__)

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@enemies.route('/api/campaigns/<int:campaign_id>/enemies', methods=['GET'])
@login_required
def list_enemies(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    enemies = Enemy.query.filter_by(campaign_id=campaign_id).all()
    return jsonify([enemy.to_dict() for enemy in enemies])

@enemies.route('/api/campaigns/<int:campaign_id>/enemies', methods=['POST'])
@login_required
def create_enemy(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.form
    enemy = Enemy(
        campaign_id=campaign_id,
        name=data['name'],
        description=data.get('description'),
        stats=data.get('stats', {})
    )
    
    # Processar imagem se enviada
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            enemy.image_url = url_for('static', filename=f'uploads/{filename}')
    
    db.session.add(enemy)
    db.session.commit()
    
    return jsonify(enemy.to_dict()), 201

@enemies.route('/api/enemies/<int:enemy_id>', methods=['PUT'])
@login_required
def update_enemy(enemy_id):
    enemy = Enemy.query.get_or_404(enemy_id)
    if enemy.campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.form
    enemy.name = data.get('name', enemy.name)
    enemy.description = data.get('description', enemy.description)
    enemy.stats = data.get('stats', enemy.stats)
    
    # Processar nova imagem se enviada
    if 'image' in request.files:
        file = request.files['image']
        if file and allowed_file(file.filename):
            # Remover imagem antiga se existir
            if enemy.image_url:
                old_filename = enemy.image_url.split('/')[-1]
                old_path = os.path.join(current_app.config['UPLOAD_FOLDER'], old_filename)
                if os.path.exists(old_path):
                    os.remove(old_path)
            
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{filename}"
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            enemy.image_url = url_for('static', filename=f'uploads/{filename}')
    
    db.session.commit()
    return jsonify(enemy.to_dict())

@enemies.route('/api/enemies/<int:enemy_id>', methods=['DELETE'])
@login_required
def delete_enemy(enemy_id):
    enemy = Enemy.query.get_or_404(enemy_id)
    if enemy.campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Remover imagem se existir
    if enemy.image_url:
        filename = enemy.image_url.split('/')[-1]
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
    
    db.session.delete(enemy)
    db.session.commit()
    return '', 204 