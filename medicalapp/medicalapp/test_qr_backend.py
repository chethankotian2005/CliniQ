#!/usr/bin/env python
"""
Create a simple QR test view
"""
import os
import sys
import django

# Set up Django environment
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

def qr_test_view(request):
    """Serve the QR test page"""
    test_html_path = os.path.join(os.path.dirname(__file__), 'qr_test_page.html')
    
    try:
        with open(test_html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HttpResponse(html_content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse("QR test page not found", status=404)

# Test the actual QR scanning manually
def test_qr_manual():
    """Test QR scanning functionality manually"""
    print("Testing QR Scanner Backend")
    print("=" * 30)
    
    from patients.booking_views import QRScanView
    from django.test import RequestFactory
    import json
    
    # Test with the QR code we created
    test_qr = "CLINIQ:BOOKING:a4848d3b:test"
    
    factory = RequestFactory()
    request_data = json.dumps({'qr_code': test_qr})
    request = factory.post('/patients/api/booking/qr-scan/', 
                          data=request_data, 
                          content_type='application/json')
    
    view = QRScanView()
    
    try:
        response = view.post(request)
        response_data = json.loads(response.content.decode())
        
        print(f"QR Code: {test_qr}")
        print(f"Response Status: {response.status_code}")
        print(f"Response Data: {json.dumps(response_data, indent=2)}")
        
        if response_data.get('success'):
            print("✅ QR scanning backend is working!")
        else:
            print(f"❌ QR scanning failed: {response_data.get('message')}")
            
    except Exception as e:
        print(f"❌ Error testing QR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qr_manual()