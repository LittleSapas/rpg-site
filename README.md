# RPG Manager

Um sistema web para gerenciamento de campanhas de RPG integrado com o Discord.

## Funcionalidades

- Autenticação via Discord
- Gerenciamento de campanhas por servidor
- Sistema de fichas personalizáveis
- Logs de alterações em tempo real
- Área do mestre com controle total
- Sistema de anotações e regras
- Sessão virtual com informações dos jogadores
- Interface responsiva para todos os dispositivos

## Requisitos

- Python 3.8+
- Flask
- SQLAlchemy
- Flask-SocketIO
- Discord Developer Application

## Configuração

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd rpg-manager
```

2. Crie um ambiente virtual e ative-o:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```
SECRET_KEY=sua-chave-secreta
DISCORD_CLIENT_ID=seu-client-id-do-discord
DISCORD_CLIENT_SECRET=seu-client-secret-do-discord
DISCORD_REDIRECT_URI=http://seu-dominio/callback
DATABASE_URL=sqlite:///rpg.db
```

5. Configure sua aplicação Discord:
- Acesse o [Discord Developer Portal](https://discord.com/developers/applications)
- Crie uma nova aplicação
- Em "OAuth2", adicione seu redirect URI
- Copie o Client ID e Client Secret para o arquivo `.env`

6. Inicialize o banco de dados:
```bash
flask db upgrade
```

7. Execute o servidor de desenvolvimento:
```bash
flask run
```

## Configuração para Produção (PythonAnywhere)

1. Faça login no PythonAnywhere

2. Vá para a seção "Web" e crie uma nova aplicação web
   - Escolha Flask como framework
   - Python 3.8 ou superior

3. Configure o virtualenv:
```bash
mkvirtualenv --python=/usr/bin/python3.8 rpg-manager
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente no arquivo `web_app.py`:
```python
import os
os.environ['SECRET_KEY'] = 'sua-chave-secreta'
os.environ['DISCORD_CLIENT_ID'] = 'seu-client-id'
os.environ['DISCORD_CLIENT_SECRET'] = 'seu-client-secret'
os.environ['DISCORD_REDIRECT_URI'] = 'https://seu-dominio.pythonanywhere.com/callback'
os.environ['DATABASE_URL'] = 'sqlite:///rpg.db'
```

5. Configure o WSGI file:
```python
import sys
path = '/home/seu-usuario/rpg-manager'
if path not in sys.path:
    sys.path.append(path)

from app import app as application
```

6. Reinicie sua aplicação web

## Uso

1. Acesse o site e faça login com sua conta Discord
2. Selecione um servidor onde você é administrador
3. Crie uma nova campanha
4. Configure o template de ficha de personagem
5. Adicione as regras do sistema
6. Convide os jogadores
7. Gerencie as fichas e acompanhe as alterações

## Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.

## Contato

Seu Nome - [@seu_twitter](https://twitter.com/seu_twitter)

Link do Projeto: [https://github.com/seu-usuario/rpg-manager](https://github.com/seu-usuario/rpg-manager) 