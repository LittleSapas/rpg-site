from . import db
from datetime import datetime

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    server_id = db.Column(db.String(120), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    character_template = db.Column(db.JSON)
    
    # Relacionamentos
    characters = db.relationship('Character', backref='campaign', lazy=True, cascade='all, delete-orphan')
    system_info = db.relationship('SystemInfo', backref='campaign', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Campaign {self.name}>' 