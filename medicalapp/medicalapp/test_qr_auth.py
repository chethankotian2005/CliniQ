#!/usr/bin/env python
"""
Test QR scanner with proper authentication
"""
import os
import sys
import django

# Set up Django environment
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from adminpanel.models import AdminUser

def test_qr_scanner_with_auth():
    """Test QR scanner with proper authentication"""
    print("🔐 Testing QR Scanner with Authentication")
    print("=" * 50)
    
    # Create a test client
    client = Client()
    
    try:
        # Get admin user
        admin_user = User.objects.get(username='admin')
        print(f"✅ Admin user found: {admin_user.username}")
        
        # Login
        login_success = client.login(username='admin', password='admin123')
        if login_success:
            print("✅ Admin login successful")
        else:
            print("❌ Admin login failed")
            return False
            
        # Test QR scanner page
        response = client.get('/adminpanel/qr-scanner/')
        print(f"QR Scanner Page Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ QR scanner page accessible with authentication")
            
            # Check if key elements are in the page
            content = response.content.decode()
            
            checks = [
                ('start-scan button', 'id="start-scan"' in content),
                ('HTML5 QR library', 'html5-qrcode' in content),
                ('Manual entry', 'Manual Entry' in content),
                ('Process QR function', 'processQRCode' in content or 'processManualEntry' in content)
            ]
            
            for check_name, check_result in checks:
                status = "✅" if check_result else "❌"
                print(f"  {status} {check_name}")
                
            return all(check[1] for check in checks)
        else:
            print(f"❌ QR scanner page error: {response.status_code}")
            return False
            
    except User.DoesNotExist:
        print("❌ Admin user not found")
        return False
    except Exception as e:
        print(f"❌ Error testing authentication: {e}")
        return False

def test_manual_qr_api():
    """Test the QR API with authenticated client"""
    print("\n🔗 Testing QR API with Authentication")
    print("=" * 40)
    
    client = Client()
    
    try:
        # Login first
        client.login(username='admin', password='admin123')
        
        # Get a valid QR code
        from patients.models import Queue
        valid_booking = Queue.objects.filter(status='booked').first()
        
        if not valid_booking:
            print("❌ No valid bookings for testing")
            return False
            
        qr_code = valid_booking.qr_code
        print(f"Testing QR: {qr_code}")
        
        # Test the API
        response = client.post(
            '/patients/api/booking/qr-scan/',
            data={'qr_code': qr_code},
            content_type='application/json'
        )
        
        print(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"API Success: {response_data.get('success')}")
            
            if response_data.get('success'):
                print(f"✅ Patient: {response_data.get('patient_name')}")
                print(f"✅ Token: {response_data.get('token_number')}")
                print(f"✅ Department: {response_data.get('department')}")
                return True
            else:
                print(f"❌ API Error: {response_data.get('message')}")
                return False
        else:
            print(f"❌ API HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def create_simplified_qr_test():
    """Create a simplified QR test page that doesn't require auth"""
    print("\n🛠️ Creating Simplified QR Test Page")
    print("=" * 40)
    
    # Create a simple HTML page for testing
    simple_test_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Simple QR Test</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f8f9fa; }
        .container { max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }
        .btn { padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; margin: 5px; }
        .btn:hover { background: #0056b3; }
        .form-control { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; margin: 10px 0; }
        .alert { padding: 15px; margin: 10px 0; border-radius: 4px; }
        .alert-success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .alert-danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        .alert-info { background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
        #reader { width: 100%; max-width: 400px; margin: 20px auto; border: 2px dashed #28a745; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 QR Scanner Test Tool</h1>
        
        <div class="alert alert-info">
            <strong>Test QR Code:</strong> CLINIQ:BOOKING:12:65333ef0<br>
            <strong>Note:</strong> This page tests QR functionality without authentication.
        </div>

        <h3>📷 Camera QR Scanner</h3>
        <div id="reader"></div>
        <button id="start-camera" class="btn">Start Camera</button>
        <button id="stop-camera" class="btn" style="background: #dc3545;" disabled>Stop Camera</button>
        <div id="camera-result"></div>

        <h3>⌨️ Manual QR Testing</h3>
        <input type="text" id="manual-qr" class="form-control" placeholder="Paste QR code: CLINIQ:BOOKING:12:65333ef0" value="CLINIQ:BOOKING:12:65333ef0">
        <button id="test-qr" class="btn">Test QR Code</button>
        <div id="manual-result"></div>

        <h3>📋 Debug Log</h3>
        <div id="debug-log" style="background: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; min-height: 100px; max-height: 300px; overflow-y: auto;"></div>
    </div>

    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <script>
        let scanner = null;
        
        function log(message) {
            const logDiv = document.getElementById('debug-log');
            const time = new Date().toLocaleTimeString();
            logDiv.innerHTML += `[${time}] ${message}<br>`;
            logDiv.scrollTop = logDiv.scrollHeight;
            console.log(message);
        }
        
        function showResult(elementId, message, type = 'info') {
            const element = document.getElementById(elementId);
            element.innerHTML = `<div class="alert alert-${type}">${message}</div>`;
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            log('Page loaded - checking QR library...');
            
            if (typeof Html5QrcodeScanner !== 'undefined') {
                log('✅ HTML5 QR Code library loaded successfully');
            } else {
                log('❌ HTML5 QR Code library failed to load');
            }
        });
        
        // Start camera
        document.getElementById('start-camera').addEventListener('click', function() {
            log('Starting camera scanner...');
            
            try {
                scanner = new Html5QrcodeScanner("reader", {
                    fps: 10,
                    qrbox: { width: 250, height: 250 }
                }, false);
                
                scanner.render(
                    function(decodedText) {
                        log(`QR Code detected: ${decodedText}`);
                        showResult('camera-result', `QR Code detected: ${decodedText}`, 'success');
                        testQRCode(decodedText);
                    },
                    function(error) {
                        // Silent for scan errors
                    }
                );
                
                document.getElementById('start-camera').disabled = true;
                document.getElementById('stop-camera').disabled = false;
                log('Camera scanner started successfully');
                
            } catch (error) {
                log(`❌ Error starting camera: ${error.message}`);
                showResult('camera-result', `Error: ${error.message}`, 'danger');
            }
        });
        
        // Stop camera
        document.getElementById('stop-camera').addEventListener('click', function() {
            if (scanner) {
                scanner.clear();
                scanner = null;
            }
            document.getElementById('start-camera').disabled = false;
            document.getElementById('stop-camera').disabled = true;
            log('Camera scanner stopped');
            showResult('camera-result', 'Camera stopped', 'info');
        });
        
        // Manual test
        document.getElementById('test-qr').addEventListener('click', function() {
            const qrCode = document.getElementById('manual-qr').value.trim();
            if (!qrCode) {
                showResult('manual-result', 'Please enter a QR code', 'danger');
                return;
            }
            
            log(`Testing QR code manually: ${qrCode}`);
            testQRCode(qrCode);
        });
        
        // Test QR code
        function testQRCode(qrCode) {
            log(`Sending API request for QR: ${qrCode}`);
            showResult('manual-result', 'Processing QR code...', 'info');
            
            // Get CSRF token
            const csrfToken = getCookie('csrftoken');
            
            fetch('/patients/api/booking/qr-scan/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ qr_code: qrCode })
            })
            .then(response => {
                log(`API response status: ${response.status}`);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                log(`API response: ${JSON.stringify(data)}`);
                
                if (data.success) {
                    const message = `
                        <strong>✅ QR Code Processed Successfully!</strong><br>
                        Patient: ${data.patient_name}<br>
                        Token: ${data.token_number}<br>
                        Department: ${data.department}<br>
                        Message: ${data.message}
                    `;
                    showResult('manual-result', message, 'success');
                } else {
                    showResult('manual-result', `❌ Error: ${data.message}`, 'danger');
                }
            })
            .catch(error => {
                log(`❌ Network error: ${error.message}`);
                showResult('manual-result', `❌ Network Error: ${error.message}`, 'danger');
            });
        }
        
        // Get CSRF token
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }
    </script>
</body>
</html>'''
    
    # Save to static files or templates
    test_file = os.path.join(project_dir, 'static', 'qr_test.html')
    
    # Create static directory if it doesn't exist
    static_dir = os.path.join(project_dir, 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(simple_test_html)
        
    print(f"✅ Simple QR test page created")
    print(f"Access at: http://127.0.0.1:8000/static/qr_test.html")
    
    return test_file

def main():
    """Run comprehensive authentication-aware tests"""
    print("🔧 QR SCANNER AUTHENTICATION DEBUG")
    print("=" * 50)
    
    # Test with authentication
    auth_ok = test_qr_scanner_with_auth()
    
    # Test API with authentication  
    api_ok = test_manual_qr_api()
    
    # Create simple test page
    test_file = create_simplified_qr_test()
    
    print("\n" + "=" * 50)
    print("🎯 FINAL SUMMARY")
    print("=" * 50)
    print(f"QR Scanner (Auth): {'✅' if auth_ok else '❌'}")
    print(f"QR API (Auth): {'✅' if api_ok else '❌'}")
    
    if auth_ok and api_ok:
        print("\n🎉 QR Scanner is working with authentication!")
        print("\nTo test QR scanner:")
        print("1. Login to admin: http://127.0.0.1:8000/adminpanel/login/")
        print("2. Username: admin / Password: admin123")
        print("3. Go to QR scanner: http://127.0.0.1:8000/adminpanel/qr-scanner/")
        print("4. Use Manual Entry with: CLINIQ:BOOKING:12:65333ef0")
    else:
        print("\n❌ QR Scanner has authentication issues")
        
    print(f"\n🧪 Alternative test page: http://127.0.0.1:8000/static/qr_test.html")

if __name__ == "__main__":
    main()