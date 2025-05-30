from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

# Importar modelos
from .user import User
from .campaign import Campaign
from .system_info import SystemInfo
from .character import Character
from .character_log import CharacterLog
from .enemy import Enemy
from .session import Session
from .combat import Combat, Initiative
from .template import CharacterTemplate

def init_db(app):
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Criar tabelas
    with app.app_context():
        db.create_all()

# Exportar modelos
__all__ = [
    'db',
    'init_db',
    'User',
    'Campaign',
    'SystemInfo',
    'Character',
    'CharacterLog',
    'Enemy',
    'Session',
    'Combat',
    'Initiative',
    'CharacterTemplate'
]

# Garantir que os modelos estejam disponíveis no namespace do módulo
globals().update({name: globals()[name] for name in __all__ if name in globals()}) 