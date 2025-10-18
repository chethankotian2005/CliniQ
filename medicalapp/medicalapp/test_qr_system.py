#!/usr/bin/env python
"""
Test QR scanner functionality and check for issues
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
from patients.booking_service import BookingService
from django.utils import timezone
import json

def test_qr_scanner():
    """Test QR scanner functionality"""
    print("Testing QR Scanner Functionality")
    print("=" * 50)
    
    # Get a recent booking with QR code
    recent_bookings = Queue.objects.filter(
        patient__phone_number='+918123936830',
        status='booked',
        qr_code__isnull=False
    ).exclude(qr_code='').order_by('-booked_at')
    
    if not recent_bookings.exists():
        print("No bookings with QR codes found for testing")
        return
    
    booking = recent_bookings.first()
    print(f"Testing with Booking #{booking.id}")
    print(f"Patient: {booking.patient.name}")
    print(f"QR Code: {booking.qr_code}")
    print(f"Status: {booking.status}")
    print(f"Department: {booking.department.name}")
    print()
    
    # Test the QR activation process
    print("Testing QR activation...")
    booking_service = BookingService()
    
    try:
        result = booking_service.activate_booking_by_qr(booking.qr_code)
        
        print("QR Activation Result:")
        print(f"  Success: {result['success']}")
        if result['success']:
            print(f"  Patient Name: {result.get('patient_name', 'N/A')}")
            print(f"  Token Number: {result.get('token_number', 'N/A')}")
            print(f"  Department: {result.get('department', 'N/A')}")
            print(f"  Message: {result.get('message', 'N/A')}")
        else:
            print(f"  Error Message: {result.get('message', 'Unknown error')}")
            
        # Check booking status after activation
        booking.refresh_from_db()
        print(f"\nBooking status after activation: {booking.status}")
        print(f"Token number: {booking.token_number}")
        
    except Exception as e:
        print(f"Error during QR activation: {str(e)}")
        import traceback
        traceback.print_exc()

def check_qr_api():
    """Test the QR API endpoint directly"""
    print("\nTesting QR API Endpoint")
    print("=" * 30)
    
    # Get a test QR code
    booking = Queue.objects.filter(
        patient__phone_number='+918123936830',
        qr_code__isnull=False
    ).exclude(qr_code='').first()
    
    if not booking:
        print("No booking with QR code found for API testing")
        return
        
    print(f"Testing API with QR code: {booking.qr_code}")
    
    # Simulate the API call
    from patients.booking_views import QRScanView
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request_data = json.dumps({'qr_code': booking.qr_code})
    request = factory.post('/patients/api/booking/qr-scan/', 
                          data=request_data, 
                          content_type='application/json')
    
    view = QRScanView()
    try:
        response = view.post(request)
        response_data = json.loads(response.content.decode())
        
        print("API Response:")
        print(f"  Status Code: {response.status_code}")
        print(f"  Success: {response_data.get('success', False)}")
        print(f"  Message: {response_data.get('message', 'No message')}")
        
    except Exception as e:
        print(f"API Error: {str(e)}")

def check_camera_permissions():
    """Check browser requirements for camera access"""
    print("\nCamera Access Requirements")
    print("=" * 30)
    print("For QR scanner to work:")
    print("1. Browser must support camera access (Chrome, Firefox, Safari)")
    print("2. Page must be served over HTTPS or localhost")
    print("3. User must grant camera permissions when prompted")
    print("4. Camera must not be in use by other applications")
    print()
    print("Current server setup:")
    print("- Running on localhost: YES")
    print("- HTTPS: NO (but localhost works for camera access)")
    print()
    print("Troubleshooting steps:")
    print("1. Refresh the page and allow camera access")
    print("2. Check browser console for JavaScript errors")
    print("3. Try the manual entry option if camera fails")
    print("4. Ensure QR codes are clearly visible and well-lit")

if __name__ == "__main__":
    test_qr_scanner()
    check_qr_api()
    check_camera_permissions()