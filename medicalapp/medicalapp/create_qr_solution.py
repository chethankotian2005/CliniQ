#!/usr/bin/env python
"""
Create fresh QR codes and direct test
"""
import os
import sys
import django

# Set up Django environment
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

from patients.models import Queue, Patient, Department
from django.utils import timezone
import uuid

def create_multiple_test_qrs():
    """Create multiple test QR codes for testing"""
    print("🏗️ Creating Multiple Test QR Codes")
    print("=" * 50)
    
    try:
        # Get or create patient
        patient, _ = Patient.objects.get_or_create(
            phone_number='+918123936830',
            defaults={
                'name': 'Chethan V Kotian',
                'email': 'kotianchethan4@gmail.com',
                'age': 30,
                'gender': 'M'
            }
        )
        
        # Get department
        department = Department.objects.filter(is_active=True).first()
        if not department:
            print("❌ No active department found")
            return []
            
        qr_codes = []
        
        # Create 3 test bookings
        for i in range(3):
            booking = Queue.objects.create(
                patient=patient,
                department=department,
                status='booked',
                is_online_booking=True,
                booked_at=timezone.now(),
                booking_date=timezone.now().date(),
                booking_time_slot='afternoon',
                appointment_type='in_person',
                notes=f'Test booking #{i+1} for QR scanner testing',
                token_number=0
            )
            
            # Generate QR code
            qr_hash = uuid.uuid4().hex[:8]
            qr_code = f"CLINIQ:BOOKING:{booking.id}:{qr_hash}"
            booking.qr_code = qr_code
            booking.save()
            
            qr_codes.append({
                'id': booking.id,
                'qr_code': qr_code,
                'patient': booking.patient.name,
                'department': booking.department.name
            })
            
            print(f"✅ Created Booking #{booking.id}: {qr_code}")
            
        return qr_codes
        
    except Exception as e:
        print(f"❌ Error creating QR codes: {e}")
        return []

def test_qr_codes_directly(qr_codes):
    """Test QR codes directly without Django test client"""
    print(f"\n🧪 Testing {len(qr_codes)} QR Codes Directly")
    print("=" * 50)
    
    from patients.booking_service import BookingService
    booking_service = BookingService()
    
    working_qrs = []
    
    for qr_data in qr_codes:
        qr_code = qr_data['qr_code']
        print(f"\nTesting: {qr_code}")
        
        try:
            result = booking_service.activate_booking_by_qr(qr_code)
            
            if result['success']:
                print(f"  ✅ Success: Token {result.get('token_number')}")
                working_qrs.append(qr_code)
            else:
                print(f"  ❌ Failed: {result.get('message')}")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            
    return working_qrs

def create_final_test_page(qr_codes):
    """Create a comprehensive test page with working QR codes"""
    print(f"\n📄 Creating Final Test Page")
    print("=" * 30)
    
    # Get available QR codes for testing
    available_qrs = []
    from patients.models import Queue
    
    bookings = Queue.objects.filter(status='booked').order_by('-id')[:5]
    for booking in bookings:
        available_qrs.append({
            'id': booking.id,
            'qr_code': booking.qr_code,
            'patient': booking.patient.name,
            'department': booking.department.name,
            'status': booking.status
        })
    
    qr_options = ""
    for qr in available_qrs:
        qr_options += f'<option value="{qr["qr_code"]}">Booking #{qr["id"]} - {qr["patient"]} - {qr["department"]}</option>\n'
    
    html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>QR Scanner - Final Test</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f8f9fa; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ color: #007bff; margin: 0; }}
        .section {{ margin: 25px 0; padding: 20px; border: 1px solid #e9ecef; border-radius: 8px; background: #f8f9fa; }}
        .btn {{ padding: 12px 24px; background: #007bff; color: white; border: none; border-radius: 6px; cursor: pointer; margin: 8px 4px; font-size: 14px; }}
        .btn:hover {{ background: #0056b3; }}
        .btn-success {{ background: #28a745; }}
        .btn-success:hover {{ background: #1e7e34; }}
        .btn-danger {{ background: #dc3545; }}
        .btn-danger:hover {{ background: #c82333; }}
        .form-control {{ width: 100%; padding: 12px; border: 1px solid #ced4da; border-radius: 6px; margin: 8px 0; font-size: 14px; }}
        .alert {{ padding: 15px; margin: 15px 0; border-radius: 6px; }}
        .alert-success {{ background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }}
        .alert-danger {{ background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }}
        .alert-info {{ background: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }}
        .alert-warning {{ background: #fff3cd; color: #856404; border: 1px solid #ffeaa7; }}
        #reader {{ width: 100%; max-width: 400px; margin: 20px auto; border: 2px dashed #28a745; border-radius: 8px; }}
        .log {{ background: #f8f9fa; padding: 15px; border-radius: 6px; font-family: 'Courier New', monospace; font-size: 12px; max-height: 200px; overflow-y: auto; border: 1px solid #e9ecef; }}
        .qr-list {{ background: white; padding: 15px; border-radius: 6px; border: 1px solid #e9ecef; }}
        .qr-item {{ padding: 8px; margin: 4px 0; background: #f8f9fa; border-radius: 4px; font-family: monospace; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 QR Scanner - Final Test</h1>
            <p>Complete QR scanner testing tool with camera and manual entry</p>
        </div>
        
        <div class="alert alert-warning">
            <strong>⚠️ Important:</strong> Make sure you're logged into the admin panel first!<br>
            <a href="/adminpanel/login/" target="_blank">Login to Admin Panel</a>
        </div>

        <div class="section">
            <h3>📱 Available Test QR Codes</h3>
            <div class="qr-list">
                {qr_options if qr_options else '<p class="alert-warning">No QR codes available</p>'}
            </div>
        </div>

        <div class="section">
            <h3>📷 Camera QR Scanner</h3>
            <div id="reader"></div>
            <div style="text-align: center; margin: 20px 0;">
                <button id="start-camera" class="btn btn-success">📷 Start Camera Scanner</button>
                <button id="stop-camera" class="btn btn-danger" disabled>⏹️ Stop Camera</button>
            </div>
            <div id="camera-result"></div>
        </div>

        <div class="section">
            <h3>⌨️ Manual QR Code Testing</h3>
            <label for="qr-select">Select Test QR Code:</label>
            <select id="qr-select" class="form-control">
                <option value="">-- Select a QR code --</option>
                {qr_options}
            </select>
            
            <label for="manual-qr">Or Enter QR Code Manually:</label>
            <input type="text" id="manual-qr" class="form-control" placeholder="CLINIQ:BOOKING:ID:HASH">
            
            <button id="test-qr" class="btn">🧪 Test QR Code</button>
            <div id="manual-result"></div>
        </div>

        <div class="section">
            <h3>📋 Debug Log</h3>
            <div id="debug-log" class="log">Ready for testing...<br></div>
            <button onclick="clearLog()" class="btn" style="background: #6c757d;">🗑️ Clear Log</button>
        </div>
    </div>

    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <script>
        let scanner = null;
        
        function log(message) {{
            const logDiv = document.getElementById('debug-log');
            const time = new Date().toLocaleTimeString();
            logDiv.innerHTML += `[${{time}}] ${{message}}<br>`;
            logDiv.scrollTop = logDiv.scrollHeight;
            console.log(message);
        }}
        
        function clearLog() {{
            document.getElementById('debug-log').innerHTML = 'Log cleared...<br>';
        }}
        
        function showResult(elementId, message, type = 'info') {{
            const element = document.getElementById(elementId);
            element.innerHTML = `<div class="alert alert-${{type}}">${{message}}</div>`;
        }}
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {{
            log('🚀 QR Scanner Test Page Loaded');
            
            if (typeof Html5QrcodeScanner !== 'undefined') {{
                log('✅ HTML5 QR Code library loaded successfully');
            }} else {{
                log('❌ HTML5 QR Code library failed to load');
            }}
            
            // Auto-select first QR code
            const select = document.getElementById('qr-select');
            if (select.options.length > 1) {{
                select.selectedIndex = 1;
                document.getElementById('manual-qr').value = select.value;
            }}
        }});
        
        // QR selection change
        document.getElementById('qr-select').addEventListener('change', function() {{
            document.getElementById('manual-qr').value = this.value;
        }});
        
        // Start camera
        document.getElementById('start-camera').addEventListener('click', function() {{
            log('📷 Starting camera scanner...');
            
            try {{
                scanner = new Html5QrcodeScanner("reader", {{
                    fps: 10,
                    qrbox: {{ width: 250, height: 250 }},
                    aspectRatio: 1.0
                }}, false);
                
                scanner.render(
                    function(decodedText) {{
                        log(`🎯 QR Code detected: ${{decodedText}}`);
                        showResult('camera-result', `QR Code detected: ${{decodedText}}`, 'success');
                        testQRCode(decodedText);
                    }},
                    function(error) {{
                        // Silent for continuous scanning
                    }}
                );
                
                document.getElementById('start-camera').disabled = true;
                document.getElementById('stop-camera').disabled = false;
                log('✅ Camera scanner started - point camera at QR code');
                showResult('camera-result', '📷 Camera active - point at QR code', 'info');
                
            }} catch (error) {{
                log(`❌ Camera error: ${{error.message}}`);
                showResult('camera-result', `Camera Error: ${{error.message}}`, 'danger');
            }}
        }});
        
        // Stop camera
        document.getElementById('stop-camera').addEventListener('click', function() {{
            if (scanner) {{
                scanner.clear().then(() => {{
                    log('🛑 Camera scanner stopped');
                }}).catch(err => {{
                    log(`⚠️ Error stopping scanner: ${{err}}`);
                }});
                scanner = null;
            }}
            
            document.getElementById('start-camera').disabled = false;
            document.getElementById('stop-camera').disabled = true;
            showResult('camera-result', 'Camera stopped', 'info');
        }});
        
        // Manual test
        document.getElementById('test-qr').addEventListener('click', function() {{
            const qrCode = document.getElementById('manual-qr').value.trim();
            if (!qrCode) {{
                showResult('manual-result', '⚠️ Please enter or select a QR code', 'warning');
                return;
            }}
            
            log(`🧪 Testing QR code manually: ${{qrCode}}`);
            testQRCode(qrCode);
        }});
        
        // Test QR code function
        function testQRCode(qrCode) {{
            log(`📡 Sending API request for: ${{qrCode}}`);
            showResult('manual-result', '⏳ Processing QR code...', 'info');
            
            fetch('/patients/api/booking/qr-scan/', {{
                method: 'POST',
                headers: {{
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                }},
                body: JSON.stringify({{ qr_code: qrCode }})
            }})
            .then(response => {{
                log(`📨 API response status: ${{response.status}}`);
                
                if (!response.ok) {{
                    if (response.status === 403) {{
                        throw new Error('Authentication required - please login to admin panel');
                    }}
                    throw new Error(`HTTP ${{response.status}}`);
                }}
                return response.json();
            }})
            .then(data => {{
                log(`📄 API response: ${{JSON.stringify(data)}}`);
                
                if (data.success) {{
                    const message = `
                        <strong>🎉 QR Code Processed Successfully!</strong><br>
                        <strong>Patient:</strong> ${{data.patient_name}}<br>
                        <strong>Token Number:</strong> ${{data.token_number}}<br>
                        <strong>Department:</strong> ${{data.department}}<br>
                        <strong>Status:</strong> ${{data.status}}<br>
                        <strong>Message:</strong> ${{data.message}}
                    `;
                    showResult('manual-result', message, 'success');
                    log(`✅ SUCCESS: Token ${{data.token_number}} assigned to ${{data.patient_name}}`);
                }} else {{
                    showResult('manual-result', `❌ Error: ${{data.message}}`, 'danger');
                    log(`❌ API Error: ${{data.message}}`);
                }}
            }})
            .catch(error => {{
                log(`💥 Network/API error: ${{error.message}}`);
                
                if (error.message.includes('Authentication')) {{
                    showResult('manual-result', 
                        `🔐 Authentication Error: Please <a href="/adminpanel/login/" target="_blank">login to admin panel</a> first`, 
                        'warning');
                }} else {{
                    showResult('manual-result', `❌ Network Error: ${{error.message}}`, 'danger');
                }}
            }});
        }}
        
        // Get CSRF token
        function getCookie(name) {{
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {{
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {{
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {{
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }}
                }}
            }}
            return cookieValue;
        }}
    </script>
</body>
</html>'''
    
    # Save to static directory
    static_dir = os.path.join(project_dir, 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    test_file = os.path.join(static_dir, 'qr_final_test.html')
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"✅ Final test page created")
    print(f"📁 File: {test_file}")
    print(f"🌐 URL: http://127.0.0.1:8000/static/qr_final_test.html")
    
    return test_file

def main():
    """Create comprehensive QR test solution"""
    print("🔧 CREATING COMPREHENSIVE QR TEST SOLUTION")
    print("=" * 60)
    
    # Create test QR codes
    qr_codes = create_multiple_test_qrs()
    
    # Test QR codes directly
    if qr_codes:
        working_qrs = test_qr_codes_directly(qr_codes)
        print(f"\n✅ Working QR codes: {len(working_qrs)}")
    else:
        working_qrs = []
    
    # Create final test page
    test_file = create_final_test_page(qr_codes)
    
    print("\n" + "=" * 60)
    print("🎯 QR SCANNER SOLUTION READY")
    print("=" * 60)
    print("\n📋 TESTING INSTRUCTIONS:")
    print("1. 🔐 Login to admin panel: http://127.0.0.1:8000/adminpanel/login/")
    print("   Username: admin")
    print("   Password: admin123")
    print()
    print("2. 🧪 Open test page: http://127.0.0.1:8000/static/qr_final_test.html")
    print()
    print("3. 📱 For Manual Testing:")
    print("   - Select a QR code from dropdown")
    print("   - Click 'Test QR Code'")
    print("   - Should show success with token assignment")
    print()
    print("4. 📷 For Camera Testing:")
    print("   - Click 'Start Camera Scanner'")
    print("   - Allow camera permissions")
    print("   - Point camera at QR code (generate from online QR generator)")
    print()
    print("🔗 Alternative URLs:")
    print("- Admin QR Scanner: http://127.0.0.1:8000/adminpanel/qr-scanner/")
    print("- Simple Test: http://127.0.0.1:8000/static/qr_test.html")
    
    if qr_codes:
        print(f"\n📱 Available QR Codes for Testing:")
        for qr in qr_codes:
            print(f"  • {qr['qr_code']}")

if __name__ == "__main__":
    main()