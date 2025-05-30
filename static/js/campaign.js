// Variáveis Globais
let currentCampaign = null;
let activeSession = null;
let editors = {};

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    // Obter ID da campanha da URL
    const campaignId = window.location.pathname.split('/').pop();
    currentCampaign = campaignId;
    
    // Carregar dados iniciais
    loadCharacters();
    loadSystemSections();
    loadNotes();
    loadEnemies();
    loadLogs();
    
    // Inicializar editores Markdown
    editors.system = initMarkdownEditor('systemContent');
    editors.note = initMarkdownEditor('noteContent');
    
    // Inicializar Dropzones
    initDropzone('systemAttachments', {
        success: function(file, response) {
            file.previewElement.querySelector('.dz-filename').innerHTML = `
                <span class="text-light">${response.filename}</span>
            `;
        }
    });
    
    initDropzone('noteAttachments', {
        success: function(file, response) {
            file.previewElement.querySelector('.dz-filename').innerHTML = `
                <span class="text-light">${response.filename}</span>
            `;
        }
    });
});

// Funções de Carregamento
async function loadCharacters() {
    try {
        const response = await fetch(`/api/campaigns/${currentCampaign}/characters`);
        const characters = await response.json();
        
        const charactersList = document.getElementById('characters-list');
        charactersList.innerHTML = characters.map(character => `
            <div class="col-md-6 col-lg-4">
                <div class="card bg-dark border-secondary h-100">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <img src="${character.image_url || '/static/img/default_character.png'}" 
                                 alt="${sanitizeHTML(character.name)}" 
                                 class="rounded-circle me-2"
                                 width="48" height="48">
                            <div>
                                <h5 class="card-title mb-0">${sanitizeHTML(character.name)}</h5>
                                <small class="text-muted">${sanitizeHTML(character.user.username)}</small>
                            </div>
                        </div>
                        <div class="mb-3">
                            ${Object.entries(character.character_data)
                                .filter(([key]) => key !== 'description')
                                .map(([key, value]) => `
                                    <span class="badge bg-secondary me-1">${sanitizeHTML(key)}: ${sanitizeHTML(value.toString())}</span>
                                `).join('')}
                        </div>
                        <div class="d-flex justify-content-between align-items-center">
                            <button class="btn btn-primary btn-sm" onclick="viewCharacter(${character.id})">
                                <i class="fas fa-eye me-1"></i>Ver
                            </button>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary" onclick="editCharacter(${character.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-outline-danger" onclick="deleteCharacter(${character.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('') || `
            <div class="col-12">
                <div class="text-center py-5">
                    <i class="fas fa-users fa-3x mb-3 text-muted"></i>
                    <h3>Nenhum personagem encontrado</h3>
                    <p class="text-muted">Clique em "Novo Personagem" para começar!</p>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Erro ao carregar personagens:', error);
        showNotification('error', 'Erro ao carregar personagens');
    }
}

async function loadSystemSections() {
    try {
        const response = await fetch(`/api/campaigns/${currentCampaign}/system`);
        const sections = await response.json();
        
        const systemSections = document.getElementById('system-sections');
        systemSections.innerHTML = sections.map(section => `
            <div class="card bg-dark border-secondary mb-3">
                <div class="card-body">
                    <h5 class="card-title">${sanitizeHTML(section.title)}</h5>
                    <div class="markdown-body mb-3">
                        ${renderMarkdown(section.content)}
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <small class="text-muted">
                            Atualizado em ${formatDate(section.updated_at)}
                        </small>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="editSystem(${section.id})">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="deleteSystem(${section.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `).join('') || `
            <div class="text-center py-5">
                <i class="fas fa-book fa-3x mb-3 text-muted"></i>
                <h3>Nenhuma seção encontrada</h3>
                <p class="text-muted">Clique em "Nova Seção" para começar!</p>
            </div>
        `;
    } catch (error) {
        console.error('Erro ao carregar seções do sistema:', error);
        showNotification('error', 'Erro ao carregar seções do sistema');
    }
}

async function loadNotes() {
    try {
        const response = await fetch(`/api/campaigns/${currentCampaign}/notes`);
        const notes = await response.json();
        
        const notesList = document.getElementById('notes-list');
        notesList.innerHTML = notes.map(note => `
            <div class="col-md-6 col-lg-4">
                <div class="card bg-dark border-secondary h-100">
                    <div class="card-body">
                        <h5 class="card-title">${sanitizeHTML(note.title)}</h5>
                        ${note.category ? `
                            <span class="badge bg-secondary mb-2">${sanitizeHTML(note.category)}</span>
                        ` : ''}
                        <div class="markdown-body mb-3">
                            ${renderMarkdown(note.content.substring(0, 200))}
                            ${note.content.length > 200 ? '...' : ''}
                        </div>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                ${formatDate(note.updated_at)}
                            </small>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary" onclick="viewNote(${note.id})">
                                    <i class="fas fa-eye"></i>
                                </button>
                                <button class="btn btn-outline-danger" onclick="deleteNote(${note.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('') || `
            <div class="col-12">
                <div class="text-center py-5">
                    <i class="fas fa-sticky-note fa-3x mb-3 text-muted"></i>
                    <h3>Nenhuma anotação encontrada</h3>
                    <p class="text-muted">Clique em "Nova Anotação" para começar!</p>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Erro ao carregar anotações:', error);
        showNotification('error', 'Erro ao carregar anotações');
    }
}

async function loadEnemies() {
    try {
        const response = await fetch(`/api/campaigns/${currentCampaign}/enemies`);
        const enemies = await response.json();
        
        const enemiesList = document.getElementById('enemies-list');
        enemiesList.innerHTML = enemies.map(enemy => `
            <div class="col-md-6 col-lg-4">
                <div class="card bg-dark border-secondary h-100">
                    <div class="card-body">
                        <div class="d-flex align-items-center mb-3">
                            <img src="${enemy.image_url || '/static/img/default_enemy.png'}" 
                                 alt="${sanitizeHTML(enemy.name)}" 
                                 class="rounded me-2"
                                 width="48" height="48">
                            <h5 class="card-title mb-0">${sanitizeHTML(enemy.name)}</h5>
                        </div>
                        <p class="card-text text-muted mb-3">
                            ${sanitizeHTML(enemy.description || '').substring(0, 100)}
                            ${enemy.description?.length > 100 ? '...' : ''}
                        </p>
                        <div class="mb-3">
                            ${Object.entries(enemy.stats || {}).map(([key, value]) => `
                                <span class="badge bg-secondary me-1">${sanitizeHTML(key)}: ${value}</span>
                            `).join('')}
                        </div>
                        <div class="d-flex justify-content-between align-items-center">
                            <button class="btn btn-primary btn-sm" onclick="viewEnemy(${enemy.id})">
                                <i class="fas fa-eye me-1"></i>Ver
                            </button>
                            <div class="btn-group btn-group-sm">
                                <button class="btn btn-outline-primary" onclick="editEnemy(${enemy.id})">
                                    <i class="fas fa-edit"></i>
                                </button>
                                <button class="btn btn-outline-danger" onclick="deleteEnemy(${enemy.id})">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `).join('') || `
            <div class="col-12">
                <div class="text-center py-5">
                    <i class="fas fa-skull fa-3x mb-3 text-muted"></i>
                    <h3>Nenhum inimigo encontrado</h3>
                    <p class="text-muted">Clique em "Novo Inimigo" para começar!</p>
                </div>
            </div>
        `;
    } catch (error) {
        console.error('Erro ao carregar inimigos:', error);
        showNotification('error', 'Erro ao carregar inimigos');
    }
}

async function loadLogs() {
    try {
        const response = await fetch(`/api/campaigns/${currentCampaign}/logs`);
        const logs = await response.json();
        
        const logsList = document.getElementById('logs-list');
        logsList.innerHTML = logs.map(log => `
            <div class="list-group-item bg-dark border-secondary">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">${sanitizeHTML(log.character.name)}</h6>
                        <p class="mb-1 text-muted">${sanitizeHTML(log.change_description)}</p>
                        <small class="text-muted">
                            ${log.is_master ? '<i class="fas fa-crown me-1"></i>' : ''}
                            ${sanitizeHTML(log.user.username)} - ${formatDate(log.timestamp)}
                        </small>
                    </div>
                    <span class="badge bg-primary rounded-pill">
                        ${formatDate(log.timestamp).split(' ')[1]}
                    </span>
                </div>
            </div>
        `).join('') || `
            <div class="text-center py-5">
                <i class="fas fa-history fa-3x mb-3 text-muted"></i>
                <h3>Nenhum log encontrado</h3>
                <p class="text-muted">Os logs aparecerão aqui quando houver alterações.</p>
            </div>
        `;
    } catch (error) {
        console.error('Erro ao carregar logs:', error);
        showNotification('error', 'Erro ao carregar logs');
    }
}

// Funções de Sessão
function startSession() {
    const name = document.getElementById('sessionName').value;
    const displayedFields = Array.from(document.querySelectorAll('#displayFields input:checked'))
        .map(input => input.value);
    
    if (!name) {
        showNotification('error', 'Por favor, insira um nome para a sessão');
        return;
    }
    
    fetch(`/api/campaigns/${currentCampaign}/sessions`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name,
            displayed_fields: displayedFields
        })
    })
    .then(response => response.json())
    .then(session => {
        activeSession = session;
        
        // Fechar modal de configuração
        const modal = bootstrap.Modal.getInstance(document.getElementById('sessionModal'));
        modal.hide();
        
        // Abrir modal da sessão
        const activeModal = new bootstrap.Modal(document.getElementById('activeSessionModal'));
        activeModal.show();
        
        // Entrar na sala do Socket.IO
        socket.emit('join_session', { session_id: session.id });
        
        // Carregar personagens
        loadSessionCharacters();
    })
    .catch(error => {
        console.error('Erro ao iniciar sessão:', error);
        showNotification('error', 'Erro ao iniciar sessão');
    });
}

function confirmEndSession() {
    const modal = new bootstrap.Modal(document.getElementById('endSessionConfirmModal'));
    modal.show();
}

function endSession() {
    if (!activeSession) return;
    
    fetch(`/api/sessions/${activeSession.id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            is_active: false
        })
    })
    .then(() => {
        // Sair da sala do Socket.IO
        socket.emit('leave_session', { session_id: activeSession.id });
        
        // Fechar modais
        const confirmModal = bootstrap.Modal.getInstance(document.getElementById('endSessionConfirmModal'));
        confirmModal.hide();
        
        const activeModal = bootstrap.Modal.getInstance(document.getElementById('activeSessionModal'));
        activeModal.hide();
        
        activeSession = null;
        
        showNotification('success', 'Sessão encerrada com sucesso');
    })
    .catch(error => {
        console.error('Erro ao encerrar sessão:', error);
        showNotification('error', 'Erro ao encerrar sessão');
    });
}

// Funções de Atualização
function updateCharacterCard(data) {
    const card = document.querySelector(`#character-${data.id}`);
    if (card) {
        // Atualizar valores
        Object.entries(data.updates).forEach(([field, value]) => {
            const element = card.querySelector(`[data-field="${field}"]`);
            if (element) {
                element.textContent = value;
            }
        });
        
        // Adicionar classe de animação
        card.classList.add('fade-in');
        setTimeout(() => card.classList.remove('fade-in'), 300);
    }
}

// Funções de gerenciamento de logs
async function loadActivityLogs() {
    const logsContainer = document.getElementById('activity-log');
    try {
        const response = await fetch(`/api/campaign/${currentCampaign}/logs`);
        const logs = await response.json();
        
        logsContainer.innerHTML = '';
        logs.forEach(log => {
            const logEntry = document.createElement('div');
            logEntry.className = `log-entry ${log.is_master ? 'master' : 'player'} fade-in`;
            logEntry.innerHTML = `
                <div class="d-flex justify-content-between align-items-center">
                    <strong>${log.user_name}</strong>
                    <small>${new Date(log.timestamp).toLocaleString()}</small>
                </div>
                <p class="mb-0">${log.change_description}</p>
            `;
            logsContainer.appendChild(logEntry);
        });
    } catch (error) {
        console.error('Erro ao carregar logs:', error);
        logsContainer.innerHTML = '<div class="alert alert-danger">Erro ao carregar logs</div>';
    }
}

// Funções de gerenciamento de personagens
async function loadCharacterData() {
    const charactersGrid = document.getElementById('characters-grid');
    const characters = charactersGrid.querySelectorAll('.character-sheet');
    
    characters.forEach(async (characterCard) => {
        const characterId = characterCard.dataset.characterId;
        try {
            const response = await fetch(`/api/campaign/${currentCampaign}/character/${characterId}`);
            const data = await response.json();
            
            updateCharacterCard(data);
        } catch (error) {
            console.error(`Erro ao carregar dados do personagem ${characterId}:`, error);
        }
    });
}

function updateCharacterCard(card, data) {
    const dataContainer = card.querySelector('.character-data');
    dataContainer.innerHTML = '';
    
    Object.entries(data).forEach(([key, value]) => {
        if (key !== 'id' && key !== 'name' && key !== 'image_url') {
            const field = document.createElement('div');
            field.className = 'mb-2';
            field.innerHTML = `
                <strong>${key}:</strong>
                <span data-field="${key}">${value}</span>
            `;
            dataContainer.appendChild(field);
        }
    });
}

function viewCharacter(characterId) {
    window.location.href = `/character/${characterId}`;
}

// Funções do template de personagem
function initializeTemplateBuilder() {
    const builder = document.getElementById('template-builder');
    builder.innerHTML = `
        <div class="mb-3">
            <button type="button" class="btn btn-rpg" onclick="addField()">
                <i class="fas fa-plus me-2"></i>Adicionar Campo
            </button>
        </div>
        <div id="template-fields"></div>
    `;
}

function addField() {
    const fieldsContainer = document.getElementById('template-fields');
    const fieldId = Date.now();
    
    const fieldDiv = document.createElement('div');
    fieldDiv.className = 'mb-3 border p-3 rounded';
    fieldDiv.dataset.fieldId = fieldId;
    fieldDiv.innerHTML = `
        <div class="d-flex justify-content-between align-items-start mb-2">
            <div class="flex-grow-1 me-2">
                <input type="text" class="form-control mb-2" placeholder="Nome do Campo" required>
                <select class="form-control" onchange="updateFieldOptions(${fieldId})">
                    <option value="text">Texto</option>
                    <option value="number">Número</option>
                    <option value="textarea">Área de Texto</option>
                    <option value="select">Lista de Opções</option>
                    <option value="checkbox">Caixa de Seleção</option>
                    <option value="calculated">Campo Calculado</option>
                </select>
            </div>
            <button type="button" class="btn btn-danger" onclick="removeField(${fieldId})">
                <i class="fas fa-trash"></i>
            </button>
        </div>
        <div class="field-options"></div>
    `;
    
    fieldsContainer.appendChild(fieldDiv);
}

function removeField(fieldId) {
    const field = document.querySelector(`[data-field-id="${fieldId}"]`);
    field.remove();
}

function updateFieldOptions(fieldId) {
    const field = document.querySelector(`[data-field-id="${fieldId}"]`);
    const type = field.querySelector('select').value;
    const optionsContainer = field.querySelector('.field-options');
    
    switch (type) {
        case 'select':
            optionsContainer.innerHTML = `
                <div class="mt-2">
                    <label class="form-label">Opções</label>
                    <textarea class="form-control" placeholder="Uma opção por linha"></textarea>
                </div>
            `;
            break;
        case 'calculated':
            optionsContainer.innerHTML = `
                <div class="mt-2">
                    <label class="form-label">Fórmula</label>
                    <input type="text" class="form-control" placeholder="Ex: campo1 + campo2">
                    <small class="text-muted">Use os nomes dos campos na fórmula</small>
                </div>
            `;
            break;
        default:
            optionsContainer.innerHTML = '';
    }
}

async function saveTemplate() {
    const fields = [];
    const fieldDivs = document.querySelectorAll('#template-fields > div');
    
    fieldDivs.forEach(div => {
        const field = {
            name: div.querySelector('input[type="text"]').value,
            type: div.querySelector('select').value
        };
        
        const options = div.querySelector('.field-options');
        if (field.type === 'select') {
            field.options = options.querySelector('textarea').value.split('\n').filter(Boolean);
        } else if (field.type === 'calculated') {
            field.formula = options.querySelector('input').value;
        }
        
        fields.push(field);
    });
    
    try {
        const response = await fetch(`/api/campaign/${currentCampaign}/character-template`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ fields })
        });
        
        if (response.ok) {
            showToast('Template salvo com sucesso!', 'success');
            const modal = bootstrap.Modal.getInstance(document.getElementById('templateModal'));
            modal.hide();
        } else {
            throw new Error('Erro ao salvar template');
        }
    } catch (error) {
        console.error('Erro ao salvar template:', error);
        showToast('Erro ao salvar template', 'danger');
    }
}

// Funções da sessão virtual
let sessionActive = false;

function toggleSession() {
    const button = document.querySelector('#session button');
    if (!sessionActive) {
        button.innerHTML = '<i class="fas fa-stop me-2"></i>Encerrar Sessão';
        button.classList.add('btn-danger');
        initializeSession(currentCampaign);
    } else {
        button.innerHTML = '<i class="fas fa-play me-2"></i>Iniciar Sessão';
        button.classList.remove('btn-danger');
        endSession();
    }
    sessionActive = !sessionActive;
}

function endSession() {
    socket.emit('leave_session', { session_id: currentCampaign });
    const playersContainer = document.getElementById('session-players');
    playersContainer.innerHTML = '';
}

// Funções de convite
function copyInviteLink() {
    const input = document.getElementById('inviteLink');
    input.select();
    document.execCommand('copy');
    showToast('Link copiado para a área de transferência!', 'success');
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    const templateModal = document.getElementById('templateModal');
    if (templateModal) {
        templateModal.addEventListener('show.bs.modal', initializeTemplateBuilder);
    }
}); 