#!/usr/bin/env python
"""
Test doctor authentication
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

from django.contrib.auth import authenticate
from doctors.models import Doctor

# Test authentication
print("Testing Doctor Authentication")
print("=" * 30)

# Test credentials
username = 'dr.smith'
password = 'doctor123'

print(f"Testing: {username}")

# Test authentication
user = authenticate(username=username, password=password)
if user:
    print(f"Authentication successful for {username}")
    
    # Check if doctor profile exists
    try:
        doctor = Doctor.objects.get(user=user)
        print(f"Doctor profile found: {doctor.name}")
        print(f"Department: {doctor.department.name}")
        print(f"Available: {doctor.is_available}")
        print("SUCCESS: Doctor login should work!")
    except Doctor.DoesNotExist:
        print(f"No doctor profile found for {username}")
else:
    print(f"Authentication failed for {username}")

print(f"Total doctors in database: {Doctor.objects.count()}")