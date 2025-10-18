#!/usr/bin/env python
"""
Create a test QR code for today's date to test scanner
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

def create_test_booking_for_today():
    """Create a test booking for today to test QR scanner"""
    print("Creating Test Booking for Today")
    print("=" * 40)
    
    try:
        # Get or create test patient
        patient, created = Patient.objects.get_or_create(
            phone_number='+918123936830',
            defaults={
                'name': 'Chethan V Kotian',
                'email': 'kotianchethan4@gmail.com',
                'age': 30,
                'gender': 'M'
            }
        )
        
        # Get first available department
        department = Department.objects.filter(is_active=True).first()
        if not department:
            print("No active departments found!")
            return None
            
        # Create booking for today
        booking_service = BookingService()
        
        patient_data = {
            'name': patient.name,
            'phone_number': patient.phone_number,
            'email': patient.email,
            'age': patient.age,
            'gender': patient.gender,
            'priority': 'normal',
            'notes': 'Test booking for QR scanner testing'
        }
        
        today = timezone.now().date()
        
        result = booking_service.create_online_booking(
            patient_data=patient_data,
            department_id=department.id,
            booking_date=today,
            time_slot='afternoon',
            appointment_type='in_person'
        )
        
        if result['success']:
            booking_id = result['booking_id']
            qr_code = result['qr_code']
            
            print(f"Test booking created successfully!")
            print(f"Booking ID: {booking_id}")
            print(f"QR Code: {qr_code}")
            print(f"Patient: {result['patient_name']}")
            print(f"Department: {result['department']}")
            print(f"Date: {result['booking_date']}")
            print(f"Time Slot: {result.get('time_slot', 'N/A')}")
            print()
            print("Use this QR code to test the scanner:")
            print(f"QR CODE: {qr_code}")
            print()
            print("Manual testing steps:")
            print("1. Go to admin panel QR scanner")
            print("2. Click 'Manual Entry'")
            print(f"3. Paste this QR code: {qr_code}")
            print("4. Click 'Process QR Code'")
            
            return qr_code
            
        else:
            print(f"Failed to create booking: {result.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"Error creating test booking: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    create_test_booking_for_today()