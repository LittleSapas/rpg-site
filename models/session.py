from datetime import datetime
from . import db

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    displayed_fields = db.Column(db.JSON)  # Campos que serão exibidos para cada personagem
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, campaign_id, name, displayed_fields=None):
        self.campaign_id = campaign_id
        self.name = name
        self.displayed_fields = displayed_fields or []

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'name': self.name,
            'is_active': self.is_active,
            'displayed_fields': self.displayed_fields,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 