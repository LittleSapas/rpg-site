from datetime import datetime
from . import db

class Enemy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    stats = db.Column(db.JSON)  # Estatísticas do inimigo
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, campaign_id, name, description=None, stats=None, image_url=None):
        self.campaign_id = campaign_id
        self.name = name
        self.description = description
        self.stats = stats or {}
        self.image_url = image_url

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'name': self.name,
            'description': self.description,
            'stats': self.stats,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 