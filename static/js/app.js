// Global variables to store generated content
let generatedPrivateKey = '';
let generatedPublicKey = '';
let generatedCSR = '';
let signedCertificate = '';

// Utility functions
function showStatus(message, type = 'success') {
    const statusDiv = document.getElementById('statusMessages');
    const alertClass = type === 'success' ? 'alert-success' : type === 'error' ? 'alert-danger' : 'alert-warning';
    
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <span class="status-indicator status-${type}"></span>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    statusDiv.innerHTML = alertHtml;
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alerts = statusDiv.querySelectorAll('.alert');
        alerts.forEach(alert => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
}

function clearStatus() {
    document.getElementById('statusMessages').innerHTML = '';
}

// Key Generation
async function generateKey() {
    clearStatus();
    
    const keySize = document.getElementById('keySize').value;
    
    try {
        const response = await fetch('/generate_key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                key_size: parseInt(keySize)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            generatedPrivateKey = data.private_key;
            generatedPublicKey = data.public_key;
            
            document.getElementById('privateKey').value = data.private_key;
            document.getElementById('publicKey').value = data.public_key;
            
            showStatus('Key pair generated successfully!', 'success');
        } else {
            showStatus('Error generating key pair: ' + data.error, 'error');
        }
    } catch (error) {
        showStatus('Error generating key pair: ' + error.message, 'error');
    }
}

// CSR Generation
async function generateCSR() {
    clearStatus();
    
    const privateKey = document.getElementById('csrPrivateKey').value.trim();
    const country = document.getElementById('country').value.trim();
    const state = document.getElementById('state').value.trim();
    const locality = document.getElementById('locality').value.trim();
    const organization = document.getElementById('organization').value.trim();
    const organizationalUnit = document.getElementById('organizationalUnit').value.trim();
    const commonName = document.getElementById('commonName').value.trim();
    const dnsNames = document.getElementById('dnsNames').value.trim();
    
    if (!privateKey) {
        showStatus('Please provide a private key', 'error');
        return;
    }
    
    if (!commonName) {
        showStatus('Please provide a common name', 'error');
        return;
    }
    
    try {
        const response = await fetch('/generate_csr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                private_key: privateKey,
                country: country,
                state: state,
                locality: locality,
                organization: organization,
                organizational_unit: organizationalUnit,
                common_name: commonName,
                dns_names: dnsNames ? dnsNames.split(',').map(name => name.trim()) : []
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            generatedCSR = data.csr;
            document.getElementById('generatedCSR').value = data.csr;
            showStatus('CSR generated successfully!', 'success');
        } else {
            showStatus('Error generating CSR: ' + data.error, 'error');
        }
    } catch (error) {
        showStatus('Error generating CSR: ' + error.message, 'error');
    }
}

// Certificate Signing
async function signCertificate() {
    clearStatus();
    
    const rootCertificate = document.getElementById('rootCertificate').value.trim();
    const rootPrivateKey = document.getElementById('rootPrivateKey').value.trim();
    const csrToSign = document.getElementById('csrToSign').value.trim();
    const validityDays = document.getElementById('validityDays').value;
    const dnsNames = document.getElementById('signDnsNames').value.trim();
    
    if (!rootCertificate || !rootPrivateKey || !csrToSign) {
        showStatus('Please provide root certificate, root private key, and CSR', 'error');
        return;
    }
    
    try {
        const response = await fetch('/sign_certificate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                root_certificate: rootCertificate,
                root_private_key: rootPrivateKey,
                csr: csrToSign,
                validity_days: parseInt(validityDays),
                dns_names: dnsNames ? dnsNames.split(',').map(name => name.trim()) : []
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            signedCertificate = data.certificate;
            document.getElementById('signedCertificate').value = data.certificate;
            showStatus('Certificate signed successfully!', 'success');
        } else {
            showStatus('Error signing certificate: ' + data.error, 'error');
        }
    } catch (error) {
        showStatus('Error signing certificate: ' + error.message, 'error');
    }
}

// File Download
async function downloadFile(fileType, filename) {
    let content = '';
    
    switch (fileType) {
        case 'private_key':
            content = generatedPrivateKey;
            break;
        case 'public_key':
            content = generatedPublicKey;
            break;
        case 'csr':
            content = generatedCSR;
            break;
        case 'certificate':
            content = signedCertificate;
            break;
        default:
            showStatus('Invalid file type', 'error');
            return;
    }
    
    if (!content) {
        showStatus('No content to download', 'error');
        return;
    }
    
    try {
        const response = await fetch(`/download/${fileType}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content: content,
                filename: filename
            })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
            showStatus('File downloaded successfully!', 'success');
        } else {
            showStatus('Error downloading file', 'error');
        }
    } catch (error) {
        showStatus('Error downloading file: ' + error.message, 'error');
    }
}

// File Upload
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        clearStatus();
        
        const certFile = document.getElementById('rootCertFile').files[0];
        const keyFile = document.getElementById('rootKeyFile').files[0];
        
        if (!certFile || !keyFile) {
            showStatus('Please select both certificate and private key files', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('root_certificate', certFile);
        formData.append('root_private_key', keyFile);
        
        try {
            const response = await fetch('/upload_root', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Populate the certificate signing form with uploaded data
                document.getElementById('rootCertificate').value = data.certificate;
                document.getElementById('rootPrivateKey').value = data.private_key;
                
                // Switch to certificate signing tab
                const signTab = new bootstrap.Tab(document.getElementById('sign-tab'));
                signTab.show();
                
                showStatus(data.message, 'success');
            } else {
                showStatus('Error uploading files: ' + data.error, 'error');
            }
        } catch (error) {
            showStatus('Error uploading files: ' + error.message, 'error');
        }
    });
});

// Tab switching to populate forms
document.addEventListener('DOMContentLoaded', function() {
    // When switching to CSR tab, populate private key if available
    const csrTab = document.getElementById('csr-tab');
    csrTab.addEventListener('shown.bs.tab', function() {
        if (generatedPrivateKey) {
            document.getElementById('csrPrivateKey').value = generatedPrivateKey;
        }
    });
    
    // When switching to sign tab, populate CSR if available
    const signTab = document.getElementById('sign-tab');
    signTab.addEventListener('shown.bs.tab', function() {
        if (generatedCSR) {
            document.getElementById('csrToSign').value = generatedCSR;
        }
    });
});

// Copy to clipboard functionality
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showStatus('Copied to clipboard!', 'success');
    }, function(err) {
        showStatus('Failed to copy: ' + err, 'error');
    });
}

// Add copy buttons to textareas
document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('.text-area');
    textareas.forEach(textarea => {
        const copyButton = document.createElement('button');
        copyButton.className = 'btn btn-sm btn-outline-secondary ms-2';
        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
        copyButton.onclick = function() {
            copyToClipboard(textarea.value);
        };
        
        const container = textarea.parentElement;
        const downloadButton = container.querySelector('.btn-outline-primary');
        if (downloadButton) {
            downloadButton.parentNode.insertBefore(copyButton, downloadButton.nextSibling);
        }
    });
});

