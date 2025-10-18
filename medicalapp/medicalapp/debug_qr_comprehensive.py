#!/usr/bin/env python
"""
Debug QR scanner - check all components
"""
import os
import sys
import django
import requests
import json

# Set up Django environment
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

def test_admin_login():
    """Test if admin login works"""
    print("🔐 Testing Admin Login")
    print("-" * 30)
    
    try:
        # Test login to admin panel
        response = requests.get('http://127.0.0.1:8000/adminpanel/login/')
        if response.status_code == 200:
            print("✅ Admin login page accessible")
        else:
            print(f"❌ Admin login page error: {response.status_code}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Cannot access admin login: {e}")
        return False

def test_qr_scanner_page():
    """Test if QR scanner page loads"""
    print("\n📷 Testing QR Scanner Page")
    print("-" * 30)
    
    try:
        # Test QR scanner page
        response = requests.get('http://127.0.0.1:8000/adminpanel/qr-scanner/')
        if response.status_code == 200:
            print("✅ QR scanner page accessible")
            
            # Check if HTML5 QR code library is referenced
            if 'html5-qrcode' in response.text:
                print("✅ HTML5 QR code library referenced")
            else:
                print("❌ HTML5 QR code library NOT found")
                
            # Check for key elements
            if 'start-scan' in response.text:
                print("✅ Start scan button found")
            else:
                print("❌ Start scan button NOT found")
                
        else:
            print(f"❌ QR scanner page error: {response.status_code}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Cannot access QR scanner page: {e}")
        return False

def test_qr_api_directly():
    """Test QR API endpoint directly"""
    print("\n🔗 Testing QR API Endpoint")
    print("-" * 30)
    
    # Get a valid QR code from database
    from patients.models import Queue
    
    valid_booking = Queue.objects.filter(status='booked').first()
    if not valid_booking:
        print("❌ No valid bookings found for testing")
        return False
        
    test_qr = valid_booking.qr_code
    print(f"Testing with QR: {test_qr}")
    
    try:
        # Test API endpoint
        url = 'http://127.0.0.1:8000/patients/api/booking/qr-scan/'
        headers = {
            'Content-Type': 'application/json',
        }
        data = {'qr_code': test_qr}
        
        response = requests.post(url, json=data, headers=headers)
        
        print(f"API Response Status: {response.status_code}")
        try:
            response_data = response.json()
            print(f"API Response Data: {json.dumps(response_data, indent=2)}")
            
            if response_data.get('success'):
                print("✅ QR API is working!")
                return True
            else:
                print(f"❌ QR API failed: {response_data.get('message')}")
                return False
                
        except Exception as e:
            print(f"❌ Invalid JSON response: {e}")
            print(f"Raw response: {response.text[:200]}...")
            return False
            
    except Exception as e:
        print(f"❌ API request failed: {e}")
        return False

def check_database_bookings():
    """Check available bookings in database"""
    print("\n📊 Checking Database Bookings")
    print("-" * 30)
    
    from patients.models import Queue
    from django.utils import timezone
    
    today = timezone.now().date()
    
    # Check today's bookings
    todays_bookings = Queue.objects.filter(booking_date=today)
    print(f"Today's bookings: {todays_bookings.count()}")
    
    # Check booked status bookings
    booked_bookings = Queue.objects.filter(status='booked')
    print(f"'Booked' status bookings: {booked_bookings.count()}")
    
    # Show available test bookings
    test_bookings = Queue.objects.filter(
        status='booked',
        booking_date=today
    ).order_by('-id')[:3]
    
    print("\nAvailable test bookings:")
    for booking in test_bookings:
        print(f"  ID: {booking.id}")
        print(f"  QR: {booking.qr_code}")
        print(f"  Patient: {booking.patient.name}")
        print(f"  Status: {booking.status}")
        print(f"  Date: {booking.booking_date}")
        print()
        
    return test_bookings.exists()

def create_debug_qr_page():
    """Create a debug QR scanner page"""
    print("\n🛠️ Creating Debug QR Scanner Page")
    print("-" * 30)
    
    debug_html = '''<!DOCTYPE html>
<html>
<head>
    <title>QR Scanner Debug</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .btn { padding: 10px 20px; margin: 5px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
        .btn:disabled { opacity: 0.5; }
        .success { color: green; }
        .error { color: red; }
        .debug { background: #f8f9fa; padding: 10px; margin: 10px 0; font-family: monospace; }
        #reader { width: 100%; max-width: 400px; border: 2px dashed #28a745; margin: 10px 0; }
    </style>
</head>
<body>
    <h1>QR Scanner Debug Page</h1>
    
    <div class="section">
        <h3>Library Status</h3>
        <div id="library-status">Checking...</div>
    </div>
    
    <div class="section">
        <h3>Camera Scanner</h3>
        <div id="reader"></div>
        <button id="start-camera" class="btn">Start Camera Scanner</button>
        <button id="stop-camera" class="btn" disabled>Stop Camera Scanner</button>
        <div id="camera-status"></div>
    </div>
    
    <div class="section">
        <h3>Manual Testing</h3>
        <input type="text" id="manual-qr" placeholder="Paste QR code here" style="width: 300px; padding: 8px;">
        <button id="test-manual" class="btn">Test Manual Entry</button>
        <div id="manual-result"></div>
    </div>
    
    <div class="section">
        <h3>Debug Log</h3>
        <div id="debug-log" class="debug"></div>
    </div>

    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <script>
        let scanner = null;
        
        function log(message) {
            const logDiv = document.getElementById('debug-log');
            const time = new Date().toLocaleTimeString();
            logDiv.innerHTML += `${time}: ${message}<br>`;
            console.log(message);
        }
        
        function setStatus(elementId, message, isError = false) {
            const element = document.getElementById(elementId);
            element.innerHTML = message;
            element.className = isError ? 'error' : 'success';
        }
        
        // Check library status
        document.addEventListener('DOMContentLoaded', function() {
            if (typeof Html5QrcodeScanner !== 'undefined') {
                setStatus('library-status', '✅ HTML5 QR Code library loaded');
                log('Library loaded successfully');
            } else {
                setStatus('library-status', '❌ HTML5 QR Code library failed to load', true);
                log('ERROR: Library not loaded');
            }
            
            // Check camera support
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                log('Browser supports camera access');
            } else {
                log('ERROR: Browser does not support camera access');
            }
        });
        
        // Start camera scanner
        document.getElementById('start-camera').addEventListener('click', function() {
            log('Starting camera scanner...');
            
            try {
                const config = {
                    fps: 10,
                    qrbox: { width: 250, height: 250 }
                };
                
                scanner = new Html5QrcodeScanner("reader", config, false);
                scanner.render(
                    function(decodedText, decodedResult) {
                        log(`QR Code detected: ${decodedText}`);
                        setStatus('camera-status', `✅ QR Detected: ${decodedText}`);
                        testQRCode(decodedText);
                    },
                    function(error) {
                        // Silent - too many scan attempts
                    }
                );
                
                document.getElementById('start-camera').disabled = true;
                document.getElementById('stop-camera').disabled = false;
                setStatus('camera-status', '📷 Camera started - point at QR code');
                log('Camera scanner started');
                
            } catch (error) {
                log(`ERROR starting camera: ${error.message}`);
                setStatus('camera-status', `❌ Error: ${error.message}`, true);
            }
        });
        
        // Stop camera scanner
        document.getElementById('stop-camera').addEventListener('click', function() {
            if (scanner) {
                scanner.clear().then(() => {
                    log('Camera scanner stopped');
                }).catch(err => {
                    log(`Error stopping scanner: ${err}`);
                });
                scanner = null;
            }
            
            document.getElementById('start-camera').disabled = false;
            document.getElementById('stop-camera').disabled = true;
            setStatus('camera-status', '📷 Camera stopped');
        });
        
        // Manual testing
        document.getElementById('test-manual').addEventListener('click', function() {
            const qrCode = document.getElementById('manual-qr').value.trim();
            if (!qrCode) {
                setStatus('manual-result', '❌ Please enter a QR code', true);
                return;
            }
            
            log(`Testing manual QR: ${qrCode}`);
            testQRCode(qrCode);
        });
        
        // Test QR code with API
        function testQRCode(qrCode) {
            log(`Sending API request for: ${qrCode}`);
            setStatus('manual-result', '⏳ Processing...');
            
            fetch('/patients/api/booking/qr-scan/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ qr_code: qrCode })
            })
            .then(response => {
                log(`API Response status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                log(`API Response: ${JSON.stringify(data)}`);
                
                if (data.success) {
                    setStatus('manual-result', `✅ Success! Token: ${data.token_number}, Patient: ${data.patient_name}`);
                } else {
                    setStatus('manual-result', `❌ Failed: ${data.message}`, true);
                }
            })
            .catch(error => {
                log(`API Error: ${error.message}`);
                setStatus('manual-result', `❌ Network Error: ${error.message}`, true);
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
    
    debug_file = os.path.join(project_dir, 'debug_qr_scanner.html')
    with open(debug_file, 'w', encoding='utf-8') as f:
        f.write(debug_html)
        
    print(f"✅ Debug page created: {debug_file}")
    print("Access at: http://127.0.0.1:8000/debug_qr_scanner.html")

def main():
    """Run all debug tests"""
    print("🔧 COMPREHENSIVE QR SCANNER DEBUG")
    print("=" * 50)
    
    # Test 1: Admin login
    admin_ok = test_admin_login()
    
    # Test 2: QR scanner page
    page_ok = test_qr_scanner_page()
    
    # Test 3: Database bookings
    db_ok = check_database_bookings()
    
    # Test 4: API endpoint
    api_ok = test_qr_api_directly()
    
    # Create debug page
    create_debug_qr_page()
    
    print("\n" + "=" * 50)
    print("🎯 SUMMARY")
    print("=" * 50)
    print(f"Admin Access: {'✅' if admin_ok else '❌'}")
    print(f"QR Page Load: {'✅' if page_ok else '❌'}")
    print(f"Database: {'✅' if db_ok else '❌'}")
    print(f"API Endpoint: {'✅' if api_ok else '❌'}")
    
    if all([admin_ok, page_ok, db_ok, api_ok]):
        print("\n🎉 All components working! Try the debug page:")
        print("http://127.0.0.1:8000/debug_qr_scanner.html")
    else:
        print("\n❌ Some components failing. Check errors above.")

if __name__ == "__main__":
    main()