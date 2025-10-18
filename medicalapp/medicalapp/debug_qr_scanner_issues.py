#!/usr/bin/env python
"""
QR Scanner Diagnostic Tool
Test QR scanning functionality and debug issues
"""

import os
import sys
import django
import json
import requests
from datetime import datetime

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

from patients.models import Queue, Department, Patient
from patients.booking_service import BookingService

def test_qr_scanner_functionality():
    """Test QR scanner backend functionality"""
    
    print("🔍 QR Scanner Diagnostic Test")
    print("=" * 50)
    
    # Check if server is running
    server_url = "http://127.0.0.1:8000"
    try:
        response = requests.get(server_url, timeout=5)
        print(f"✅ Server is running at {server_url}")
    except Exception as e:
        print(f"❌ Server is not accessible: {e}")
        return
    
    # Check if we have any bookings with QR codes
    bookings_with_qr = Queue.objects.filter(qr_code__isnull=False, status='booked')
    print(f"📊 Bookings with QR codes: {bookings_with_qr.count()}")
    
    if bookings_with_qr.exists():
        booking = bookings_with_qr.first()
        print(f"📋 Test booking found:")
        print(f"   - ID: {booking.id}")
        print(f"   - Patient: {booking.patient.name}")
        print(f"   - QR Code: {booking.qr_code}")
        print(f"   - Status: {booking.status}")
        
        # Test QR activation
        print("\n🔧 Testing QR activation...")
        booking_service = BookingService()
        result = booking_service.activate_booking_by_qr(booking.qr_code)
        
        print(f"🔍 QR Activation Result:")
        print(json.dumps(result, indent=2))
        
        # Test API endpoint
        print("\n🌐 Testing API endpoint...")
        qr_scan_url = f"{server_url}/patients/api/booking/qr-scan/"
        
        # Get CSRF token first
        csrf_url = f"{server_url}/adminpanel/login/"
        session = requests.Session()
        csrf_response = session.get(csrf_url)
        
        if 'csrftoken' in session.cookies:
            csrf_token = session.cookies['csrftoken']
            print(f"✅ CSRF token obtained")
            
            # Test API call
            try:
                api_data = {'qr_code': booking.qr_code}
                headers = {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf_token,
                    'Referer': server_url
                }
                
                api_response = session.post(qr_scan_url, 
                                          json=api_data, 
                                          headers=headers)
                
                print(f"📡 API Response Status: {api_response.status_code}")
                try:
                    api_result = api_response.json()
                    print(f"📡 API Response Data:")
                    print(json.dumps(api_result, indent=2))
                except:
                    print(f"📡 API Response Text: {api_response.text}")
                    
            except Exception as e:
                print(f"❌ API call failed: {e}")
        else:
            print(f"❌ Could not obtain CSRF token")
    
    else:
        print("❌ No bookings with QR codes found for testing")
        print("💡 Run create_test_booking.py first to create a test booking")
    
    # Check QR scanner template
    print("\n📄 QR Scanner Template Check...")
    template_path = "templates/adminpanel/qr_scanner.html"
    if os.path.exists(template_path):
        print("✅ QR scanner template exists")
    else:
        print("❌ QR scanner template not found")
    
    # Check JavaScript dependencies
    print("\n📦 JavaScript Dependencies Check...")
    print("🔗 html5-qrcode library: https://unpkg.com/html5-qrcode")
    print("💡 Make sure this library can load in the browser")
    
    print("\n🛠️ Common Issues and Fixes:")
    print("1. Camera permissions: Browser must allow camera access")
    print("2. HTTPS/localhost: Camera only works on HTTPS or localhost")
    print("3. CSRF token: Make sure CSRF token is included in API calls")
    print("4. QR format: Should be CLINIQ:BOOKING:ID:HASH")
    print("5. Scanner paused: Click 'Start Scanner' button first")
    
if __name__ == "__main__":
    test_qr_scanner_functionality()