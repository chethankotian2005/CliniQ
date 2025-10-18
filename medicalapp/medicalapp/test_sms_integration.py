"""
Test script for SMS functionality
Run this to test SMS notifications
"""

import os
import sys
import django

# Add the project directory to the Python path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

from patients.sms_service import SMSService
from patients.models import Patient, Department, Queue
from django.utils import timezone
from datetime import datetime

def test_sms_service():
    """Test the SMS service with a mock booking"""
    print("🔧 Testing SMS Service...")
    
    # Create SMS service instance
    sms_service = SMSService()
    
    # Create a test patient (or get existing one)
    test_patient, created = Patient.objects.get_or_create(
        phone_number='+918123936830',  # Your demo number
        defaults={
            'name': 'Test Patient',
            'email': 'test@example.com',
            'age': 30,
            'gender': 'M'
        }
    )
    
    print(f"📱 Test patient: {test_patient.name} ({test_patient.phone_number})")
    
    # Get or create a test department
    test_dept, created = Department.objects.get_or_create(
        name='Cardiology',
        defaults={
            'is_active': True,
            'description': 'Heart care department'
        }
    )
    
    # Create a test booking
    test_booking = Queue.objects.create(
        patient=test_patient,
        department=test_dept,
        status='booked',
        is_online_booking=True,
        booked_at=timezone.now(),
        booking_date=timezone.now().date(),
        booking_time_slot='morning',
        token_number=101,
        notes='Test booking for SMS validation'
    )
    
    print(f"🏥 Test booking created: #{test_booking.id}")
    
    # Test 1: Booking confirmation SMS
    print("\n1️⃣ Testing booking confirmation SMS...")
    result1 = sms_service.send_booking_confirmation_sms(test_booking)
    print(f"   Result: {'✅ Success' if result1['success'] else '❌ Failed'}")
    if result1['success']:
        print(f"   Message SID: {result1['message_sid']}")
    else:
        print(f"   Error: {result1['error']}")
    
    # Test 2: Arrival notification SMS
    print("\n2️⃣ Testing arrival notification SMS...")
    test_booking.status = 'waiting'
    test_booking.arrived_at = timezone.now()
    test_booking.save()
    
    result2 = sms_service.send_arrival_notification_sms(test_booking)
    print(f"   Result: {'✅ Success' if result2['success'] else '❌ Failed'}")
    if result2['success']:
        print(f"   Message SID: {result2['message_sid']}")
    else:
        print(f"   Error: {result2['error']}")
    
    # Test 3: Doctor call notification SMS
    print("\n3️⃣ Testing doctor call notification SMS...")
    result3 = sms_service.send_doctor_call_notification_sms(test_booking)
    print(f"   Result: {'✅ Success' if result3['success'] else '❌ Failed'}")
    if result3['success']:
        print(f"   Message SID: {result3['message_sid']}")
    else:
        print(f"   Error: {result3['error']}")
    
    # Test 4: Appointment reminder SMS
    print("\n4️⃣ Testing appointment reminder SMS...")
    result4 = sms_service.send_appointment_reminder_sms(test_booking)
    print(f"   Result: {'✅ Success' if result4['success'] else '❌ Failed'}")
    if result4['success']:
        print(f"   Message SID: {result4['message_sid']}")
    else:
        print(f"   Error: {result4['error']}")
    
    # Test 5: Cancellation SMS
    print("\n5️⃣ Testing cancellation SMS...")
    test_booking.status = 'cancelled'
    test_booking.save()
    
    result5 = sms_service.send_cancellation_sms(test_booking)
    print(f"   Result: {'✅ Success' if result5['success'] else '❌ Failed'}")
    if result5['success']:
        print(f"   Message SID: {result5['message_sid']}")
    else:
        print(f"   Error: {result5['error']}")
    
    # Clean up test data
    print(f"\n🧹 Cleaning up test booking #{test_booking.id}")
    test_booking.delete()
    
    print("\n🎉 SMS service testing completed!")
    print("📱 Check your phone for the SMS messages.")

if __name__ == "__main__":
    test_sms_service()