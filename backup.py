import os
import shutil
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
import json
from dotenv import load_dotenv

load_dotenv()

def create_local_backup():
    """Cria um backup local do banco de dados e arquivos de upload."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = f'backups/backup_{timestamp}'
    
    # Criar diretório de backup
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup do banco de dados
    shutil.copy2('rpg.db', f'{backup_dir}/rpg.db')
    
    # Backup dos arquivos de upload
    shutil.copytree('static/uploads', f'{backup_dir}/uploads')
    
    print(f"Backup local criado em: {backup_dir}")
    return backup_dir

def upload_to_s3(backup_dir):
    """Faz upload do backup para o Amazon S3."""
    try:
        s3 = boto3.client('s3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        bucket_name = os.getenv('S3_BUCKET_NAME')
        backup_name = os.path.basename(backup_dir)
        
        # Upload do banco de dados
        s3.upload_file(
            f'{backup_dir}/rpg.db',
            bucket_name,
            f'{backup_name}/rpg.db'
        )
        
        # Upload dos arquivos de upload
        for root, dirs, files in os.walk(f'{backup_dir}/uploads'):
            for file in files:
                local_path = os.path.join(root, file)
                s3_path = os.path.join(
                    backup_name,
                    'uploads',
                    os.path.relpath(local_path, f'{backup_dir}/uploads')
                )
                s3.upload_file(local_path, bucket_name, s3_path)
        
        print(f"Backup enviado para S3: {bucket_name}/{backup_name}")
        return True
        
    except ClientError as e:
        print(f"Erro ao fazer upload para S3: {e}")
        return False

def cleanup_old_backups():
    """Remove backups locais antigos (mantém os últimos 5)."""
    backup_dirs = sorted([d for d in os.listdir('backups') if d.startswith('backup_')])
    
    while len(backup_dirs) > 5:
        old_backup = os.path.join('backups', backup_dirs.pop(0))
        shutil.rmtree(old_backup)
        print(f"Backup antigo removido: {old_backup}")

if __name__ == '__main__':
    # Criar diretório de backups se não existir
    os.makedirs('backups', exist_ok=True)
    
    # Criar backup local
    backup_dir = create_local_backup()
    
    # Upload para S3 se as credenciais estiverem configuradas
    if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
        upload_to_s3(backup_dir)
    
    # Limpar backups antigos
    cleanup_old_backups() 