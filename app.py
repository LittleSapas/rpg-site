from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, emit
from datetime import datetime
import os
from dotenv import load_dotenv
from config import Config
from models import init_db, db, User, Campaign, SystemInfo, Character, CharacterLog
from monitoring import setup_monitoring

load_dotenv()

app = Flask(__name__, 
           static_folder='static',
           static_url_path='/static')
app.config.from_object(Config)

socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# Configurar monitoramento
setup_monitoring(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

# Inicialização do banco de dados
init_db(app)

# Importação das rotas
from routes.auth import auth
from routes.campaigns import campaigns
from routes.sessions import sessions
from routes.templates import templates
from routes.enemies import enemies
from routes.notes import notes

# Registro dos blueprints
app.register_blueprint(auth)
app.register_blueprint(campaigns)
app.register_blueprint(sessions)
app.register_blueprint(templates)
app.register_blueprint(enemies)
app.register_blueprint(notes)

# Criação da pasta de uploads se não existir
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Rota de fallback para arquivos estáticos
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

# Eventos do Socket.IO
@socketio.on('connect')
def handle_connect():
    print('Cliente conectado')

@socketio.on('disconnect')
def handle_disconnect():
    print('Cliente desconectado')

@socketio.on('join_session')
def handle_join_session(data):
    session_id = data.get('session_id')
    if session_id:
        socketio.emit('player_joined', {'session_id': session_id}, room=session_id)

@socketio.on('leave_session')
def handle_leave_session(data):
    session_id = data.get('session_id')
    if session_id:
        socketio.emit('player_left', {'session_id': session_id}, room=session_id)

@socketio.on('character_updated')
def handle_character_update(data):
    campaign_id = data.get('campaign_id')
    if campaign_id:
        socketio.emit('character_update', data, room=f'campaign_{campaign_id}')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    socketio.run(app, debug=True) 