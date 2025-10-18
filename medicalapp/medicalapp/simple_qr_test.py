#!/usr/bin/env python
"""
Simple QR test for today's booking
"""

import os
import sys
import django
from datetime import date

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

from patients.models import Queue
from patients.booking_service import BookingService

# Get today's booking
today = date.today()
today_booking = Queue.objects.filter(
    qr_code__isnull=False, 
    status='booked',
    booking_date=today
).first()

if today_booking:
    print("Today's booking found:")
    print(f"   ID: {today_booking.id}")
    print(f"   Patient: {today_booking.patient.name}")
    print(f"   QR Code: {today_booking.qr_code}")
    print(f"   Status: {today_booking.status}")
    print(f"   Date: {today_booking.booking_date}")
    
    # Test QR activation
    print("\nTesting QR activation...")
    booking_service = BookingService()
    result = booking_service.activate_booking_by_qr(today_booking.qr_code)
    
    print("QR Activation Result:")
    if result['success']:
        print("SUCCESS!")
        for key, value in result.items():
            print(f"   {key}: {value}")
    else:
        print("FAILED!")
        print(f"   Error: {result['message']}")
else:
    print("No booking found for today")