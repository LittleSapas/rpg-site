from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Importar modelos para que o Flask-Migrate os detecte
    from .user import User
    from .campaign import Campaign
    from .system_info import SystemInfo
    from .character import Character
    from .character_log import CharacterLog
    from .combat import Combat, Initiative
    from .enemy import Enemy
    from .note import Note
    from .session import Session
    from .template import CharacterTemplate
    
    # Criar tabelas
    with app.app_context():
        db.create_all()

# Exportar modelos
__all__ = [
    'User',
    'Campaign',
    'SystemInfo',
    'Character',
    'CharacterLog',
    'Combat',
    'Initiative',
    'Enemy',
    'Note',
    'Session',
    'CharacterTemplate'
] 