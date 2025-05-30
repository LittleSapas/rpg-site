from datetime import datetime
from . import db

class Combat(db.Model):
    __tablename__ = 'combats'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    round_number = db.Column(db.Integer, default=1)
    current_turn = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    session = db.relationship('Session')
    initiatives = db.relationship('Initiative', backref='combat', cascade='all, delete-orphan')

class Initiative(db.Model):
    __tablename__ = 'initiatives'
    
    id = db.Column(db.Integer, primary_key=True)
    combat_id = db.Column(db.Integer, db.ForeignKey('combats.id'), nullable=False)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=True)
    enemy_id = db.Column(db.Integer, db.ForeignKey('enemies.id'), nullable=True)
    initiative_value = db.Column(db.Integer, nullable=False)
    current_hp = db.Column(db.Integer)
    max_hp = db.Column(db.Integer)
    conditions = db.Column(db.JSON, default=list)
    position_x = db.Column(db.Integer)
    position_y = db.Column(db.Integer)
    
    def to_dict(self):
        return {
            'id': self.id,
            'combat_id': self.combat_id,
            'character_id': self.character_id,
            'enemy_id': self.enemy_id,
            'initiative_value': self.initiative_value,
            'current_hp': self.current_hp,
            'max_hp': self.max_hp,
            'conditions': self.conditions,
            'position': {'x': self.position_x, 'y': self.position_y}
        } 