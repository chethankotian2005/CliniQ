#!/usr/bin/env python
"""
Create a test booking with a new patient for TODAY
"""

import os
import sys
import django
from datetime import datetime, date

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

from patients.models import Department, Patient
from patients.booking_service import BookingService

def create_new_patient_booking():
    """Create a test booking for today with new patient"""
    
    print("Creating Test Booking for TODAY with New Patient")
    print("=" * 50)
    
    # Create new patient with unique phone number
    patient, created = Patient.objects.get_or_create(
        phone_number='+918123936999',  # Different number
        defaults={
            'name': 'Test Scanner User',
            'age': 35,
            'gender': 'male',
            'emergency_contact': '+918123936999'
        }
    )
    
    if created:
        print(f"Created new patient: {patient.name}")
    else:
        print(f"Using existing patient: {patient.name}")
    
    # Get department
    department = Department.objects.first()
    print(f"Using department: {department.name}")
    
    # Create booking for TODAY
    today = date.today()
    print(f"Booking date: {today}")
    
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
            booking_date=today,
            time_slot='evening'
        )
        
        if result['success']:
            print(f"✅ Test booking created successfully!")
            print(f"Booking ID: {result['booking_id']}")
            print(f"QR Code: {result['qr_code']}")
            print(f"Patient: {patient.name}")
            print(f"Department: {department.name}")
            print(f"Date: {today}")
            print(f"Time Slot: evening")
            print()
            print(f"🎯 TEST THIS QR CODE:")
            print(f"📱 {result['qr_code']}")
            print()
            print("📝 Manual testing steps:")
            print("1. Go to: http://127.0.0.1:8000/adminpanel/qr-scanner/")
            print("2. Click 'Manual Entry' button")
            print(f"3. Paste: {result['qr_code']}")
            print("4. Click 'Process QR Code' button")
            print("5. Check browser console (F12) for debug messages")
        else:
            print(f"❌ Booking failed: {result['message']}")
            
    except Exception as e:
        print(f"❌ Error creating booking: {e}")

if __name__ == "__main__":
    create_new_patient_booking()