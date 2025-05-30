from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, Campaign, SystemInfo, Character, CharacterLog
from datetime import datetime

campaigns = Blueprint('campaigns', __name__)

@campaigns.route('/campaigns/<server_id>')
@login_required
def server_campaigns(server_id):
    campaigns_list = Campaign.query.filter_by(server_id=server_id).all()
    return render_template('campaigns/list.html', campaigns=campaigns_list, server_id=server_id)

@campaigns.route('/campaign/new/<server_id>', methods=['GET', 'POST'])
@login_required
def new_campaign(server_id):
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Nome da campanha é obrigatório', 'danger')
            return redirect(url_for('campaigns.new_campaign', server_id=server_id))
        
        campaign = Campaign(
            name=name,
            server_id=server_id,
            owner_id=current_user.id
        )
        
        db.session.add(campaign)
        db.session.commit()
        
        flash('Campanha criada com sucesso!', 'success')
        return redirect(url_for('campaigns.campaign_dashboard', campaign_id=campaign.id))
    
    return render_template('campaigns/new.html', server_id=server_id)

@campaigns.route('/campaign/<campaign_id>')
@login_required
def campaign_dashboard(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Verificar se o usuário tem acesso à campanha
    if campaign.owner_id != current_user.id:
        flash('Você não tem permissão para acessar esta campanha', 'danger')
        return redirect(url_for('index'))
    
    characters = Character.query.filter_by(campaign_id=campaign_id).all()
    system_info = SystemInfo.query.filter_by(campaign_id=campaign_id).all()
    
    return render_template('campaigns/dashboard.html',
                         campaign=campaign,
                         characters=characters,
                         system_info=system_info)

@campaigns.route('/campaign/<campaign_id>/system', methods=['GET', 'POST'])
@login_required
def manage_system(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Não autorizado'}), 401
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            return jsonify({'error': 'Título e conteúdo são obrigatórios'}), 400
        
        system_info = SystemInfo(
            campaign_id=campaign_id,
            title=title,
            content=content
        )
        
        db.session.add(system_info)
        db.session.commit()
        
        return jsonify({
            'id': system_info.id,
            'title': system_info.title,
            'content': system_info.content
        })
    
    system_info = SystemInfo.query.filter_by(campaign_id=campaign_id).all()
    return render_template('campaigns/system.html', campaign=campaign, system_info=system_info)

@campaigns.route('/campaign/<campaign_id>/character-template', methods=['GET', 'POST'])
@login_required
def manage_character_template(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Não autorizado'}), 401
    
    if request.method == 'POST':
        template_data = request.get_json()
        campaign.character_template = template_data
        db.session.commit()
        
        return jsonify({'message': 'Template atualizado com sucesso'})
    
    return render_template('campaigns/character_template.html',
                         campaign=campaign,
                         template=campaign.character_template)

@campaigns.route('/campaign/<campaign_id>/session')
@login_required
def virtual_session(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    characters = Character.query.filter_by(campaign_id=campaign_id).all()
    
    return render_template('campaigns/session.html',
                         campaign=campaign,
                         characters=characters)

@campaigns.route('/api/campaign/<campaign_id>/logs')
@login_required
def get_character_logs(campaign_id):
    character_id = request.args.get('character_id')
    
    if not character_id:
        return jsonify({'error': 'ID do personagem é obrigatório'}), 400
    
    logs = CharacterLog.query.filter_by(character_id=character_id)\
        .order_by(CharacterLog.timestamp.desc())\
        .limit(50)\
        .all()
    
    return jsonify([{
        'id': log.id,
        'user_id': log.user_id,
        'change_description': log.change_description,
        'timestamp': log.timestamp.isoformat(),
        'is_master': log.is_master
    } for log in logs])

@campaigns.route('/api/campaign/<campaign_id>/character/<character_id>', methods=['PUT'])
@login_required
def update_character(campaign_id, character_id):
    character = Character.query.get_or_404(character_id)
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Verificar permissões
    if character.user_id != current_user.id and campaign.owner_id != current_user.id:
        return jsonify({'error': 'Não autorizado'}), 401
    
    data = request.get_json()
    
    # Atualizar dados do personagem
    character.character_data.update(data)
    
    # Registrar log
    log = CharacterLog(
        character_id=character_id,
        user_id=current_user.id,
        change_description=f"Atualizou informações do personagem",
        is_master=(current_user.id == campaign.owner_id)
    )
    
    db.session.add(log)
    db.session.commit()
    
    return jsonify({
        'message': 'Personagem atualizado com sucesso',
        'character': character.character_data
    }) 