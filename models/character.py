from . import db
from datetime import datetime

class Character(db.Model):
    __tablename__ = 'characters'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    character_data = db.Column(db.JSON)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    campaign = db.relationship('Campaign', backref='characters')
    user = db.relationship('User', backref='characters')
    logs = db.relationship('CharacterLog', backref='character', lazy=True, cascade='all, delete-orphan')
    initiatives = db.relationship('Initiative', backref='character', lazy=True)
    
    def __repr__(self):
        return f'<Character {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'campaign_id': self.campaign_id,
            'user_id': self.user_id,
            'character_data': self.character_data,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 