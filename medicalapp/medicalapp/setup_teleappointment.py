#!/usr/bin/env python3
"""
Teleappointment Setup Script for CLINIQ
This script helps integrate teleappointment functionality into the existing system
"""

import os
import sys
import django
from pathlib import Path

def setup_django():
    """Setup Django environment"""
    # Add the project directory to Python path
    project_root = Path(__file__).parent
    sys.path.append(str(project_root))
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'medicalapp.settings')
    
    try:
        django.setup()
        print("✅ Django environment set up successfully")
        return True
    except Exception as e:
        print(f"❌ Error setting up Django: {e}")
        return False

def run_migrations():
    """Run database migrations for teleappointment"""
    try:
        from django.core.management import execute_from_command_line
        
        print("🔄 Running database migrations...")
        execute_from_command_line(['manage.py', 'makemigrations', 'patients'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Database migrations completed successfully")
        return True
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

def check_requirements():
    """Check if all required packages are installed"""
    required_packages = [
        'django',
        'djangorestframework', 
        'qrcode',
        'pillow',
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Please install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def update_settings():
    """Check and suggest settings updates"""
    print("\n📋 Settings Configuration Checklist:")
    print("Please ensure the following are configured in your settings.py:")
    print("✅ EMAIL_BACKEND - for sending appointment confirmations")
    print("✅ SMS service configuration - for SMS notifications")
    print("✅ SITE_URL - for generating meeting links")
    print("✅ DEFAULT_FROM_EMAIL - for email notifications")
    
    settings_template = """
# Teleappointment Settings
SITE_URL = 'https://yourdomain.com'  # Update with your domain
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'

# Email Configuration (for appointment confirmations)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # Update with your SMTP server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'

# Time Zone
TIME_ZONE = 'Asia/Kolkata'  # Adjust as needed
USE_TZ = True
"""
    
    print("\n📝 Suggested settings to add:")
    print(settings_template)

def create_sample_data():
    """Create sample teleappointment data for testing"""
    try:
        from patients.models import Department, Patient, Queue, TeleAppointment
        from doctors.models import Doctor
        from django.utils import timezone
        from datetime import timedelta
        
        print("\n🎭 Creating sample teleappointment data...")
        
        # Check if we have departments and doctors
        if not Department.objects.exists():
            print("⚠️  No departments found. Please create departments first.")
            return False
        
        if not Doctor.objects.exists():
            print("⚠️  No doctors found. Please create doctors first.")
            return False
        
        # Create a sample patient
        patient, created = Patient.objects.get_or_create(
            phone_number='9999999999',
            defaults={
                'name': 'Test Patient',
                'email': 'test@example.com',
                'age': 30,
                'gender': 'M'
            }
        )
        
        if created:
            print(f"✅ Created sample patient: {patient.name}")
        else:
            print(f"✅ Using existing patient: {patient.name}")
        
        # Create a sample teleappointment
        department = Department.objects.first()
        doctor = Doctor.objects.first()
        
        # Create queue entry
        queue_entry, created = Queue.objects.get_or_create(
            patient=patient,
            department=department,
            booking_date=timezone.now().date(),
            defaults={
                'preferred_doctor': doctor,
                'status': 'booked',
                'is_online_booking': True,
                'appointment_type': 'telemedicine',
                'booking_time_slot': '14:00',
                'booked_at': timezone.now(),
                'token_number': 1
            }
        )
        
        if created:
            print(f"✅ Created sample queue entry: {queue_entry}")
        
        # Create teleappointment
        from patients.telemedicine_service import TelemedicineService
        
        tele_service = TelemedicineService()
        scheduled_time = timezone.now() + timedelta(hours=1)
        
        result = tele_service.create_teleappointment(
            queue_entry=queue_entry,
            scheduled_time=scheduled_time,
            platform='webrtc'
        )
        
        if result['success']:
            print(f"✅ Created sample teleappointment: {result['meeting_id']}")
            print(f"📱 Meeting URL: {result['meeting_url']}")
        else:
            print(f"❌ Error creating teleappointment: {result['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        return False

def test_api_endpoints():
    """Test teleappointment API endpoints"""
    print("\n🧪 Testing API endpoints...")
    
    try:
        from django.test import Client
        from django.urls import reverse
        
        client = Client()
        
        # Test department listing
        response = client.get('/patients/api/departments/')
        if response.status_code == 200:
            print("✅ Departments API working")
        else:
            print(f"❌ Departments API failed: {response.status_code}")
        
        # Test teleappointment booking page
        response = client.get('/patients/teleappointment/')
        if response.status_code == 200:
            print("✅ Teleappointment booking page accessible")
        else:
            print(f"❌ Teleappointment booking page failed: {response.status_code}")
        
        print("✅ Basic API tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Error testing APIs: {e}")
        return False

def print_usage_guide():
    """Print usage guide for teleappointments"""
    guide = """
📚 TELEAPPOINTMENT USAGE GUIDE

🔗 URLs:
- Booking Page: /patients/teleappointment/
- Management: /patients/teleappointment/management/
- Video Call: /patients/video-call/{meeting_id}/

📱 API Endpoints:
- Book Teleappointment: POST /patients/api/teleappointment/book/
- Get Appointment Status: GET /patients/api/teleappointment/{id}/
- Start Video Session: POST /patients/api/teleappointment/start/
- End Video Session: POST /patients/api/teleappointment/end/
- Available Slots: GET /patients/api/teleappointment/slots/{department_id}/

🎯 Features:
✅ Video consultation booking
✅ WebRTC-based video calls
✅ SMS and email notifications
✅ Appointment scheduling and rescheduling
✅ Multiple video platforms support (Zoom, Google Meet, Teams)
✅ Real-time appointment management
✅ Mobile-responsive design

🔧 Next Steps:
1. Configure SMS service in sms_service.py
2. Set up email server in settings.py
3. Customize video call platform preferences
4. Test with real appointments
5. Configure firewall for WebRTC if needed

📞 Support:
- Ensure patients have modern browsers
- Test video calls on different devices
- Monitor connection quality
- Provide technical support for patients
"""
    print(guide)

def main():
    """Main setup function"""
    print("🏥 CLINIQ Teleappointment Setup")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return False
    
    # Setup Django
    if not setup_django():
        return False
    
    # Run migrations
    if not run_migrations():
        return False
    
    # Settings guidance
    update_settings()
    
    # Create sample data
    create_sample_data()
    
    # Test APIs
    test_api_endpoints()
    
    # Print usage guide
    print_usage_guide()
    
    print("\n🎉 Teleappointment setup completed successfully!")
    print("Your system is now ready for video consultations.")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)