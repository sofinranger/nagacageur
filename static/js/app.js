// NagaCageur - Database Maintenance Tool - JavaScript

// Global variables
let allTables = [];

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
    
    // Auto-dismiss after 5 seconds for success messages
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

// Load Tables
document.getElementById('loadTablesBtn').addEventListener('click', async function() {
    const btn = this;
    const originalHTML = btn.innerHTML;
    
    // Disable button and show loading
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
    
    clearAlerts();
    
    // Get form data
    const formData = {
        host: document.getElementById('host').value,
        user: document.getElementById('user').value,
        password: document.getElementById('password').value,
        database: document.getElementById('database').value
    };
    
    try {
        const response = await fetch('/get-tables', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success && result.tables) {
            allTables = result.tables;
            displayTables(result.tables);
            document.getElementById('tableSection').style.display = 'block';
            document.getElementById('processBtn').disabled = false;
            showAlert(`✓ Loaded ${result.tables.length} tables successfully!`, 'success');
        } else {
            showAlert(result.message || 'Failed to load tables', 'danger');
        }
        
    } catch (error) {
        showAlert('Failed to load tables: ' + error.message, 'danger');
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }
});

// Display tables in list
function displayTables(tables) {
    const tableList = document.getElementById('tableList');
    tableList.innerHTML = '';
    
    tables.forEach((table, index) => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <input type="checkbox" 
                       class="form-check-input table-checkbox" 
                       id="table_${index}" 
                       value="${table.name}"
                       checked>
            </td>
            <td>
                <label for="table_${index}" class="form-check-label" style="cursor: pointer;">
                    ${table.name}
                </label>
            </td>
            <td class="text-end">${table.rows ? table.rows.toLocaleString() : '0'}</td>
            <td class="text-end">${table.size || '-'}</td>
        `;
        tableList.appendChild(row);
    });
    
    // Update process button state
    updateProcessButtonState();
}

// Select All
document.getElementById('selectAllBtn').addEventListener('click', function() {
    const checkboxes = document.querySelectorAll('.table-checkbox');
    checkboxes.forEach(cb => cb.checked = true);
    document.getElementById('checkAllCheckbox').checked = true;
    updateProcessButtonState();
});

// Deselect All
document.getElementById('deselectAllBtn').addEventListener('click', function() {
    const checkboxes = document.querySelectorAll('.table-checkbox');
    checkboxes.forEach(cb => cb.checked = false);
    document.getElementById('checkAllCheckbox').checked = false;
    updateProcessButtonState();
});

// Check All Checkbox
document.getElementById('checkAllCheckbox').addEventListener('change', function() {
    const checkboxes = document.querySelectorAll('.table-checkbox');
    checkboxes.forEach(cb => cb.checked = this.checked);
    updateProcessButtonState();
});

// Individual checkbox change
document.addEventListener('change', function(e) {
    if (e.target.classList.contains('table-checkbox')) {
        updateProcessButtonState();
        
        // Update checkAll checkbox
        const checkboxes = document.querySelectorAll('.table-checkbox');
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        document.getElementById('checkAllCheckbox').checked = allChecked;
    }
});

// Update process button state
function updateProcessButtonState() {
    const checkboxes = document.querySelectorAll('.table-checkbox:checked');
    const processBtn = document.getElementById('processBtn');
    processBtn.disabled = checkboxes.length === 0;
}

// Maintenance Form Submit
document.getElementById('maintenanceForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const processBtn = document.getElementById('processBtn');
    const originalHTML = processBtn.innerHTML;
    
    // Get selected tables
    const selectedTables = Array.from(document.querySelectorAll('.table-checkbox:checked'))
        .map(cb => cb.value);
    
    if (selectedTables.length === 0) {
        showAlert('Please select at least one table to check!', 'warning');
        return;
    }
    
    // Disable button and show loading
    processBtn.disabled = true;
    processBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
    
    clearAlerts();
    
    // Show progress section
    const progressSection = document.getElementById('progressSection');
    progressSection.style.display = 'block';
    
    // Hide results section
    document.getElementById('resultsSection').style.display = 'none';
    
    // Reset progress
    updateProgress(0, 0, selectedTables.length, 'Starting maintenance...');
    
    // Get form data
    const formData = {
        host: document.getElementById('host').value,
        user: document.getElementById('user').value,
        password: document.getElementById('password').value,
        database: document.getElementById('database').value,
        tables: selectedTables
    };
    
    try {
        // Start maintenance
        const response = await fetch('/start-maintenance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        if (result.success) {
            showAlert(result.message, 'success');
            
            // Display results
            displayResults(result.results);
            
            // Show open folder button
            document.getElementById('openFolderBtn').style.display = 'block';
            
            // Update progress to 100%
            updateProgress(100, selectedTables.length, selectedTables.length, 'Maintenance completed!');
            
        } else {
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        showAlert('Maintenance failed: ' + error.message, 'danger');
    } finally {
        // Re-enable button
        processBtn.disabled = false;
        processBtn.innerHTML = originalHTML;
    }
});

// Display maintenance results
function displayResults(results) {
    const resultsList = document.getElementById('resultsList');
    resultsList.innerHTML = '';
    
    results.forEach(result => {
        const row = document.createElement('tr');
        
        // Status badge
        let statusBadge = '';
        if (result.status === 'OK') {
            statusBadge = '<span class="badge bg-success">OK</span>';
        } else if (result.status === 'ERROR') {
            statusBadge = '<span class="badge bg-danger">ERROR</span>';
        } else {
            statusBadge = '<span class="badge bg-warning">WARNING</span>';
        }
        
        // Action badge
        let actionBadge = '';
        if (result.action === 'None') {
            actionBadge = '<span class="badge bg-secondary">None</span>';
        } else if (result.action === 'REPAIR') {
            actionBadge = '<span class="badge bg-warning">REPAIR</span>';
        } else if (result.action === 'REPAIR + OPTIMIZE') {
            actionBadge = '<span class="badge bg-info">REPAIR + OPTIMIZE</span>';
        } else if (result.action === 'OPTIMIZE') {
            actionBadge = '<span class="badge bg-primary">OPTIMIZE</span>';
        }
        
        row.innerHTML = `
            <td>${result.table}</td>
            <td>${statusBadge}</td>
            <td>${actionBadge}</td>
            <td>${result.result}</td>
        `;
        resultsList.appendChild(row);
    });
    
    // Show results section
    document.getElementById('resultsSection').style.display = 'block';
}

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
            showAlert('Could not open log folder: ' + (result.message || 'Unknown error'), 'warning');
        }
        
    } catch (error) {
        showAlert('Error opening folder: ' + error.message, 'warning');
    }
});

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

// Console welcome message
console.log('%c NagaCageur - Database Maintenance & Data Management Tool ', 'background: linear-gradient(135deg, #FF9A56 0%, #FF8C42 100%); color: white; font-size: 16px; padding: 8px 16px; border-radius: 8px; font-weight: 600;');
console.log('%c Web Interface v2.1.0 - Flask + Bootstrap 5 ', 'background: #2C3E50; color: white; padding: 5px 12px; border-radius: 5px;');
console.log('%c Multi-Tool System: 1) Table Maintenance | 2) TH Barang Saldo Checker | 3) Smart Audit Toko ', 'color: #FF9A56; font-weight: bold; font-size: 14px;');
console.log('%c © 2026 Nagatech Sistem Integrator (NGTC) ', 'color: #546E7A; font-style: italic;');


// ============================================================================
// TOOL 2: TH BARANG SALDO CHECKER
// ============================================================================

// Set default date to last month and restrict to last month only
const today = new Date();
let lastMonthYear = today.getFullYear();
let lastMonthMonth = today.getMonth() + 1; // Convert to 1-indexed (1-12)

// Calculate last month
if (lastMonthMonth === 1) {
    // If current month is January (1), go back to December (12) of previous year
    lastMonthYear = lastMonthYear - 1;
    lastMonthMonth = 12;
} else {
    // Otherwise just subtract 1 from current month
    lastMonthMonth = lastMonthMonth - 1;
}

// Format as YYYY-MM
const lastMonthStr = `${lastMonthYear}-${String(lastMonthMonth).padStart(2, '0')}`;

console.log('Current date:', today.toISOString().slice(0, 10));
console.log('Last month calculated:', lastMonthStr);

const checkDateInput = document.getElementById('checkDate');
checkDateInput.value = lastMonthStr;
checkDateInput.max = lastMonthStr;
checkDateInput.min = lastMonthStr;

// Add helper text
const checkDateLabel = checkDateInput.previousElementSibling;
const helperText = document.createElement('small');
helperText.className = 'text-muted d-block mt-1';
helperText.innerHTML = `<i class="bi bi-info-circle"></i> Only last month (${lastMonthStr}) can be processed`;
checkDateInput.parentElement.appendChild(helperText);

// Toggle password visibility for Tool 2
document.getElementById('togglePassword2').addEventListener('click', function() {
    const passwordInput = document.getElementById('password2');
    const passwordIcon = document.getElementById('passwordIcon2');
    
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

// Check Saldo Button
document.getElementById('checkSaldoBtn').addEventListener('click', async function() {
    const btn = this;
    const originalHTML = btn.innerHTML;
    
    // Disable button and show loading
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Checking...';
    
    clearAlerts();
    
    // Hide previous results
    document.getElementById('checkResultsSection').style.display = 'none';
    document.getElementById('fixingButtonContainer').style.display = 'none';
    document.getElementById('creatingButtonContainer').style.display = 'none';
    document.getElementById('fixProgressSection').style.display = 'none';
    
    // Get form data
    const formData = {
        host: document.getElementById('host2').value,
        user: document.getElementById('user2').value,
        password: document.getElementById('password2').value,
        database: document.getElementById('database2').value,
        checkDate: document.getElementById('checkDate').value
    };
    
    try {
        const response = await fetch('/check-saldo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        // Show results section
        document.getElementById('checkResultsSection').style.display = 'block';
        const messageDiv = document.getElementById('checkResultsMessage');
        messageDiv.innerHTML = result.message;
        
        if (result.success && result.needsFixing) {
            // Show fixing button
            document.getElementById('fixingButtonContainer').style.display = 'block';
            document.getElementById('targetTableName').textContent = result.monthlyTable;
            
            // Store data for fixing
            document.getElementById('startFixingBtn').dataset.checkDate = result.checkDate;
            document.getElementById('startFixingBtn').dataset.monthlyTable = result.monthlyTable;
            
            messageDiv.className = 'alert alert-warning';
        } else if (result.success && result.needsCreating) {
            // Show create table button
            document.getElementById('creatingButtonContainer').style.display = 'block';
            document.getElementById('createTableName').textContent = result.monthlyTable;
            document.getElementById('createTableName2').textContent = result.monthlyTable;
            
            // Store data for creating
            document.getElementById('startCreatingBtn').dataset.checkDate = result.checkDate;
            document.getElementById('startCreatingBtn').dataset.monthlyTable = result.monthlyTable;
            
            messageDiv.className = 'alert alert-warning';
        } else if (result.success) {
            messageDiv.className = 'alert alert-success';
        } else {
            messageDiv.className = 'alert alert-danger';
        }
        
    } catch (error) {
        showAlert('Check failed: ' + error.message, 'danger');
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }
});

// Start Fixing Button - Show Confirmation Modal
document.getElementById('startFixingBtn').addEventListener('click', function() {
    const checkDate = this.dataset.checkDate;
    const monthlyTable = this.dataset.monthlyTable;
    
    // Update modal content
    document.getElementById('modalCheckDate').textContent = checkDate;
    document.getElementById('modalMonthlyTable').textContent = monthlyTable;
    
    // Show modal
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmFixingModal'));
    confirmModal.show();
});

// Confirm Fixing Button - Execute Fixing
document.getElementById('confirmFixingBtn').addEventListener('click', async function() {
    // Close the confirmation modal
    const confirmModal = bootstrap.Modal.getInstance(document.getElementById('confirmFixingModal'));
    confirmModal.hide();
    
    const btn = document.getElementById('startFixingBtn');
    const checkDate = btn.dataset.checkDate;
    const monthlyTable = btn.dataset.monthlyTable;
    const originalHTML = btn.innerHTML;
    
    // Disable button and show loading
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
    
    // Show progress section
    document.getElementById('fixProgressSection').style.display = 'block';
    document.getElementById('fixProgressMessage').innerHTML = '<i class="bi bi-hourglass-split"></i> Moving data... Please wait...';
    
    // Get form data
    const formData = {
        host: document.getElementById('host2').value,
        user: document.getElementById('user2').value,
        password: document.getElementById('password2').value,
        database: document.getElementById('database2').value,
        checkDate: checkDate,
        monthlyTable: monthlyTable
    };
    
    try {
        const response = await fetch('/fix-saldo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        const progressMessage = document.getElementById('fixProgressMessage');
        
        if (result.success) {
            progressMessage.className = 'alert alert-success';
            progressMessage.innerHTML = `<i class="bi bi-check-circle-fill me-2"></i>${result.message}`;
            
            // Hide fixing button after success
            document.getElementById('fixingButtonContainer').style.display = 'none';
            
            // Show success alert
            showAlert(result.message, 'success');
        } else {
            progressMessage.className = 'alert alert-danger';
            progressMessage.innerHTML = `<i class="bi bi-x-circle-fill me-2"></i>${result.message}`;
            
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        const progressMessage = document.getElementById('fixProgressMessage');
        progressMessage.className = 'alert alert-danger';
        progressMessage.innerHTML = `<i class="bi bi-x-circle-fill me-2"></i>Error: ${error.message}`;
        
        showAlert('Fixing failed: ' + error.message, 'danger');
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }
});


// Start Creating Table Button - Show Confirmation Modal
document.getElementById('startCreatingBtn').addEventListener('click', function() {
    const monthlyTable = this.dataset.monthlyTable;
    
    // Update modal content
    document.getElementById('modalCreateTableName').textContent = monthlyTable;
    
    // Show modal
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmCreateTableModal'));
    confirmModal.show();
});

// Confirm Create Table Button - Execute Creation
document.getElementById('confirmCreateTableBtn').addEventListener('click', async function() {
    // Close the confirmation modal
    const confirmModal = bootstrap.Modal.getInstance(document.getElementById('confirmCreateTableModal'));
    confirmModal.hide();
    
    const btn = document.getElementById('startCreatingBtn');
    const checkDate = btn.dataset.checkDate;
    const monthlyTable = btn.dataset.monthlyTable;
    const originalHTML = btn.innerHTML;
    
    // Disable button and show loading
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Creating...';
    
    // Show progress section
    document.getElementById('fixProgressSection').style.display = 'block';
    document.getElementById('fixProgressMessage').innerHTML = '<i class="bi bi-hourglass-split"></i> Creating table... Please wait...';
    
    // Get form data
    const formData = {
        host: document.getElementById('host2').value,
        user: document.getElementById('user2').value,
        password: document.getElementById('password2').value,
        database: document.getElementById('database2').value,
        checkDate: checkDate,
        monthlyTable: monthlyTable
    };
    
    try {
        const response = await fetch('/create-table-saldo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const result = await response.json();
        
        const progressMessage = document.getElementById('fixProgressMessage');
        
        if (result.success) {
            progressMessage.className = 'alert alert-success';
            progressMessage.innerHTML = `<i class="bi bi-check-circle-fill me-2"></i>${result.message}`;
            
            // Hide creating button after success
            document.getElementById('creatingButtonContainer').style.display = 'none';
            
            // Update check results message
            document.getElementById('checkResultsMessage').className = 'alert alert-success';
            document.getElementById('checkResultsMessage').innerHTML = `✓ Table ${monthlyTable} has been created successfully! You can now check again to verify.`;
            
            // Show success alert
            showAlert(result.message, 'success');
        } else {
            progressMessage.className = 'alert alert-danger';
            progressMessage.innerHTML = `<i class="bi bi-x-circle-fill me-2"></i>${result.message}`;
            
            showAlert(result.message, 'danger');
        }
        
    } catch (error) {
        const progressMessage = document.getElementById('fixProgressMessage');
        progressMessage.className = 'alert alert-danger';
        progressMessage.innerHTML = `<i class="bi bi-x-circle-fill me-2"></i>Error: ${error.message}`;
        
        showAlert('Creating table failed: ' + error.message, 'danger');
    } finally {
        // Re-enable button
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }
});


// ============================================================================
// TOOL 3: SMART AUDIT TOKO
// ============================================================================

// Toggle password visibility for Tool 3
document.getElementById('togglePassword3').addEventListener('click', function() {
    const passwordInput = document.getElementById('password3');
    const passwordIcon = document.getElementById('passwordIcon3');
    
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

// Start Audit Button - Show Confirmation Modal
document.getElementById('startAuditBtn').addEventListener('click', function() {
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmAuditModal'));
    confirmModal.show();
});

// Confirm Audit Button - Execute Audit
document.getElementById('confirmAuditBtn').addEventListener('click', async function() {
    // Close the confirmation modal
    const confirmModal = bootstrap.Modal.getInstance(document.getElementById('confirmAuditModal'));
    confirmModal.hide();
    
    const btn = document.getElementById('startAuditBtn');
    const originalHTML = btn.innerHTML;
    
    // Disable button and show loading
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Running Audit...';
    
    clearAlerts();
    
    // Show progress section
    document.getElementById('auditProgressSection').style.display = 'block';
    document.getElementById('auditResultsSection').style.display = 'none';
    
    const progressBar = document.getElementById('auditProgressBar');
    const progressText = document.getElementById('auditProgressText');
    const progressStatus = document.getElementById('auditProgressStatus');
    
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    progressStatus.textContent = 'Connecting to database...';
    
    // Get form data
    const formData = {
        host: document.getElementById('host3').value,
        user: document.getElementById('user3').value,
        password: document.getElementById('password3').value,
        database: document.getElementById('database3').value
    };
    
    try {
        // Use fetch with streaming response
        const response = await fetch('/smart-audit-stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
            const {done, value} = await reader.read();
            
            if (done) break;
            
            buffer += decoder.decode(value, {stream: true});
            
            // Process complete messages (separated by double newlines)
            let lines = buffer.split('\n\n');
            buffer = lines.pop(); // Keep the incomplete line in the buffer
            
            for (let line of lines) {
                if (line.startsWith('data: ')) {
                    const jsonStr = line.substring(6);
                    try {
                        const data = JSON.parse(jsonStr);
                        console.log('[AUDIT] Received:', data);
                        
                        if (data.error) {
                            // Error occurred
                            document.getElementById('auditProgressSection').style.display = 'none';
                            showAlert(data.message, 'danger');
                            btn.disabled = false;
                            btn.innerHTML = originalHTML;
                            return;
                        } else if (data.type === 'progress') {
                            // Handle different progress steps
                            if (data.step === 'query' || data.step === 'query_phase2') {
                                const percent = data.step === 'query' ? 5 : 50;
                                progressBar.style.width = percent + '%';
                                progressText.textContent = percent + '%';
                                progressStatus.textContent = data.message;
                            } else if (data.step === 'start_phase1') {
                                progressBar.style.width = '10%';
                                progressText.textContent = '10%';
                                progressStatus.textContent = data.message;
                            } else if (data.step === 'processing_phase1') {
                                // Phase 1: 10% - 50%
                                const percent = Math.min(10 + Math.round((data.current / data.total) * 40), 50);
                                progressBar.style.width = percent + '%';
                                progressText.textContent = percent + '%';
                                progressStatus.textContent = data.message || `Phase 1: ${data.current}/${data.total} - ${data.kode_barang}`;
                            } else if (data.step === 'start_phase2') {
                                progressBar.style.width = '55%';
                                progressText.textContent = '55%';
                                progressStatus.textContent = data.message;
                            } else if (data.step === 'processing_phase2') {
                                // Phase 2: 55% - 95%
                                const percent = Math.min(55 + Math.round((data.current / data.total) * 40), 95);
                                progressBar.style.width = percent + '%';
                                progressText.textContent = percent + '%';
                                progressStatus.textContent = data.message || `Phase 2: ${data.current}/${data.total} - ${data.kode_barang}`;
                            }
                        } else if (data.type === 'complete') {
                            // Audit completed
                            progressBar.style.width = '100%';
                            progressText.textContent = '100%';
                            progressStatus.textContent = 'Audit completed!';
                            
                            console.log('[AUDIT] Complete! Summary:', data.summary);
                            
                            // Update Phase 1 summary cards
                            document.getElementById('summaryTmBarang').textContent = data.summary.phase1.total_tm_barang.toLocaleString();
                            document.getElementById('summaryMatchTmToTt').textContent = data.summary.phase1.match_tm_to_tt.toLocaleString();
                            document.getElementById('summaryNotFoundTmToTt').textContent = data.summary.phase1.not_found.toLocaleString();
                            document.getElementById('summaryDuplicateTmToTt').textContent = data.summary.phase1.duplicate.toLocaleString();
                            
                            // Update Phase 2 summary cards
                            document.getElementById('summaryTtBarang').textContent = data.summary.phase2.total_tt_barang.toLocaleString();
                            document.getElementById('summaryMatchTtToTm').textContent = data.summary.phase2.match_tt_to_tm.toLocaleString();
                            document.getElementById('summaryNotFoundTtToTm').textContent = data.summary.phase2.not_found.toLocaleString();
                            document.getElementById('summaryDuplicateTtToTm').textContent = data.summary.phase2.duplicate.toLocaleString();
                            
                            // Update total issues count
                            document.getElementById('totalIssuesCount').textContent = data.summary.total_issues.toLocaleString();
                            
                            // Display issues in table
                            displayAuditResults(data.issues);
                            
                            // Store issues globally for fixing
                            window.auditIssues = data.issues;
                            window.auditFormData = formData;
                            
                            // Show/hide fix button based on fixable issues
                            const fixableIssues = data.issues.filter(issue => 
                                issue.issue === 'TM_DUPLICATE_IN_TT' || issue.issue === 'TM_NOT_IN_TT'
                            );
                            
                            if (fixableIssues.length > 0) {
                                document.getElementById('fixIssuesSection').style.display = 'block';
                            } else {
                                document.getElementById('fixIssuesSection').style.display = 'none';
                            }
                            
                            // Hide progress, show results
                            setTimeout(() => {
                                document.getElementById('auditProgressSection').style.display = 'none';
                                document.getElementById('auditResultsSection').style.display = 'block';
                                
                                // Show summary alert
                                const totalIssues = data.summary.total_issues;
                                if (totalIssues === 0) {
                                    showAlert('✓ Audit completed! No issues found. All data is consistent in both directions.', 'success');
                                } else {
                                    showAlert(`⚠ Audit completed! Found ${totalIssues} issue(s). Please review the results below.`, 'warning');
                                }
                                
                                // Re-enable button
                                btn.disabled = false;
                                btn.innerHTML = originalHTML;
                            }, 500);
                            
                            return;
                        } else if (data.type === 'error') {
                            // Error during processing
                            document.getElementById('auditProgressSection').style.display = 'none';
                            showAlert(data.message, 'danger');
                            btn.disabled = false;
                            btn.innerHTML = originalHTML;
                            return;
                        }
                    } catch (parseError) {
                        console.error('[AUDIT] Parse error:', parseError, 'Data:', jsonStr);
                    }
                }
            }
        }
        
    } catch (error) {
        console.error('[AUDIT] Fetch error:', error);
        document.getElementById('auditProgressSection').style.display = 'none';
        showAlert('Connection error during audit: ' + error.message, 'danger');
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }
});

// Display Audit Results in Table
function displayAuditResults(issues) {
    console.log('[AUDIT] displayAuditResults called with', issues.length, 'issues');
    
    const tableBody = document.getElementById('auditResultsTableBody');
    
    if (!tableBody) {
        console.error('[AUDIT] Table element not found!');
        return;
    }
    
    tableBody.innerHTML = '';
    
    if (issues.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="text-center py-4">
                    <i class="bi bi-check-circle-fill text-success" style="font-size: 3rem;"></i>
                    <p class="mt-2 mb-0 text-success fw-bold">No issues found! All data is consistent.</p>
                </td>
            </tr>
        `;
        return;
    }
    
    issues.forEach((issue, index) => {
        let badgeClass = '';
        let badgeText = '';
        let countValue = issue.count_tt || issue.count_tm || 0;
        
        // Determine badge style based on issue type
        if (issue.issue === 'TM_NOT_IN_TT' || issue.issue === 'TT_NOT_IN_TM') {
            badgeClass = 'badge-danger';
            badgeText = issue.issue === 'TM_NOT_IN_TT' ? 'TM NOT IN TT' : 'TT NOT IN TM';
        } else if (issue.issue === 'TM_DUPLICATE_IN_TT' || issue.issue === 'TT_DUPLICATE_IN_TM') {
            badgeClass = 'badge-warning';
            badgeText = issue.issue === 'TM_DUPLICATE_IN_TT' ? 'TM DUP IN TT' : 'TT DUP IN TM';
        } else if (issue.issue === 'NOT_FOUND') {
            badgeClass = 'badge-danger';
            badgeText = 'NOT FOUND';
        } else if (issue.issue === 'DUPLICATE') {
            badgeClass = 'badge-warning';
            badgeText = 'DUPLICATE';
        }
        
        const row = `
            <tr>
                <td>${index + 1}</td>
                <td><code>${issue.kode_barang}</code></td>
                <td><code>${issue.kode_lokasi}</code></td>
                <td class="text-center">${countValue}</td>
                <td>
                    <span class="badge ${badgeClass}">${badgeText}</span>
                    <br>
                    <small class="text-muted">${issue.issue_text}</small>
                </td>
            </tr>
        `;
        
        tableBody.innerHTML += row;
    });
}
// Fix Issues Button - Show Confirmation Modal
document.getElementById('fixIssuesBtn').addEventListener('click', function() {
    const fixableIssues = window.auditIssues.filter(issue => 
        issue.issue === 'TM_DUPLICATE_IN_TT' || issue.issue === 'TM_NOT_IN_TT'
    );
    
    // Update modal with total fixable issues
    document.getElementById('modalTotalIssues').textContent = fixableIssues.length;
    
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmFixSmartAuditModal'));
    confirmModal.show();
});

// Confirm Fix Smart Audit Button - Execute Fixing
document.getElementById('confirmFixSmartAuditBtn').addEventListener('click', async function() {
    // Close the confirmation modal
    const confirmModal = bootstrap.Modal.getInstance(document.getElementById('confirmFixSmartAuditModal'));
    confirmModal.hide();
    
    const btn = document.getElementById('fixIssuesBtn');
    const originalHTML = btn.innerHTML;
    
    // Disable button and show loading
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Fixing...';
    
    clearAlerts();
    
    // Show fixing progress section
    document.getElementById('fixingProgressSection').style.display = 'block';
    document.getElementById('fixingResultsSection').style.display = 'none';
    
    const progressBar = document.getElementById('fixingProgressBar');
    const progressText = document.getElementById('fixingProgressText');
    const progressStatus = document.getElementById('fixingProgressStatus');
    
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    progressStatus.textContent = 'Starting fix process...';
    
    // Prepare request data
    const requestData = {
        host: window.auditFormData.host,
        user: window.auditFormData.user,
        password: window.auditFormData.password,
        database: window.auditFormData.database,
        issues: window.auditIssues
    };
    
    try {
        // Use fetch with streaming response
        const response = await fetch('/fix-smart-audit-stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
            const {done, value} = await reader.read();
            
            if (done) break;
            
            buffer += decoder.decode(value, {stream: true});
            
            // Process complete messages (separated by double newlines)
            let lines = buffer.split('\n\n');
            buffer = lines.pop(); // Keep the incomplete line in the buffer
            
            for (let line of lines) {
                if (line.startsWith('data: ')) {
                    const jsonStr = line.substring(6);
                    try {
                        const data = JSON.parse(jsonStr);
                        console.log('[FIXING] Received:', data);
                        
                        if (data.error) {
                            // Error occurred
                            document.getElementById('fixingProgressSection').style.display = 'none';
                            showAlert(data.message, 'danger');
                            btn.disabled = false;
                            btn.innerHTML = originalHTML;
                            return;
                        } else if (data.type === 'progress') {
                            // Handle different progress steps
                            if (data.step === 'start') {
                                progressBar.style.width = '5%';
                                progressText.textContent = '5%';
                                progressStatus.textContent = data.message;
                            } else if (data.step === 'fixing_duplicates') {
                                progressBar.style.width = '10%';
                                progressText.textContent = '10%';
                                progressStatus.textContent = data.message;
                            } else if (data.step === 'inserting_missing') {
                                progressBar.style.width = '50%';
                                progressText.textContent = '50%';
                                progressStatus.textContent = data.message;
                            } else if (data.step === 'processing') {
                                progressBar.style.width = data.percent + '%';
                                progressText.textContent = data.percent + '%';
                                progressStatus.textContent = data.message;
                            }
                        } else if (data.type === 'warning') {
                            // Warning during processing
                            console.warn('[FIXING]', data.message);
                        } else if (data.type === 'complete') {
                            // Fixing completed
                            progressBar.style.width = '100%';
                            progressText.textContent = '100%';
                            progressStatus.textContent = 'Fixing completed!';
                            
                            console.log('[FIXING] Complete! Result:', data.result);
                            
                            // Update fixing results display
                            document.getElementById('duplicatesDeleted').textContent = data.result.duplicates_deleted.toLocaleString();
                            document.getElementById('missingInserted').textContent = data.result.missing_inserted.toLocaleString();
                            document.getElementById('totalFixed').textContent = data.result.total_fixed.toLocaleString();
                            
                            // Hide progress, show results
                            setTimeout(() => {
                                document.getElementById('fixingProgressSection').style.display = 'none';
                                document.getElementById('fixingResultsSection').style.display = 'block';
                                
                                // Show success alert
                                showAlert(`✓ Fixing completed! ${data.result.total_fixed} issue(s) fixed successfully. (Duplicates deleted: ${data.result.duplicates_deleted}, Missing inserted: ${data.result.missing_inserted})`, 'success');
                                
                                // Hide fix button after successful fix
                                document.getElementById('fixIssuesSection').style.display = 'none';
                                
                                // Re-enable button
                                btn.disabled = false;
                                btn.innerHTML = originalHTML;
                            }, 500);
                            
                            return;
                        } else if (data.type === 'error') {
                            // Error during processing
                            document.getElementById('fixingProgressSection').style.display = 'none';
                            showAlert(data.message, 'danger');
                            btn.disabled = false;
                            btn.innerHTML = originalHTML;
                            return;
                        }
                    } catch (parseError) {
                        console.error('[FIXING] Parse error:', parseError, 'Data:', jsonStr);
                    }
                }
            }
        }
        
    } catch (error) {
        console.error('[FIXING] Fetch error:', error);
        document.getElementById('fixingProgressSection').style.display = 'none';
        showAlert('Connection error during fixing: ' + error.message, 'danger');
        btn.disabled = false;
        btn.innerHTML = originalHTML;
    }
});