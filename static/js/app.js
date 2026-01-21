// FantasmaWiFi-Pro Web UI JavaScript

// Initialize Socket.IO connection
const socket = io();

// Global state
let interfaces = [];
let currentStatus = null;

// DOM Elements
const statusBadge = document.getElementById('statusBadge');
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const platformEl = document.getElementById('platform');
const modeEl = document.getElementById('mode');
const sourceEl = document.getElementById('source');
const targetEl = document.getElementById('target');
const uptimeEl = document.getElementById('uptime');

const startForm = document.getElementById('startForm');
const modeSelect = document.getElementById('modeSelect');
const sourceSelect = document.getElementById('sourceSelect');
const targetSelect = document.getElementById('targetSelect');
const hotspotSettings = document.getElementById('hotspotSettings');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const stopSection = document.getElementById('stopSection');
const refreshBtn = document.getElementById('refreshBtn');

const interfacesList = document.getElementById('interfacesList');
const profilesList = document.getElementById('profilesList');
const saveProfileBtn = document.getElementById('saveProfileBtn');
const loadProfileBtn = document.getElementById('loadProfileBtn');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('FantasmaWiFi-Pro Web UI loaded');
    loadInterfaces();
    loadStatus();
    loadProfiles();
    setupEventListeners();
});

// Socket.IO Event Handlers
socket.on('connect', () => {
    console.log('Connected to server');
    showAlert('Connected to Fantasma server', 'success');
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    showAlert('Disconnected from server', 'error');
});

socket.on('status_update', (status) => {
    console.log('Status update:', status);
    updateStatus(status);
});

// Event Listeners
function setupEventListeners() {
    // Mode selection change
    modeSelect.addEventListener('change', (e) => {
        if (e.target.value === 'hotspot') {
            hotspotSettings.style.display = 'block';
        } else {
            hotspotSettings.style.display = 'none';
        }
    });

    // Start form submission
    startForm.addEventListener('submit', (e) => {
        e.preventDefault();
        startSharing();
    });

    // Stop button
    stopBtn.addEventListener('click', () => {
        stopSharing();
    });

    // Refresh interfaces
    refreshBtn.addEventListener('click', () => {
        loadInterfaces();
        showAlert('Interfaces refreshed', 'info');
    });

    // Save profile
    saveProfileBtn.addEventListener('click', () => {
        saveCurrentProfile();
    });

    // Load profile
    loadProfileBtn.addEventListener('click', () => {
        showProfileSelector();
    });
}

// API Functions
async function loadInterfaces() {
    try {
        const response = await fetch('/api/interfaces');
        const data = await response.json();
        
        if (data.error) {
            showAlert(data.error, 'error');
            return;
        }
        
        interfaces = data.interfaces || [];
        updateInterfacesList();
        populateInterfaceSelects();
    } catch (error) {
        console.error('Error loading interfaces:', error);
        showAlert('Failed to load interfaces', 'error');
    }
}

async function loadStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.error) {
            console.error('Error loading status:', data.error);
            return;
        }
        
        updateStatus(data);
    } catch (error) {
        console.error('Error loading status:', error);
    }
}

async function startSharing() {
    const formData = new FormData(startForm);
    const data = {
        mode: formData.get('mode'),
        source: formData.get('source'),
        target: formData.get('target'),
        ssid: formData.get('ssid'),
        password: formData.get('password'),
        channel: formData.get('channel'),
        ip_range: formData.get('ip_range')
    };

    // Validate password length for hotspot mode
    if (data.mode === 'hotspot' && data.password && data.password.length < 8) {
        showAlert('Password must be at least 8 characters', 'error');
        return;
    }

    startBtn.disabled = true;
    startBtn.textContent = 'Starting...';

    try {
        const response = await fetch('/api/start', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            showAlert('Sharing started successfully!', 'success');
            setTimeout(() => loadStatus(), 1000);
        } else {
            showAlert(result.message || 'Failed to start sharing', 'error');
        }
    } catch (error) {
        console.error('Error starting sharing:', error);
        showAlert('Failed to start sharing: ' + error.message, 'error');
    } finally {
        startBtn.disabled = false;
        startBtn.textContent = 'Start Sharing';
    }
}

async function stopSharing() {
    stopBtn.disabled = true;
    stopBtn.textContent = 'Stopping...';

    try {
        const response = await fetch('/api/stop', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const result = await response.json();

        if (result.success) {
            showAlert('Sharing stopped successfully', 'success');
            setTimeout(() => loadStatus(), 1000);
        } else {
            showAlert(result.message || 'Failed to stop sharing', 'error');
        }
    } catch (error) {
        console.error('Error stopping sharing:', error);
        showAlert('Failed to stop sharing: ' + error.message, 'error');
    } finally {
        stopBtn.disabled = false;
        stopBtn.textContent = 'Stop Sharing';
    }
}

async function loadProfiles() {
    try {
        const response = await fetch('/api/profiles');
        const data = await response.json();
        
        const profiles = data.profiles || [];
        
        if (profiles.length === 0) {
            profilesList.innerHTML = '<p class="empty-state">No profiles saved yet</p>';
        } else {
            profilesList.innerHTML = profiles.map(name => `
                <div class="profile-item">
                    <span class="profile-name">${name}</span>
                    <div class="profile-actions">
                        <button class="btn btn-small btn-secondary" onclick="loadProfile('${name}')">Load</button>
                        <button class="btn btn-small btn-danger" onclick="deleteProfile('${name}')">Delete</button>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading profiles:', error);
    }
}

async function saveCurrentProfile() {
    const formData = new FormData(startForm);
    // TODO: Replace with custom modal dialog for better UX
    const name = prompt('Enter profile name:');
    
    if (!name) return;
    
    const config = {
        mode: formData.get('mode'),
        source: formData.get('source'),
        target: formData.get('target'),
        ssid: formData.get('ssid'),
        password: formData.get('password'),
        channel: formData.get('channel'),
        ip_range: formData.get('ip_range')
    };

    try {
        const response = await fetch('/api/profiles', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, config })
        });

        const result = await response.json();

        if (result.success) {
            showAlert(`Profile "${name}" saved successfully`, 'success');
            loadProfiles();
        } else {
            showAlert('Failed to save profile', 'error');
        }
    } catch (error) {
        console.error('Error saving profile:', error);
        showAlert('Failed to save profile', 'error');
    }
}

async function loadProfile(name) {
    try {
        const response = await fetch(`/api/profiles/${name}`);
        const data = await response.json();
        
        if (data.error) {
            showAlert('Profile not found', 'error');
            return;
        }
        
        const config = data.profile;
        
        // Populate form with profile data
        modeSelect.value = config.mode;
        sourceSelect.value = config.source;
        targetSelect.value = config.target;
        document.getElementById('ssid').value = config.ssid;
        document.getElementById('password').value = config.password;
        document.getElementById('channel').value = config.channel;
        document.getElementById('ipRange').value = config.ip_range;
        
        // Show/hide hotspot settings
        hotspotSettings.style.display = config.mode === 'hotspot' ? 'block' : 'none';
        
        showAlert(`Profile "${name}" loaded`, 'success');
    } catch (error) {
        console.error('Error loading profile:', error);
        showAlert('Failed to load profile', 'error');
    }
}

async function deleteProfile(name) {
    // TODO: Replace with custom modal dialog for better UX
    if (!confirm(`Delete profile "${name}"?`)) return;

    try {
        const response = await fetch(`/api/profiles/${name}`, {
            method: 'DELETE'
        });

        const result = await response.json();

        if (result.success) {
            showAlert(`Profile "${name}" deleted`, 'success');
            loadProfiles();
        } else {
            showAlert('Failed to delete profile', 'error');
        }
    } catch (error) {
        console.error('Error deleting profile:', error);
        showAlert('Failed to delete profile', 'error');
    }
}

// UI Update Functions
function updateStatus(status) {
    currentStatus = status;
    
    // Update platform
    platformEl.textContent = status.platform || 'Unknown';
    
    // Update active status
    if (status.active) {
        statusDot.classList.add('active');
        statusText.textContent = 'Active';
        modeEl.textContent = status.mode || 'Unknown';
        sourceEl.textContent = status.source_interface || '-';
        targetEl.textContent = status.target_interface || '-';
        uptimeEl.textContent = formatUptime(status.uptime || 0);
        
        // Show stop button, hide form
        startForm.style.display = 'none';
        stopSection.style.display = 'block';
    } else {
        statusDot.classList.remove('active');
        statusText.textContent = 'Inactive';
        modeEl.textContent = 'None';
        sourceEl.textContent = '-';
        targetEl.textContent = '-';
        uptimeEl.textContent = '-';
        
        // Show form, hide stop button
        startForm.style.display = 'block';
        stopSection.style.display = 'none';
    }
}

function updateInterfacesList() {
    if (interfaces.length === 0) {
        interfacesList.innerHTML = '<p class="empty-state">No interfaces found</p>';
        return;
    }
    
    interfacesList.innerHTML = interfaces.map(iface => `
        <div class="interface-item">
            <div>
                <div class="interface-name">${iface.name}</div>
                <div class="interface-details">
                    ${iface.ip || 'No IP'} • ${iface.mac || 'No MAC'}
                </div>
            </div>
            <span class="interface-type">${iface.type}</span>
        </div>
    `).join('');
}

function populateInterfaceSelects() {
    // Clear existing options (except first)
    sourceSelect.innerHTML = '<option value="">-- Select Source --</option>';
    targetSelect.innerHTML = '<option value="">-- Select Target --</option>';
    
    // Add interface options
    interfaces.forEach(iface => {
        const sourceOption = new Option(
            `${iface.name} (${iface.type}) - ${iface.ip || 'No IP'}`,
            iface.name
        );
        const targetOption = new Option(
            `${iface.name} (${iface.type}) - ${iface.ip || 'No IP'}`,
            iface.name
        );
        
        sourceSelect.add(sourceOption);
        targetSelect.add(targetOption);
    });
}

function showAlert(message, type) {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    // Insert at top of main dashboard
    const dashboard = document.querySelector('.dashboard');
    dashboard.insertBefore(alert, dashboard.firstChild);
    
    // Remove after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

function formatUptime(seconds) {
    if (seconds === 0) return '-';
    
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

function showProfileSelector() {
    // TODO: Replace with custom modal dialog for better UX
    // Simple implementation - could be enhanced with a modal
    const profiles = Array.from(profilesList.querySelectorAll('.profile-name'))
        .map(el => el.textContent);
    
    if (profiles.length === 0) {
        showAlert('No profiles available', 'info');
        return;
    }
    
    const name = prompt('Enter profile name to load:\n\n' + profiles.join('\n'));
    if (name) {
        loadProfile(name);
    }
}
