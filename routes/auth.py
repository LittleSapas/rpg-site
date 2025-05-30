from flask import Blueprint, redirect, url_for, session, request, current_app
from flask_login import login_user, logout_user, current_user
import requests
from models import db, User
import os

auth = Blueprint('auth', __name__)

DISCORD_API_ENDPOINT = 'https://discord.com/api/v10'
DISCORD_CLIENT_ID = os.getenv('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.getenv('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.getenv('DISCORD_REDIRECT_URI')

def get_discord_token(code):
    data = {
        'client_id': DISCORD_CLIENT_ID,
        'client_secret': DISCORD_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': DISCORD_REDIRECT_URI,
        'scope': 'identify guilds'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(f'{DISCORD_API_ENDPOINT}/oauth2/token', data=data, headers=headers)
    return response.json()

def get_discord_user(token):
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(f'{DISCORD_API_ENDPOINT}/users/@me', headers=headers)
    return response.json()

@auth.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    return redirect(f'https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}'
                   f'&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify%20guilds')

@auth.route('/callback')
def callback():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    code = request.args.get('code')
    if not code:
        return redirect(url_for('index'))
    
    try:
        token_data = get_discord_token(code)
        access_token = token_data.get('access_token')
        
        if not access_token:
            return redirect(url_for('index'))
        
        user_data = get_discord_user(access_token)
        discord_id = user_data.get('id')
        
        if not discord_id:
            return redirect(url_for('index'))
        
        user = User.query.filter_by(discord_id=discord_id).first()
        
        if not user:
            user = User(
                discord_id=discord_id,
                username=user_data.get('username'),
                avatar=f'https://cdn.discordapp.com/avatars/{discord_id}/{user_data.get("avatar")}.png'
                if user_data.get('avatar') else None
            )
            db.session.add(user)
            db.session.commit()
        
        session['discord_token'] = access_token
        login_user(user)
        return redirect(url_for('dashboard'))
    
    except Exception as e:
        print(f'Erro na autenticação: {str(e)}')
        return redirect(url_for('index'))

@auth.route('/logout')
def logout():
    session.pop('discord_token', None)
    logout_user()
    return redirect(url_for('index'))

@auth.route('/api/discord/servers')
def get_servers():
    if not current_user.is_authenticated:
        return {'error': 'Não autorizado'}, 401
    
    token = session.get('discord_token')
    if not token:
        return {'error': 'Token não encontrado'}, 401
    
    try:
        headers = {
            'Authorization': f'Bearer {token}'
        }
        response = requests.get(f'{DISCORD_API_ENDPOINT}/users/@me/guilds', headers=headers)
        servers = response.json()
        
        # Filtrar apenas os servidores onde o usuário tem permissões de administrador
        admin_servers = [
            {
                'id': server['id'],
                'name': server['name'],
                'icon_url': f'https://cdn.discordapp.com/icons/{server["id"]}/{server["icon"]}.png'
                if server.get('icon') else '/static/img/default_server.png',
                'member_count': 0  # Isso precisaria de uma chamada adicional para cada servidor
            }
            for server in servers
            if (int(server['permissions']) & 0x8) == 0x8  # Verificar permissão de administrador
        ]
        
        return admin_servers
        
    except Exception as e:
        print(f'Erro ao buscar servidores: {str(e)}')
        return {'error': 'Erro ao buscar servidores'}, 500 