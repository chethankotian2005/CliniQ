#!/usr/bin/env python
"""
Create a test booking for TODAY to test QR scanner
"""

import os
import sys
import django
from datetime import datetime, date

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

from patients.models import Department, Patient
from patients.booking_service import BookingService

def create_today_booking():
    """Create a test booking for today"""
    
    print("📅 Creating Test Booking for TODAY")
    print("=" * 40)
    
    # Use existing patient or create new one
    patient, created = Patient.objects.get_or_create(
        phone_number='+918123936830',
        defaults={
            'name': 'Chethan V Kotian',
            'age': 30,
            'gender': 'male',
            'emergency_contact': '+918123936830'
        }
    )
    
    if created:
        print(f"📝 Created new patient: {patient.name}")
    else:
        print(f"👤 Using existing patient: {patient.name}")
    
    # Get department
    try:
        department = Department.objects.first()
        if not department:
            # Create a department if none exists
            department = Department.objects.create(
                name="General Medicine",
                description="General medical consultations"
            )
            print(f"🏥 Created department: {department.name}")
        else:
            print(f"🏥 Using department: {department.name}")
    except Exception as e:
        print(f"❌ Error with department: {e}")
        return
    
    # Create booking for TODAY
    today = date.today()
    print(f"📅 Booking date: {today}")
    
    booking_service = BookingService()
    
    patient_data = {
        'name': patient.name,
        'phone_number': patient.phone_number,
        'age': patient.age,
        'gender': patient.gender,
        'priority': 'normal'
    }
    
    try:
        result = booking_service.create_online_booking(
            patient_data=patient_data,
            department_id=department.id,
            booking_date=today,  # TODAY!
            time_slot='afternoon'
        )
        
        if result['success']:
            print(f"✅ Test booking created successfully!")
            print(f"📋 Booking ID: {result['booking_id']}")
            print(f"🔗 QR Code: {result['qr_code']}")
            print(f"👤 Patient: {patient.name}")
            print(f"🏥 Department: {department.name}")
            print(f"📅 Date: {today}")
            print(f"⏰ Time Slot: afternoon")
            print()
            print(f"🎯 Use this QR code to test the scanner:")
            print(f"📱 QR CODE: {result['qr_code']}")
            print()
            print("📝 Manual testing steps:")
            print("1. Go to admin panel QR scanner")
            print("2. Click 'Manual Entry'")
            print(f"3. Paste this QR code: {result['qr_code']}")
            print("4. Click 'Process QR Code'")
        else:
            print(f"❌ Booking failed: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error creating booking: {e}")

if __name__ == "__main__":
    create_today_booking()