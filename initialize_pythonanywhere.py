import os
import sys
from flask_migrate import upgrade
from app import app, db

def initialize_app():
    print("Iniciando configuração do ambiente...")
    
    # Criar diretório de uploads se não existir
    upload_folder = os.path.join(app.root_path, 'static/uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)
        print(f"Diretório de uploads criado: {upload_folder}")
    
    # Criar diretório de sessões se não existir
    session_folder = os.path.join(app.root_path, 'flask_session')
    if not os.path.exists(session_folder):
        os.makedirs(session_folder)
        print(f"Diretório de sessões criado: {session_folder}")
    
    # Aplicar migrações do banco de dados
    with app.app_context():
        upgrade()
        print("Migrações do banco de dados aplicadas com sucesso")
    
    print("Configuração concluída com sucesso!")

if __name__ == '__main__':
    initialize_app() 