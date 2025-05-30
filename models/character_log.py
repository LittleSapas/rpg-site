from . import db
from datetime import datetime

class CharacterLog(db.Model):
    __tablename__ = 'character_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    character_id = db.Column(db.Integer, db.ForeignKey('characters.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    change_description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_master = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    character = db.relationship('Character', backref='logs')
    user = db.relationship('User', backref='character_logs')
    
    def __repr__(self):
        return f'<CharacterLog {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'character_id': self.character_id,
            'user_id': self.user_id,
            'user_name': self.user.username,
            'change_description': self.change_description,
            'timestamp': self.timestamp.isoformat(),
            'is_master': self.is_master
        } 