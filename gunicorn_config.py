import multiprocessing
import os

# Configurações do servidor
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "eventlet"
threads = 2
timeout = 120

# Configurações de logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Configurações do processo
daemon = False
pidfile = "gunicorn.pid"
user = None
group = None

# Configurações do worker
worker_tmp_dir = "/dev/shm"
worker_connections = 1000
keepalive = 2

# Configurações do hook
def on_starting(server):
    """Log quando o servidor estiver iniciando."""
    server.log.info("Iniciando servidor Gunicorn...")

def on_reload(server):
    """Log quando o servidor for recarregado."""
    server.log.info("Recarregando servidor Gunicorn...") 