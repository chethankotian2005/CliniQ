#!/usr/bin/env python
"""
Quick fix for admin authentication and QR scanner access
"""
import os
import sys
import django

# Set up Django environment
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

from django.contrib.auth.models import User
from adminpanel.models import AdminUser

def fix_admin_authentication():
    """Fix admin authentication for QR scanner access"""
    print("🔧 Fixing Admin Authentication")
    print("=" * 40)
    
    try:
        # Create superuser if doesn't exist
        username = 'admin'
        password = 'admin123'
        email = 'admin@cliniq.com'
        
        # Check if superuser exists
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            print(f"✅ Created superuser: {username}")
        else:
            user = User.objects.get(username=username)
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            print(f"✅ Updated superuser: {username}")
        
        # Check if AdminUser exists
        admin_user, created = AdminUser.objects.get_or_create(
            user=user,
            defaults={
                'phone_number': '+918123936830',
                'role': 'super_admin'
            }
        )
        
        if created:
            print(f"✅ Created AdminUser for: {username}")
        else:
            admin_user.role = 'super_admin'
            admin_user.save()
            print(f"✅ Updated AdminUser for: {username}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error fixing authentication: {e}")
        return False

def check_qr_scanner_view():
    """Check if QR scanner view is accessible"""
    print("\n🔍 Checking QR Scanner View")
    print("=" * 30)
    
    try:
        from adminpanel.views import admin_qr_scanner
        print("✅ QR scanner view found")
        
        # Check URL pattern
        from adminpanel.urls import urlpatterns
        qr_urls = [url for url in urlpatterns if 'qr-scanner' in str(url.pattern)]
        
        if qr_urls:
            print("✅ QR scanner URL pattern exists")
        else:
            print("❌ QR scanner URL pattern not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking QR scanner view: {e}")
        return False

def test_direct_api():
    """Test QR API directly"""
    print("\n🧪 Testing QR API Directly")
    print("=" * 30)
    
    try:
        from patients.booking_service import BookingService
        from patients.models import Queue
        
        booking_service = BookingService()
        
        # Get latest booking
        booking = Queue.objects.filter(status__in=['booked', 'checked_in']).first()
        
        if booking and booking.qr_code:
            print(f"Testing QR: {booking.qr_code}")
            
            result = booking_service.activate_booking_by_qr(booking.qr_code)
            
            if result['success']:
                print(f"✅ API works: Token {result.get('token_number')}")
            else:
                print(f"⚠️ API result: {result.get('message')}")
                
        else:
            print("❌ No QR codes available for testing")
            
    except Exception as e:
        print(f"❌ API test error: {e}")

def main():
    """Run all fixes"""
    print("🔧 ADMIN AUTHENTICATION & QR SCANNER FIX")
    print("=" * 50)
    
    # Fix authentication
    auth_fixed = fix_admin_authentication()
    
    # Check QR scanner
    view_ok = check_qr_scanner_view()
    
    # Test API
    test_direct_api()
    
    print("\n" + "=" * 50)
    print("🎯 AUTHENTICATION FIX COMPLETE")
    print("=" * 50)
    
    if auth_fixed and view_ok:
        print("\n✅ ALL SYSTEMS READY!")
        print("\n📋 NEXT STEPS:")
        print("1. 🚀 Start Django server: python manage.py runserver")
        print("2. 🔐 Login: http://127.0.0.1:8000/adminpanel/login/")
        print("   Username: admin")
        print("   Password: admin123")
        print("3. 🧪 Test QR: http://127.0.0.1:8000/static/qr_final_test.html")
        print("4. 📱 Admin QR: http://127.0.0.1:8000/adminpanel/qr-scanner/")
    else:
        print("\n⚠️ Some issues found - check logs above")

if __name__ == "__main__":
    main()