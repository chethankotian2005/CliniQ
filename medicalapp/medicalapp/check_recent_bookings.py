#!/usr/bin/env python
"""
Check recent bookings for SMS troubleshooting
"""
import os
import sys
import django

# Set up Django environment
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

from patients.models import Queue, Patient
from patients.sms_service import SMSService
from django.utils import timezone
from datetime import datetime, timedelta

def check_recent_bookings():
    """Check recent bookings and test SMS manually"""
    print("Checking Recent Bookings and SMS Status")
    print("=" * 50)

    # Get recent bookings (last 24 hours)
    recent_time = timezone.now() - timedelta(hours=24)
    recent_bookings = Queue.objects.filter(
        booked_at__gte=recent_time,
        patient__phone_number='+918123936830'
    ).order_by('-booked_at')

    print(f"Found {recent_bookings.count()} recent bookings for +918123936830:")
    
    for booking in recent_bookings:
        print(f"\nBooking #{booking.id}:")
        print(f"   Patient: {booking.patient.name}")
        print(f"   Phone: {booking.patient.phone_number}")
        print(f"   Department: {booking.department.name}")
        print(f"   Status: {booking.status}")
        print(f"   Booked At: {booking.booked_at}")
        print(f"   Booking Date: {booking.booking_date}")
        print(f"   Time Slot: {booking.booking_time_slot}")
        print(f"   Online Booking: {booking.is_online_booking}")

    # Check if any patients exist with this number
    patients = Patient.objects.filter(phone_number='+918123936830')
    print(f"\nFound {patients.count()} patients with phone +918123936830:")
    for patient in patients:
        print(f"   ID: {patient.id}, Name: {patient.name}, Email: {patient.email}")

    # Test SMS for the most recent booking
    if recent_bookings.exists():
        latest_booking = recent_bookings.first()
        print(f"\nTesting SMS for latest booking #{latest_booking.id}...")
        
        try:
            sms_service = SMSService()
            result = sms_service.send_booking_confirmation_sms(latest_booking)
            
            print(f"SMS Test Result:")
            print(f"   Success: {result['success']}")
            if result['success']:
                print(f"   Message SID: {result['message_sid']}")
                print(f"   To: {result['to']}")
                print(f"   Status: {result.get('status', 'Unknown')}")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"   SMS Test Failed: {str(e)}")
    else:
        print("\nNo recent bookings found. Creating a test booking...")
        
        # Create test booking if none exists
        try:
            from patients.models import Department
            
            # Get or create test patient
            patient, created = Patient.objects.get_or_create(
                phone_number='+918123936830',
                defaults={
                    'name': 'Test Patient',
                    'email': 'test@example.com',
                    'age': 30,
                    'gender': 'M'
                }
            )
            
            # Get first available department
            department = Department.objects.filter(is_active=True).first()
            if not department:
                print("No active departments found!")
                return
            
            # Create test booking
            test_booking = Queue.objects.create(
                patient=patient,
                department=department,
                status='booked',
                is_online_booking=True,
                booked_at=timezone.now(),
                booking_date=timezone.now().date(),
                booking_time_slot='morning',
                notes='Manual test booking for SMS validation'
            )
            
            print(f"Created test booking #{test_booking.id}")
            
            # Test SMS
            sms_service = SMSService()
            result = sms_service.send_booking_confirmation_sms(test_booking)
            
            print(f"SMS Test Result:")
            print(f"   Success: {result['success']}")
            if result['success']:
                print(f"   Message SID: {result['message_sid']}")
                print(f"   Status: {result.get('status', 'Unknown')}")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            print(f"Failed to create test booking: {str(e)}")

if __name__ == "__main__":
    check_recent_bookings()