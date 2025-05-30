from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models import db, CharacterTemplate, Campaign
from datetime import datetime

templates = Blueprint('templates', __name__)

@templates.route('/api/campaigns/<int:campaign_id>/templates', methods=['GET'])
@login_required
def list_templates(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    templates = CharacterTemplate.query.filter_by(campaign_id=campaign_id).all()
    return jsonify([template.to_dict() for template in templates])

@templates.route('/api/campaigns/<int:campaign_id>/templates', methods=['POST'])
@login_required
def create_template(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    template = CharacterTemplate(
        campaign_id=campaign_id,
        name=data['name'],
        fields=data['fields']
    )
    
    db.session.add(template)
    db.session.commit()
    
    return jsonify(template.to_dict()), 201

@templates.route('/api/templates/<int:template_id>', methods=['PUT'])
@login_required
def update_template(template_id):
    template = CharacterTemplate.query.get_or_404(template_id)
    if template.campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    template.name = data.get('name', template.name)
    template.fields = data.get('fields', template.fields)
    
    db.session.commit()
    return jsonify(template.to_dict())

@templates.route('/api/templates/<int:template_id>', methods=['DELETE'])
@login_required
def delete_template(template_id):
    template = CharacterTemplate.query.get_or_404(template_id)
    if template.campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(template)
    db.session.commit()
    return '', 204

@templates.route('/api/templates/<int:template_id>/validate', methods=['POST'])
@login_required
def validate_character_data(template_id):
    template = CharacterTemplate.query.get_or_404(template_id)
    data = request.get_json()
    
    validation_errors = []
    for field in template.fields:
        field_name = field['name']
        field_type = field['type']
        required = field.get('required', False)
        
        if required and field_name not in data:
            validation_errors.append(f"Campo obrigatório '{field_name}' não encontrado")
            continue
            
        if field_name in data:
            value = data[field_name]
            
            # Validação por tipo
            if field_type == 'number':
                try:
                    float(value)
                except (ValueError, TypeError):
                    validation_errors.append(f"Campo '{field_name}' deve ser um número")
            elif field_type == 'boolean':
                if not isinstance(value, bool):
                    validation_errors.append(f"Campo '{field_name}' deve ser um booleano")
            elif field_type == 'string':
                if not isinstance(value, str):
                    validation_errors.append(f"Campo '{field_name}' deve ser uma string")
            
            # Validações adicionais
            if 'min' in field and isinstance(value, (int, float)):
                if value < field['min']:
                    validation_errors.append(f"Campo '{field_name}' deve ser maior que {field['min']}")
            if 'max' in field and isinstance(value, (int, float)):
                if value > field['max']:
                    validation_errors.append(f"Campo '{field_name}' deve ser menor que {field['max']}")
            if 'pattern' in field and isinstance(value, str):
                import re
                if not re.match(field['pattern'], value):
                    validation_errors.append(f"Campo '{field_name}' não corresponde ao padrão esperado")
    
    if validation_errors:
        return jsonify({'errors': validation_errors}), 400
    return jsonify({'valid': True}) 