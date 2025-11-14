/**
 * Admin Dashboard JavaScript
 * Handles authentication, PDF upload, and analysis execution
 */

// Global state
const adminState = {
    token: null,
    currentUser: null,
    uploadedFile: null,
    currentAnalysis: null,
    pdetData: {
        subregions: [],
        municipalities: []
    }
};

// ============================================================================
// Authentication
// ============================================================================

async function login(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const messageDiv = document.getElementById('loginMessage');
    
    try {
        const response = await fetch('/api/v1/auth/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            adminState.token = data.token;
            adminState.currentUser = data.username;
            localStorage.setItem('atroz_admin_token', data.token);
            showAdminPanel();
        } else {
            showMessage(messageDiv, data.error || 'Error de autenticación', 'error');
        }
    } catch (error) {
        showMessage(messageDiv, 'Error de conexión', 'error');
        console.error('Login error:', error);
    }
}

function logout() {
    if (adminState.token) {
        fetch('/api/v1/auth/logout', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${adminState.token}`
            }
        }).catch(console.error);
    }
    
    adminState.token = null;
    adminState.currentUser = null;
    localStorage.removeItem('atroz_admin_token');
    
    document.getElementById('loginScreen').classList.remove('hidden');
    document.getElementById('adminPanel').classList.add('hidden');
}

function showAdminPanel() {
    document.getElementById('loginScreen').classList.add('hidden');
    document.getElementById('adminPanel').classList.remove('hidden');
    document.getElementById('currentUser').textContent = `Usuario: ${adminState.currentUser}`;
    
    // Initialize admin panel
    loadPDETData();
    loadRecentAnalyses();
}

// Check for existing token on page load
function checkExistingAuth() {
    const token = localStorage.getItem('atroz_admin_token');
    if (token) {
        // Verify token is still valid
        fetch('/api/v1/auth/verify', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.valid) {
                adminState.token = token;
                adminState.currentUser = data.username;
                showAdminPanel();
            } else {
                localStorage.removeItem('atroz_admin_token');
            }
        })
        .catch(() => {
            localStorage.removeItem('atroz_admin_token');
        });
    }
}

// ============================================================================
// PDET Data Loading
// ============================================================================

async function loadPDETData() {
    try {
        const response = await fetch('/api/v1/pdet/data', {
            headers: {
                'Authorization': `Bearer ${adminState.token}`
            }
        });
        
        const data = await response.json();
        adminState.pdetData = data;
        
        populateSubregionSelect();
    } catch (error) {
        console.error('Error loading PDET data:', error);
    }
}

function populateSubregionSelect() {
    const select = document.getElementById('subregionSelect');
    select.innerHTML = '<option value="">Seleccione una subregión...</option>';
    
    adminState.pdetData.subregions.forEach(subregion => {
        const option = document.createElement('option');
        option.value = subregion.id;
        option.textContent = subregion.name;
        select.appendChild(option);
    });
}

function onSubregionChange() {
    const subregionId = document.getElementById('subregionSelect').value;
    const municipalitySelect = document.getElementById('municipalitySelect');
    
    if (!subregionId) {
        municipalitySelect.disabled = true;
        municipalitySelect.innerHTML = '<option value="">Primero seleccione una subregión...</option>';
        return;
    }
    
    // Find subregion
    const subregion = adminState.pdetData.subregions.find(s => s.id === subregionId);
    if (!subregion) return;
    
    // Populate municipalities
    municipalitySelect.innerHTML = '<option value="">Seleccione un municipio...</option>';
    subregion.municipalities.forEach(muni => {
        const option = document.createElement('option');
        option.value = muni.id;
        option.textContent = muni.name;
        municipalitySelect.appendChild(option);
    });
    
    municipalitySelect.disabled = false;
}

// ============================================================================
// File Upload
// ============================================================================

function setupUploadZone() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('pdfFile');
    
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
    
    // Drag and drop
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', () => {
        uploadZone.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        
        if (e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });
}

function handleFileSelect(file) {
    const statusDiv = document.getElementById('uploadStatus');
    
    // Validate file
    if (!file.type.includes('pdf')) {
        showMessage(statusDiv, 'Por favor seleccione un archivo PDF', 'error');
        return;
    }
    
    if (file.size > 50 * 1024 * 1024) {
        showMessage(statusDiv, 'El archivo excede el tamaño máximo de 50MB', 'error');
        return;
    }
    
    adminState.uploadedFile = file;
    
    // Update UI
    const uploadZone = document.getElementById('uploadZone');
    uploadZone.innerHTML = `
        <div style="font-size: 48px; margin-bottom: 10px;">✓</div>
        <p style="color: var(--atroz-green-toxic);">${file.name}</p>
        <p style="font-size: 11px; opacity: 0.5; margin-top: 10px;">${formatFileSize(file.size)}</p>
        <button onclick="clearUpload(); event.stopPropagation();" style="margin-top: 15px; padding: 8px 16px; background: var(--atroz-red-700); border: none; color: white; cursor: pointer;">
            Cambiar archivo
        </button>
    `;
    
    showMessage(statusDiv, 'Archivo cargado correctamente', 'success');
    document.getElementById('analyzeBtn').disabled = false;
}

function clearUpload() {
    adminState.uploadedFile = null;
    document.getElementById('pdfFile').value = '';
    document.getElementById('uploadZone').innerHTML = `
        <div style="font-size: 48px; margin-bottom: 10px;">📎</div>
        <p>Arrastra un archivo PDF aquí o haz click para seleccionar</p>
        <p style="font-size: 11px; opacity: 0.5; margin-top: 10px;">Máximo 50MB</p>
    `;
    document.getElementById('uploadStatus').innerHTML = '';
    document.getElementById('uploadStatus').classList.add('hidden');
    document.getElementById('analyzeBtn').disabled = true;
}

// ============================================================================
// Analysis
// ============================================================================

async function startAnalysis() {
    if (!adminState.uploadedFile) {
        alert('Por favor cargue un archivo PDF primero');
        return;
    }
    
    const subregionId = document.getElementById('subregionSelect').value;
    const municipalityId = document.getElementById('municipalitySelect').value;
    
    if (!subregionId || !municipalityId) {
        alert('Por favor seleccione una subregión y municipio');
        return;
    }
    
    // Upload file first
    const uploadSuccess = await uploadFile();
    if (!uploadSuccess) {
        return;
    }
    
    // Start analysis
    document.getElementById('analyzeBtn').disabled = true;
    const statusDiv = document.getElementById('analysisStatus');
    const progressDiv = document.getElementById('analysisProgress');
    const resultsDiv = document.getElementById('analysisResults');
    
    showMessage(statusDiv, 'Iniciando análisis...', 'info');
    progressDiv.classList.remove('hidden');
    resultsDiv.classList.add('hidden');
    
    try {
        const response = await fetch('/api/v1/admin/analyze', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${adminState.token}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                subregion_id: subregionId,
                municipality_id: municipalityId,
                filename: adminState.uploadedFile.name
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            adminState.currentAnalysis = data.request_id;
            pollAnalysisStatus(data.request_id);
        } else {
            showMessage(statusDiv, data.error || 'Error al iniciar análisis', 'error');
            progressDiv.classList.add('hidden');
            document.getElementById('analyzeBtn').disabled = false;
        }
    } catch (error) {
        showMessage(statusDiv, 'Error de conexión', 'error');
        progressDiv.classList.add('hidden');
        document.getElementById('analyzeBtn').disabled = false;
        console.error('Analysis error:', error);
    }
}

async function uploadFile() {
    const progressBar = document.getElementById('uploadProgress');
    const progressFill = document.getElementById('uploadProgressFill');
    
    progressBar.classList.remove('hidden');
    
    const formData = new FormData();
    formData.append('file', adminState.uploadedFile);
    
    try {
        const response = await fetch('/api/v1/admin/upload', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${adminState.token}`
            },
            body: formData
        });
        
        progressFill.style.width = '100%';
        
        if (response.ok) {
            setTimeout(() => {
                progressBar.classList.add('hidden');
                progressFill.style.width = '0%';
            }, 500);
            return true;
        } else {
            const data = await response.json();
            alert(data.error || 'Error al cargar archivo');
            progressBar.classList.add('hidden');
            return false;
        }
    } catch (error) {
        alert('Error de conexión al cargar archivo');
        progressBar.classList.add('hidden');
        console.error('Upload error:', error);
        return false;
    }
}

async function pollAnalysisStatus(requestId) {
    const statusDiv = document.getElementById('analysisStatus');
    const progressFill = document.getElementById('analysisProgressFill');
    const stageDiv = document.getElementById('analysisStage');
    
    let progress = 0;
    const stages = [
        'Extrayendo texto del PDF...',
        'Analizando nivel macro...',
        'Analizando nivel meso (clusters)...',
        'Analizando nivel micro (44 preguntas)...',
        'Generando recomendaciones...',
        'Compilando evidencias...',
        'Finalizando análisis...'
    ];
    
    const interval = setInterval(() => {
        progress += 100 / stages.length;
        if (progress > 95) progress = 95;  // Stop at 95% until complete
        
        progressFill.style.width = `${progress}%`;
        stageDiv.textContent = stages[Math.floor(progress / (100 / stages.length))] || stages[stages.length - 1];
    }, 2000);
    
    // Poll for completion
    const checkInterval = setInterval(async () => {
        try {
            const response = await fetch(`/api/v1/admin/analysis/${requestId}`, {
                headers: {
                    'Authorization': `Bearer ${adminState.token}`
                }
            });
            
            const data = await response.json();
            
            if (data.status === 'completed') {
                clearInterval(interval);
                clearInterval(checkInterval);
                
                progressFill.style.width = '100%';
                showMessage(statusDiv, '¡Análisis completado exitosamente!', 'success');
                
                setTimeout(() => {
                    displayAnalysisResults(data.result);
                }, 1000);
            } else if (data.status === 'failed') {
                clearInterval(interval);
                clearInterval(checkInterval);
                
                showMessage(statusDiv, `Error: ${data.error}`, 'error');
                document.getElementById('analysisProgress').classList.add('hidden');
                document.getElementById('analyzeBtn').disabled = false;
            }
        } catch (error) {
            // Continue polling on error
            console.error('Status poll error:', error);
        }
    }, 3000);
}

function displayAnalysisResults(result) {
    const resultsDiv = document.getElementById('analysisResults');
    
    resultsDiv.innerHTML = `
        <div class="analysis-result">
            <h3 style="font-size: 16px; margin-bottom: 20px; letter-spacing: 2px;">RESULTADOS DEL ANÁLISIS</h3>
            
            <div class="metric">
                <span class="metric-label">Puntuación Macro</span>
                <span class="metric-value">${(result.macro_score * 100).toFixed(1)}%</span>
            </div>
            
            <div class="metric">
                <span class="metric-label">Clusters Analizados</span>
                <span class="metric-value">${Object.keys(result.meso_clusters || {}).length}</span>
            </div>
            
            <div class="metric">
                <span class="metric-label">Preguntas Evaluadas</span>
                <span class="metric-value">${(result.micro_questions || []).length}</span>
            </div>
            
            <div class="metric">
                <span class="metric-label">Recomendaciones</span>
                <span class="metric-value">${(result.recommendations || []).length}</span>
            </div>
            
            <div class="metric">
                <span class="metric-label">Evidencias</span>
                <span class="metric-value">${(result.evidence_items || []).length}</span>
            </div>
            
            <div class="metric">
                <span class="metric-label">Tiempo de Procesamiento</span>
                <span class="metric-value">${result.processing_time_seconds?.toFixed(1)}s</span>
            </div>
            
            <button onclick="viewFullReport('${result.request_id}')" class="btn" style="margin-top: 20px; width: 100%;">
                Ver Reporte Completo
            </button>
        </div>
    `;
    
    resultsDiv.classList.remove('hidden');
    document.getElementById('analysisProgress').classList.add('hidden');
    document.getElementById('analyzeBtn').disabled = false;
    
    // Reload recent analyses
    loadRecentAnalyses();
}

function viewFullReport(requestId) {
    // Open dashboard with this analysis
    window.open(`/?analysis=${requestId}`, '_blank');
}

// ============================================================================
// Recent Analyses
// ============================================================================

async function loadRecentAnalyses() {
    try {
        const response = await fetch('/api/v1/admin/analyses/recent', {
            headers: {
                'Authorization': `Bearer ${adminState.token}`
            }
        });
        
        const data = await response.json();
        
        if (data.analyses && data.analyses.length > 0) {
            displayRecentAnalyses(data.analyses);
        }
    } catch (error) {
        console.error('Error loading recent analyses:', error);
    }
}

function displayRecentAnalyses(analyses) {
    const container = document.getElementById('recentAnalyses');
    
    container.innerHTML = analyses.map(analysis => `
        <div class="analysis-result">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div>
                    <h4 style="font-size: 14px; margin-bottom: 5px;">${analysis.municipality_name}</h4>
                    <p style="font-size: 11px; opacity: 0.5;">${analysis.subregion_name}</p>
                    <p style="font-size: 11px; opacity: 0.5; margin-top: 5px;">
                        ${new Date(analysis.completed_at).toLocaleString('es-CO')}
                    </p>
                </div>
                <div style="text-align: right;">
                    <div class="metric-value" style="font-size: 24px;">
                        ${(analysis.macro_score * 100).toFixed(0)}%
                    </div>
                    <button onclick="viewFullReport('${analysis.request_id}')" class="btn" style="margin-top: 10px; padding: 8px 16px;">
                        Ver
                    </button>
                </div>
            </div>
        </div>
    `).join('');
}

// ============================================================================
// Utility Functions
// ============================================================================

function showMessage(element, message, type) {
    element.textContent = message;
    element.className = `status-message status-${type}`;
    element.classList.remove('hidden');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    // Setup event listeners
    document.getElementById('loginForm').addEventListener('submit', login);
    document.getElementById('subregionSelect').addEventListener('change', onSubregionChange);
    
    // Setup upload zone
    setupUploadZone();
    
    // Initialize particles
    if (typeof initParticles === 'function') {
        initParticles();
    }
    
    // Check for existing auth
    checkExistingAuth();
});
