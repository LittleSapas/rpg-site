from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from ..models.combat import Combat, Initiative
from ..models import db
from ..models.character import Character
from ..models.enemy import Enemy
from ..socketio import socketio

bp = Blueprint('combat', __name__)

@bp.route('/api/sessions/<int:session_id>/combat', methods=['POST'])
@login_required
def create_combat(session_id):
    combat = Combat(session_id=session_id)
    db.session.add(combat)
    db.session.commit()
    
    socketio.emit('combat_started', {'combat_id': combat.id}, room=f'session_{session_id}')
    return jsonify({"message": "Combate iniciado", "combat_id": combat.id}), 201

@bp.route('/api/combat/<int:combat_id>/initiative', methods=['POST'])
@login_required
def add_initiative(combat_id):
    data = request.json
    initiative = Initiative(
        combat_id=combat_id,
        character_id=data.get('character_id'),
        enemy_id=data.get('enemy_id'),
        initiative_value=data['initiative_value'],
        current_hp=data.get('current_hp'),
        max_hp=data.get('max_hp'),
        position_x=data.get('position_x'),
        position_y=data.get('position_y')
    )
    db.session.add(initiative)
    db.session.commit()
    
    combat = Combat.query.get_or_404(combat_id)
    socketio.emit('initiative_added', initiative.to_dict(), room=f'session_{combat.session_id}')
    return jsonify(initiative.to_dict()), 201

@bp.route('/api/combat/<int:combat_id>/next-turn', methods=['POST'])
@login_required
def next_turn(combat_id):
    combat = Combat.query.get_or_404(combat_id)
    initiatives = Initiative.query.filter_by(combat_id=combat_id).order_by(Initiative.initiative_value.desc()).all()
    
    if not initiatives:
        return jsonify({"error": "Não há participantes no combate"}), 400
    
    combat.current_turn = (combat.current_turn + 1) % len(initiatives)
    if combat.current_turn == 0:
        combat.round_number += 1
    
    db.session.commit()
    
    current_initiative = initiatives[combat.current_turn].to_dict()
    turn_data = {
        "round": combat.round_number,
        "current_turn": combat.current_turn,
        "current_initiative": current_initiative
    }
    
    socketio.emit('turn_changed', turn_data, room=f'session_{combat.session_id}')
    return jsonify(turn_data)

@bp.route('/api/combat/<int:combat_id>/update-hp', methods=['POST'])
@login_required
def update_hp(combat_id):
    data = request.json
    initiative = Initiative.query.get_or_404(data['initiative_id'])
    initiative.current_hp = data['current_hp']
    db.session.commit()
    
    combat = Combat.query.get_or_404(combat_id)
    socketio.emit('hp_updated', initiative.to_dict(), room=f'session_{combat.session_id}')
    return jsonify(initiative.to_dict())

@bp.route('/api/combat/<int:combat_id>/conditions', methods=['POST'])
@login_required
def update_conditions(combat_id):
    data = request.json
    initiative = Initiative.query.get_or_404(data['initiative_id'])
    initiative.conditions = data['conditions']
    db.session.commit()
    
    combat = Combat.query.get_or_404(combat_id)
    socketio.emit('conditions_updated', initiative.to_dict(), room=f'session_{combat.session_id}')
    return jsonify(initiative.to_dict())

@bp.route('/api/combat/<int:combat_id>/end', methods=['POST'])
@login_required
def end_combat(combat_id):
    combat = Combat.query.get_or_404(combat_id)
    combat.is_active = False
    db.session.commit()
    
    socketio.emit('combat_ended', {'combat_id': combat_id}, room=f'session_{combat.session_id}')
    return jsonify({"message": "Combate finalizado"})

@bp.route('/api/combat/<int:combat_id>/move', methods=['POST'])
@login_required
def move_character(combat_id):
    data = request.json
    initiative = Initiative.query.get_or_404(data['initiative_id'])
    
    # Verificar se é o turno do personagem
    combat = Combat.query.get_or_404(combat_id)
    initiatives = Initiative.query.filter_by(combat_id=combat_id).order_by(Initiative.initiative_value.desc()).all()
    current_initiative = initiatives[combat.current_turn]
    
    if initiative.id != current_initiative.id:
        return jsonify({"error": "Não é o turno deste personagem"}), 400
    
    # Atualizar posição
    initiative.position_x = data['position_x']
    initiative.position_y = data['position_y']
    db.session.commit()
    
    socketio.emit('character_moved', initiative.to_dict(), room=f'session_{combat.session_id}')
    return jsonify(initiative.to_dict()) 