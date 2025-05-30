// Variáveis globais
let socket;
let combatId;
let sessionId;
let selectedCharacter = null;

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    socket = io();
    combatId = document.body.dataset.combatId;
    sessionId = document.body.dataset.sessionId;
    
    // Conectar ao socket da sessão
    socket.emit('join', {room: `session_${sessionId}`});
    
    // Eventos de Socket
    setupSocketEvents();
    
    // Event Listeners
    setupEventListeners();
    
    // Inicialização do grid tático
    initializeCombatGrid();
    
    // Carregar dados iniciais
    loadInitialData();
});

// Configuração dos eventos do Socket
function setupSocketEvents() {
    socket.on('initiative_added', updateInitiativeList);
    socket.on('turn_changed', updateTurn);
    socket.on('hp_updated', updateCharacterHP);
    socket.on('conditions_updated', updateConditions);
    socket.on('combat_ended', handleCombatEnd);
    socket.on('character_moved', updateCharacterPosition);
}

// Configuração dos event listeners
function setupEventListeners() {
    document.getElementById('next-turn-btn').addEventListener('click', nextTurn);
    document.getElementById('end-combat-btn').addEventListener('click', confirmEndCombat);
    document.getElementById('add-initiative-btn').addEventListener('click', showInitiativeModal);
    document.getElementById('roll-initiative').addEventListener('click', rollInitiative);
    document.getElementById('save-initiative').addEventListener('click', saveInitiative);
    document.getElementById('initiative-type').addEventListener('change', toggleInitiativeSelects);
}

// Funções do Grid Tático
function initializeCombatGrid() {
    const grid = document.getElementById('combat-grid');
    for (let i = 0; i < 225; i++) {
        const cell = document.createElement('div');
        cell.className = 'grid-cell';
        cell.dataset.index = i;
        cell.addEventListener('click', handleGridClick);
        grid.appendChild(cell);
    }
}

function handleGridClick(event) {
    if (!selectedCharacter) return;
    
    const cell = event.target;
    const index = parseInt(cell.dataset.index);
    const position = {
        x: index % 15,
        y: Math.floor(index / 15)
    };
    
    moveCharacter(selectedCharacter, position);
}

function moveCharacter(characterId, position) {
    fetch(`/api/combat/${combatId}/move`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            character_id: characterId,
            position_x: position.x,
            position_y: position.y
        })
    });
}

// Funções de Iniciativa
function showInitiativeModal() {
    const modal = new bootstrap.Modal(document.getElementById('initiative-modal'));
    modal.show();
}

function toggleInitiativeSelects() {
    const type = document.getElementById('initiative-type').value;
    document.getElementById('character-select-container').style.display = 
        type === 'character' ? 'block' : 'none';
    document.getElementById('enemy-select-container').style.display = 
        type === 'enemy' ? 'block' : 'none';
}

function rollInitiative() {
    const result = Math.floor(Math.random() * 20) + 1;
    document.getElementById('initiative-value').value = result;
}

function saveInitiative() {
    const type = document.getElementById('initiative-type').value;
    const data = {
        initiative_value: parseInt(document.getElementById('initiative-value').value),
        current_hp: parseInt(document.getElementById('initial-hp').value)
    };
    
    if (type === 'character') {
        data.character_id = document.getElementById('character-select').value;
    } else {
        data.enemy_id = document.getElementById('enemy-select').value;
    }
    
    fetch(`/api/combat/${combatId}/initiative`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    
    const modal = bootstrap.Modal.getInstance(document.getElementById('initiative-modal'));
    modal.hide();
}

// Funções de Atualização da UI
function updateInitiativeList(data) {
    const container = document.getElementById('initiative-container');
    const item = document.createElement('div');
    item.className = 'list-group-item bg-dark border-secondary';
    item.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <div>
                <h6 class="mb-0">${data.name}</h6>
                <div class="progress bg-secondary" style="height: 5px; width: 100px;">
                    <div class="progress-bar bg-danger" style="width: ${(data.current_hp / data.max_hp) * 100}%"></div>
                </div>
            </div>
            <span class="badge bg-primary">${data.initiative_value}</span>
        </div>
    `;
    container.appendChild(item);
}

function updateTurn(data) {
    document.getElementById('round-number').textContent = data.round;
    
    // Atualizar destaque do personagem atual
    const items = document.querySelectorAll('#initiative-container .list-group-item');
    items.forEach((item, index) => {
        item.classList.toggle('active', index === data.current_turn);
    });
    
    // Atualizar painel de status
    updateCurrentCharacter(data.current_initiative);
}

function updateCurrentCharacter(data) {
    const card = document.getElementById('current-character');
    card.innerHTML = `
        <div class="card-body">
            <h5 class="card-title">${data.name}</h5>
            <div class="mb-2">
                <label class="form-label">HP</label>
                <div class="input-group">
                    <input type="number" class="form-control" value="${data.current_hp}">
                    <span class="input-group-text">/ ${data.max_hp}</span>
                    <button class="btn btn-outline-primary" onclick="updateHP(${data.id})">
                        <i class="fas fa-save"></i>
                    </button>
                </div>
            </div>
            <div class="conditions mb-2">
                ${data.conditions.map(condition => `
                    <span class="condition-tag">${condition}</span>
                `).join('')}
            </div>
            <button class="btn btn-outline-secondary btn-sm" onclick="addCondition(${data.id})">
                <i class="fas fa-plus me-1"></i>Adicionar Condição
            </button>
        </div>
    `;
}

function updateCharacterHP(data) {
    const item = document.querySelector(`#initiative-container [data-id="${data.id}"]`);
    if (item) {
        const progressBar = item.querySelector('.progress-bar');
        progressBar.style.width = `${(data.current_hp / data.max_hp) * 100}%`;
    }
}

function updateConditions(data) {
    const conditions = document.getElementById('conditions-container');
    conditions.innerHTML = data.conditions.map(condition => `
        <span class="condition-tag">
            ${condition}
            <button class="btn btn-sm btn-link text-danger" onclick="removeCondition(${data.id}, '${condition}')">
                <i class="fas fa-times"></i>
            </button>
        </span>
    `).join('');
}

function updateCharacterPosition(data) {
    const cells = document.querySelectorAll('.grid-cell');
    cells.forEach(cell => cell.classList.remove('occupied'));
    
    const index = data.position.y * 15 + data.position.x;
    cells[index].classList.add('occupied');
}

// Funções de Controle do Combate
function nextTurn() {
    fetch(`/api/combat/${combatId}/next-turn`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'}
    });
}

function confirmEndCombat() {
    if (confirm('Deseja realmente encerrar o combate?')) {
        fetch(`/api/combat/${combatId}/end`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'}
        });
    }
}

function handleCombatEnd(data) {
    if (data.combat_id === combatId) {
        window.location.href = `/sessions/${sessionId}`;
    }
}

// Funções de Condições
function addCondition(initiativeId) {
    const condition = prompt('Digite a condição:');
    if (condition) {
        fetch(`/api/combat/${combatId}/conditions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                initiative_id: initiativeId,
                condition: condition
            })
        });
    }
}

function removeCondition(initiativeId, condition) {
    fetch(`/api/combat/${combatId}/conditions/${initiativeId}`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            condition: condition
        })
    });
}

// Funções de Carregamento Inicial
async function loadInitialData() {
    try {
        const response = await fetch(`/api/combat/${combatId}`);
        const data = await response.json();
        
        // Carregar iniciativas
        data.initiatives.forEach(updateInitiativeList);
        
        // Atualizar turno atual
        updateTurn({
            round: data.round_number,
            current_turn: data.current_turn,
            current_initiative: data.initiatives[data.current_turn]
        });
        
        // Carregar posições no grid
        data.initiatives.forEach(updateCharacterPosition);
    } catch (error) {
        console.error('Erro ao carregar dados iniciais:', error);
    }
} 