import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime
import psutil
import json
from flask import request, current_app

def setup_logging(app):
    """Configura o sistema de logging da aplicação."""
    # Criar diretório de logs se não existir
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Configurar handler para arquivo
    file_handler = RotatingFileHandler(
        'logs/app.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
    ))
    file_handler.setLevel(logging.INFO)
    
    # Adicionar handlers ao app
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    # Log de inicialização
    app.logger.info('Aplicação iniciada')

def log_request():
    """Log de requisições HTTP."""
    current_app.logger.info(
        f'Request: {request.method} {request.url} - '
        f'IP: {request.remote_addr} - '
        f'User Agent: {request.user_agent}'
    )

def monitor_system():
    """Monitora recursos do sistema."""
    stats = {
        'timestamp': datetime.now().isoformat(),
        'cpu_percent': psutil.cpu_percent(),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent
    }
    
    # Salvar estatísticas
    with open('logs/system_stats.json', 'a') as f:
        json.dump(stats, f)
        f.write('\n')
    
    # Alertar se recursos estiverem críticos
    if stats['cpu_percent'] > 90:
        current_app.logger.warning('CPU usage critical: %d%%', stats['cpu_percent'])
    if stats['memory_percent'] > 90:
        current_app.logger.warning('Memory usage critical: %d%%', stats['memory_percent'])
    if stats['disk_percent'] > 90:
        current_app.logger.warning('Disk usage critical: %d%%', stats['disk_percent'])

def log_error(error):
    """Log de erros detalhado."""
    current_app.logger.error(
        'Error: %s\nTraceback: %s',
        str(error),
        error.__traceback__
    )

def setup_monitoring(app):
    """Configura todo o sistema de monitoramento."""
    setup_logging(app)
    
    # Registrar função para log de requisições
    app.before_request(log_request)
    
    # Registrar função para log de erros
    app.errorhandler(Exception)(log_error)
    
    # Configurar monitoramento periódico do sistema
    if not app.debug:
        from apscheduler.schedulers.background import BackgroundScheduler
        scheduler = BackgroundScheduler()
        scheduler.add_job(
            monitor_system,
            'interval',
            minutes=5
        )
        scheduler.start() 