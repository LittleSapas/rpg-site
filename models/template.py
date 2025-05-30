from . import db
from datetime import datetime

class CharacterTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    system_type = db.Column(db.String(50), nullable=False)  # D&D 5e, Pathfinder, etc.
    template_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    user = db.relationship('User', backref='character_templates')
    
    def __repr__(self):
        return f'<CharacterTemplate {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'system_type': self.system_type,
            'template_data': self.template_data,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'user_id': self.user_id,
            'is_public': self.is_public,
            'creator': self.user.username
        } 