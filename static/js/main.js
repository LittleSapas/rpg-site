// Configuração do Socket.IO
const socket = io();

// Gerenciamento de estado
let currentCampaign = null;
let currentCharacter = null;

// Funções de utilidade
function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed bottom-0 end-0 m-3`;
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 5000);
}

// Eventos do Socket.IO
socket.on('connect', () => {
    console.log('Conectado ao servidor');
});

socket.on('disconnect', () => {
    console.log('Desconectado do servidor');
});

socket.on('character_update', (data) => {
    if (data.campaign_id === currentCampaign) {
        updateCharacterCard(data);
        showToast(`Personagem ${data.name} foi atualizado!`, 'info');
    }
});

socket.on('player_joined', (data) => {
    showNotification('success', `${data.username} entrou na sessão`);
});

socket.on('player_left', (data) => {
    showNotification('info', `${data.username} saiu da sessão`);
});

// Funções de atualização da UI
function updateCharacterCard(characterData) {
    const card = document.querySelector(`#character-${characterData.id}`);
    if (card) {
        // Atualizar informações do personagem
        card.querySelector('.character-name').textContent = characterData.name;
        card.querySelector('.character-image').src = characterData.image_url;
        
        // Atualizar campos dinâmicos
        Object.entries(characterData.fields).forEach(([key, value]) => {
            const field = card.querySelector(`[data-field="${key}"]`);
            if (field) {
                field.textContent = value;
            }
        });
    }
}

function appendLogEntry(logData) {
    const logsContainer = document.getElementById('character-logs');
    if (logsContainer) {
        const logEntry = document.createElement('div');
        logEntry.className = `log-entry ${logData.is_master ? 'master' : 'player'} fade-in`;
        logEntry.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <strong>${logData.user_name}</strong>
                <small>${new Date(logData.timestamp).toLocaleString()}</small>
            </div>
            <p class="mb-0">${logData.change_description}</p>
        `;
        logsContainer.insertBefore(logEntry, logsContainer.firstChild);
    }
}

// Funções de interação com formulários
function setupCharacterForm() {
    const form = document.getElementById('character-form');
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            showLoading();

            const formData = new FormData(form);
            try {
                const response = await fetch('/api/character/save', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const data = await response.json();
                    showToast('Personagem salvo com sucesso!', 'success');
                    socket.emit('character_updated', data);
                } else {
                    throw new Error('Erro ao salvar personagem');
                }
            } catch (error) {
                showToast('Erro ao salvar personagem', 'danger');
                console.error(error);
            } finally {
                hideLoading();
            }
        });
    }
}

// Funções de sessão virtual
function initializeSession(sessionId) {
    const sessionArea = document.getElementById('session-area');
    if (sessionArea) {
        socket.emit('join_session', { session_id: sessionId });
        
        // Atualizar status dos jogadores
        socket.on('player_status_update', (data) => {
            updatePlayerStatus(data);
        });
    }
}

function updatePlayerStatus(playerData) {
    const playerCard = document.querySelector(`#player-${playerData.id}`);
    if (playerCard) {
        playerCard.querySelector('.player-status').className = 
            `player-status ${playerData.online ? 'text-success' : 'text-danger'}`;
        
        // Atualizar informações visíveis
        playerData.visible_fields.forEach(field => {
            const fieldElement = playerCard.querySelector(`[data-field="${field.name}"]`);
            if (fieldElement) {
                fieldElement.textContent = field.value;
            }
        });
    }
}

// Funções de Utilidade
function showNotification(type, message) {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show m-3" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', alertHtml);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function sanitizeHTML(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Funções de Upload
function handleImageUpload(file, callback) {
    const formData = new FormData();
    formData.append('image', file);

    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.url) {
            callback(data.url);
        } else {
            showNotification('error', 'Erro ao fazer upload da imagem');
        }
    })
    .catch(error => {
        console.error('Erro ao fazer upload:', error);
        showNotification('error', 'Erro ao fazer upload da imagem');
    });
}

// Funções de Markdown
function initMarkdownEditor(elementId, options = {}) {
    return new EasyMDE({
        element: document.getElementById(elementId),
        spellChecker: false,
        status: false,
        toolbar: [
            'bold', 'italic', 'heading',
            '|', 'quote', 'unordered-list', 'ordered-list',
            '|', 'link', 'image',
            '|', 'preview', 'side-by-side', 'fullscreen',
            '|', 'guide'
        ],
        theme: 'dark',
        ...options
    });
}

function renderMarkdown(text) {
    return marked.parse(text, {
        gfm: true,
        breaks: true,
        sanitize: true
    });
}

// Funções de Rolagem de Dados
function rollDice(sides) {
    const result = Math.floor(Math.random() * sides) + 1;
    const diceLog = document.getElementById('diceLog');
    
    if (diceLog) {
        const rollHtml = `
            <div class="dice-result">
                <span class="roll-type">d${sides}:</span>
                <span class="roll-value">${result}</span>
            </div>
        `;
        diceLog.insertAdjacentHTML('afterbegin', rollHtml);
        
        // Limitar o número de resultados exibidos
        while (diceLog.children.length > 10) {
            diceLog.lastChild.remove();
        }
        
        // Emitir o resultado para outros jogadores
        socket.emit('dice_rolled', {
            type: sides,
            result: result
        });
    }
    
    return result;
}

// Funções de Dropzone
function initDropzone(elementId, options = {}) {
    return new Dropzone(`#${elementId}`, {
        url: '/api/upload',
        acceptedFiles: 'image/*,.pdf,.doc,.docx',
        maxFilesize: 5, // MB
        addRemoveLinks: true,
        dictDefaultMessage: 'Arraste arquivos aqui ou clique para fazer upload',
        dictRemoveFile: 'Remover',
        dictCancelUpload: 'Cancelar',
        dictUploadCanceled: 'Upload cancelado',
        dictFileTooBig: 'Arquivo muito grande ({{filesize}}MB). Tamanho máximo: {{maxFilesize}}MB',
        dictInvalidFileType: 'Tipo de arquivo inválido',
        ...options
    });
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    setupCharacterForm();
    
    // Inicializar tooltips
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => new bootstrap.Tooltip(tooltip));
    
    // Inicializar popovers
    const popovers = document.querySelectorAll('[data-bs-toggle="popover"]');
    popovers.forEach(popover => new bootstrap.Popover(popover));
    
    // Configurar inputs de imagem
    const imageInputs = document.querySelectorAll('input[type="file"][accept="image/*"]');
    imageInputs.forEach(input => {
        input.addEventListener('change', (event) => {
            const file = event.target.files[0];
            if (file) {
                const preview = document.querySelector(input.dataset.preview);
                if (preview) {
                    const reader = new FileReader();
                    reader.onload = e => preview.src = e.target.result;
                    reader.readAsDataURL(file);
                }
            }
        });
    });
    
    // Verificar se estamos em uma sessão
    const sessionId = document.body.dataset.sessionId;
    if (sessionId) {
        initializeSession(sessionId);
    }
}); 