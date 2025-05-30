from . import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    discord_id = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(120), nullable=False)
    avatar = db.Column(db.String(200))
    
    # Relacionamentos
    campaigns = db.relationship('Campaign', backref='owner', lazy=True)
    characters = db.relationship('Character', backref='user', lazy=True)
    logs = db.relationship('CharacterLog', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>' 