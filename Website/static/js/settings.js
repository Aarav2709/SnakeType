let currentSettings = {};

document.addEventListener('DOMContentLoaded', function() {
    loadCurrentSettings();
    initializeSettingsControls();
});

function loadCurrentSettings() {
    fetch('/api/settings')
        .then(response => response.json())
        .then(settings => {
            currentSettings = settings;
            updateSettingsUI(settings);
        })
        .catch(error => {
            console.error('Error loading settings:', error);
            showSaveStatus('Error loading settings', 'error');
        });
}

function updateSettingsUI(settings) {
    document.getElementById('auto-difficulty').checked = settings.auto_difficulty === 'true';
    document.getElementById('sound-enabled').checked = settings.sound_enabled === 'true';
    document.getElementById('show-live-wpm').checked = true; // Default
    document.getElementById('show-keyboard').checked = false; // Default
    
    document.getElementById('daily-goal').value = settings.daily_goal || 5;
    
    document.getElementById('theme-select').value = settings.theme || 'dark';
    document.getElementById('font-size').value = 'medium'; // Default
    document.getElementById('keyboard-layout').value = 'qwerty'; // Default
}

function initializeSettingsControls() {
    const fileInput = document.getElementById('custom-text-file');
    const fileName = document.getElementById('file-name');
    
    fileInput.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            fileName.textContent = file.name;
            handleCustomTextUpload(file);
        } else {
            fileName.textContent = '';
        }
    });
    
    document.getElementById('theme-select').addEventListener('change', function() {
        previewTheme(this.value);
    });
    
    document.querySelectorAll('input, select').forEach(element => {
        element.addEventListener('change', function() {
            const settingKey = this.id.replace(/-/g, '_');
            let value = this.value;
            
            if (this.type === 'checkbox') {
                value = this.checked ? 'true' : 'false';
            }
            
            currentSettings[settingKey] = value;
        });
    });
}

function saveSettings() {
    const saveButton = document.querySelector('.save-settings');
    const originalText = saveButton.textContent;
    
    saveButton.textContent = '💾 Saving...';
    saveButton.disabled = true;
    
    fetch('/api/settings', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(currentSettings)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSaveStatus('Settings saved successfully!', 'success');
            applySettings(currentSettings);
        } else {
            showSaveStatus('Failed to save settings', 'error');
        }
    })
    .catch(error => {
        console.error('Error saving settings:', error);
        showSaveStatus('Error saving settings', 'error');
    })
    .finally(() => {
        saveButton.textContent = originalText;
        saveButton.disabled = false;
    });
}

function showSaveStatus(message, type) {
    const statusElement = document.getElementById('save-status');
    statusElement.textContent = message;
    statusElement.className = `save-status ${type}`;
    
    setTimeout(() => {
        statusElement.textContent = '';
        statusElement.className = 'save-status';
    }, 3000);
}

function applySettings(settings) {
    if (settings.theme) {
        document.body.className = `theme-${settings.theme}`;
        localStorage.setItem('theme', settings.theme);
    }
    
    if (settings.font_size) {
        document.documentElement.style.setProperty('--font-scale', getFontScale(settings.font_size));
        localStorage.setItem('fontSize', settings.font_size);
    }
    
    localStorage.setItem('userSettings', JSON.stringify(settings));
}

function getFontScale(size) {
    const scales = {
        small: '0.9',
        medium: '1.0',
        large: '1.1',
        xlarge: '1.2'
    };
    return scales[size] || '1.0';
}

function previewTheme(theme) {
    document.body.className = `theme-${theme}`;
}

function handleCustomTextUpload(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/api/upload_text', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSaveStatus(`Uploaded ${data.word_count} words successfully!`, 'success');
            sessionStorage.setItem('customText', JSON.stringify(data.words));
        } else {
            showSaveStatus(`Upload failed: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error uploading file:', error);
        showSaveStatus('Upload failed', 'error');
    });
}

function exportData() {
    fetch('/api/export_data')
        .then(response => response.json())
        .then(data => {
            const blob = new Blob([JSON.stringify(data, null, 2)], {
                type: 'application/json'
            });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `snaketype-data-${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showSaveStatus('Data exported successfully!', 'success');
        })
        .catch(error => {
            console.error('Error exporting data:', error);
            showSaveStatus('Export failed', 'error');
        });
}

function confirmReset() {
    const modal = document.getElementById('resetModal');
    modal.style.display = 'block';
}

function closeResetModal() {
    const modal = document.getElementById('resetModal');
    modal.style.display = 'none';
}

function confirmResetData() {
    localStorage.clear();
    sessionStorage.clear();
    
    showSaveStatus('All data has been reset', 'success');
    closeResetModal();
    
    setTimeout(() => {
        window.location.reload();
    }, 2000);
}

document.addEventListener('click', function(event) {
    const modal = document.getElementById('resetModal');
    if (event.target === modal) {
        closeResetModal();
    }
});

document.addEventListener('keydown', function(event) {
    if (event.ctrlKey && event.key === 's') {
        event.preventDefault();
        saveSettings();
    }
    
    if (event.key === 'Escape') {
        closeResetModal();
    }
});

let autoSaveTimeout;
function scheduleAutoSave() {
    clearTimeout(autoSaveTimeout);
    autoSaveTimeout = setTimeout(() => {
        const autoSaveSettings = { ...currentSettings };
        delete autoSaveSettings.reset_data; // Don't auto-save destructive actions
        
        fetch('/api/settings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(autoSaveSettings)
        }).catch(error => {
            console.error('Auto-save failed:', error);
        });
    }, 1000);
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input, select').forEach(element => {
        element.addEventListener('change', scheduleAutoSave);
    });
});

function createThemePreview() {
    const themeSelect = document.getElementById('theme-select');
    const previewContainer = document.createElement('div');
    previewContainer.className = 'theme-preview';
    
    const themes = ['dark', 'light', 'blue', 'green'];
    themes.forEach(theme => {
        const option = document.createElement('div');
        option.className = `theme-option theme-${theme}`;
        option.textContent = theme.charAt(0).toUpperCase() + theme.slice(1);
        option.addEventListener('click', () => {
            themeSelect.value = theme;
            previewTheme(theme);
            currentSettings.theme = theme;
            
            document.querySelectorAll('.theme-option').forEach(opt => opt.classList.remove('active'));
            option.classList.add('active');
        });
        previewContainer.appendChild(option);
    });
    
    themeSelect.parentNode.insertBefore(previewContainer, themeSelect.nextSibling);
    
    const currentTheme = currentSettings.theme || 'dark';
    document.querySelector(`.theme-${currentTheme}`).classList.add('active');
}

document.addEventListener('DOMContentLoaded', createThemePreview);

document.addEventListener('DOMContentLoaded', function() {
    const savedTheme = localStorage.getItem('theme');
    const savedFontSize = localStorage.getItem('fontSize');
    
    if (savedTheme) {
        document.body.className = `theme-${savedTheme}`;
    }
    
    if (savedFontSize) {
        document.documentElement.style.setProperty('--font-scale', getFontScale(savedFontSize));
    }
});
