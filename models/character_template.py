from datetime import datetime
from . import db

class CharacterTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    fields = db.Column(db.JSON, nullable=False)  # Lista de campos e suas configurações
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, campaign_id, name, fields):
        self.campaign_id = campaign_id
        self.name = name
        self.fields = fields

    def to_dict(self):
        return {
            'id': self.id,
            'campaign_id': self.campaign_id,
            'name': self.name,
            'fields': self.fields,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        } 