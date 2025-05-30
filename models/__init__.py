from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Importar modelos para que o Flask-Migrate os detecte
    from .combat import Combat, Initiative
    from .character import Character
    from .character_log import CharacterLog
    from .campaign import Campaign, SystemInfo
    from .enemy import Enemy
    from .note import Note
    from .session import Session
    from .template import CharacterTemplate
    
    # Criar tabelas
    with app.app_context():
        db.create_all() 

# Importações para facilitar o acesso aos modelos
from .user import User
from .campaign import Campaign
from .character import Character
from .character_log import CharacterLog
from .system_info import SystemInfo
from .character_template import CharacterTemplate
from .session import Session
from .enemy import Enemy 