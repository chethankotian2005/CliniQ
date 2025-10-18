"""
Fix for QR Scanner - Improved JavaScript with better error handling
"""

# Read the current QR scanner template
import os

template_path = "templates/adminpanel/qr_scanner.html"

# Create a JavaScript fix that can be injected
js_fix = """
// Enhanced QR Code processing with better error handling
function processQRCode(qrData) {
    console.log('Processing QR code:', qrData);
    updateScanStatus('info', 'Processing QR code...');
    
    // Simple fetch without CSRF token (API is @csrf_exempt)
    fetch('/patients/api/booking/qr-scan/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ qr_code: qrData })
    })
    .then(response => {
        console.log('API Response status:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('API Response data:', data);
        
        if (data.success) {
            console.log('Success! Token:', data.token_number);
            showSuccess(data);
            addToRecentScans(data, true);
            updateStats();
        } else {
            console.log('API Error:', data.message);
            showError(data.message);
            addToRecentScans({ message: data.message }, false);
        }
        
        // Resume scanning after a short delay
        setTimeout(() => {
            if (html5QrcodeScanner) {
                html5QrcodeScanner.resume();
                updateScanStatus('info', 'Scanner ready. Point camera at next QR code...');
            }
        }, 2000);
    })
    .catch(error => {
        console.error('Network Error:', error);
        showError('Network error: ' + error.message);
        setTimeout(() => {
            if (html5QrcodeScanner) {
                html5QrcodeScanner.resume();
                updateScanStatus('warning', 'Network error. Scanner ready for next code...');
            }
        }, 2000);
    });
}

// Enhanced manual entry processing
function processManualEntry() {
    const qrCode = document.getElementById('manual-qr-input').value.trim();
    const resultDiv = document.getElementById('manual-scan-result');
    
    console.log('Manual entry QR code:', qrCode);
    
    if (!qrCode) {
        resultDiv.innerHTML = '<div class="alert alert-warning">Please enter a QR code</div>';
        return;
    }
    
    resultDiv.innerHTML = '<div class="alert alert-info">Processing...</div>';
    
    // Add timeout to show processing is happening
    setTimeout(() => {
        processQRCode(qrCode);
    }, 100);
    
    // Close modal after a longer delay to see result
    setTimeout(() => {
        const modal = bootstrap.Modal.getInstance(document.getElementById('manualEntryModal'));
        if (modal) {
            modal.hide();
        }
    }, 3000);
}

// Enhanced error display
function showError(message) {
    console.error('Showing error:', message);
    
    const errorContent = document.getElementById('error-content');
    errorContent.innerHTML = '<p class="text-danger">' + message + '</p>';
    
    updateScanStatus('danger', message);
    
    const errorModal = new bootstrap.Modal(document.getElementById('errorModal'));
    errorModal.show();
    
    // Auto-close error modal after 5 seconds
    setTimeout(() => {
        errorModal.hide();
    }, 5000);
}
"""

print("QR Scanner JavaScript Fix")
print("=" * 30)
print(js_fix)
print("\nTo apply this fix:")
print("1. Open the QR scanner page in browser")
print("2. Open browser developer console (F12)")
print("3. Copy and paste the above JavaScript code")
print("4. Try manual entry with: CLINIQ:BOOKING:19:3520e40e")
print("\nThis will add better console logging and error handling.")