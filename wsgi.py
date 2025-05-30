import eventlet
eventlet.monkey_patch()

import sys
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Adicionar o diretório do projeto ao path
path = os.path.dirname(os.path.abspath(__file__))
if path not in sys.path:
    sys.path.append(path)

# Importar a aplicação
from app import app

# Configurar monitoramento
from monitoring import setup_monitoring
setup_monitoring(app)

# Expor a aplicação para o Gunicorn
application = app 