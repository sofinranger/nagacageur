// Nagagold Migration Tool - JavaScript

// Set default date to today
document.addEventListener('DOMContentLoaded', function() {
    const dateInput = document.getElementById('date');
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
});

// Toggle password visibility
document.getElementById('togglePassword').addEventListener('click', function() {
    const passwordInput = document.getElementById('password');
    const passwordIcon = document.getElementById('passwordIcon');
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        passwordIcon.classList.remove('bi-eye');
        passwordIcon.classList.add('bi-eye-slash');
    } else {
        passwordInput.type = 'password';
        passwordIcon.classList.remove('bi-eye-slash');
        passwordIcon.classList.add('bi-eye');
    }
});

// Show alert message
function showAlert(message, type = 'info') {
    const alertContainer = document.getElementById('alertContainer');
    
    const alertHTML = `
        <div class="alert alert-${type} alert-dismissible fade show fade-in" role="alert">
            <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-triangle' : 'info-circle'}-fill me-2"></i>
            ${message.replace(/\n/g, '<br>')}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    alertContainer.innerHTML = alertHTML;
    
    // Auto-dismiss after 5 seconds
    if (type === 'success') {
        setTimeout(() => {
            const alert = alertContainer.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

// Clear alerts
function clearAlerts() {
    document.getElementById('alertContainer').innerHTML = '';
}

// Test Connection
document.getElementById('testConnectionBtn').addEventListener('click', async function() {
    const btn = this;
    const originalHTML = btn.innerHTML;
    
    // Disable button and show loading
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Testing...';
    
    clearAlerts();
    
    // Get form data
    const formData = {
        host: document.getElementById('host').value,
        user: document.getElementById('user').value,
        password: document.getElementById('password').value,
        database: document.getElementById('database').value
    };
    
    try {
        const response = await fetch('/test-connection', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        showAlert('Connection test failed: ' + error.message, 'danger');
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }
});

// Migration Form Submit
document.getElementById('migrationForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const processBtn = document.getElementById('processBtn');
    const originalHTML = processBtn.innerHTML;
    
    // Disable button and show loading
    processBtn.disabled = true;
    processBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
    
    clearAlerts();
    
    // Show progress section
    const progressSection = document.getElementById('progressSection');
    progressSection.style.display = 'block';
    
    // Reset progress
    updateProgress(0, 0, 0, 'Starting migration...');
    
    // Get form data
    const formData = {
        host: document.getElementById('host').value,
        user: document.getElementById('user').value,
        password: document.getElementById('password').value,
        database: document.getElementById('database').value,
        date: document.getElementById('date').value
    };
    
    try {
        // Start migration
        const response = await fetch('/start-migration', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            
            // Show open folder button
            document.getElementById('openFolderBtn').style.display = 'block';
            
            // Update progress to 100%
            updateProgress(100, result.files ? result.files.length : 0, result.files ? result.files.length : 0, 'Migration completed!');
            
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        showAlert('Migration failed: ' + error.message, 'danger');
    } finally {
        // Re-enable button
        processBtn.disabled = false;
        processBtn.innerHTML = originalHTML;
    }
});

// Update progress display
function updateProgress(percentage, current, total, message) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const currentCount = document.getElementById('currentCount');
    const totalCount = document.getElementById('totalCount');
    const progressMessage = document.getElementById('progressMessage');
    
    progressBar.style.width = percentage + '%';
    progressBar.setAttribute('aria-valuenow', percentage);
    progressText.textContent = Math.round(percentage) + '%';
    
    currentCount.textContent = current;
    totalCount.textContent = total;
    
    progressMessage.textContent = message;
    
    // Change color based on percentage
    if (percentage === 100) {
        progressBar.classList.remove('bg-primary', 'bg-warning');
        progressBar.classList.add('bg-success');
    } else if (percentage > 50) {
        progressBar.classList.remove('bg-primary');
        progressBar.classList.add('bg-warning');
    }
}

// Open Data Folder
document.getElementById('openFolderBtn').addEventListener('click', async function() {
    try {
        const response = await fetch('/open-data-folder', {
            method: 'POST'
        });
        
        const result = await response.json();
        
        if (!result.success) {
            showAlert('Could not open data folder: ' + (result.message || 'Unknown error'), 'warning');
        }
        
    } catch (error) {
        showAlert('Error opening folder: ' + error.message, 'warning');
    }
});

// Polling for migration status (optional - for real-time updates)
let statusInterval = null;

function startStatusPolling() {
    statusInterval = setInterval(async () => {
        try {
            const response = await fetch('/migration-status');
            const status = await response.json();
            
            if (status.is_running) {
                updateProgress(
                    status.percentage,
                    status.current,
                    status.total,
                    status.message
                );
            } else if (status.completed) {
                stopStatusPolling();
            } else if (status.error) {
                showAlert('Error: ' + status.error, 'danger');
                stopStatusPolling();
            }
            
        } catch (error) {
            console.error('Status polling error:', error);
        }
    }, 1000); // Poll every second
}

function stopStatusPolling() {
    if (statusInterval) {
        clearInterval(statusInterval);
        statusInterval = null;
    }
}

// Enter key navigation
document.getElementById('host').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('user').focus();
    }
});

document.getElementById('user').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('password').focus();
    }
});

document.getElementById('password').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('database').focus();
    }
});

document.getElementById('database').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('date').focus();
    }
});

// Console welcome message
console.log('%c Nagagold Migration Tool ', 'background: #2196F3; color: white; font-size: 16px; padding: 5px 10px; border-radius: 5px;');
console.log('Web Interface v2.0.0 - Flask + Bootstrap 5');
console.log('© 2026 Nagatech SI Team');
