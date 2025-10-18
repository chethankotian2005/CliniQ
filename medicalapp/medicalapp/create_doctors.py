#!/usr/bin/env python
"""
Create sample doctors for testing
"""

import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

from django.contrib.auth.models import User
from doctors.models import Doctor
from patients.models import Department

def create_sample_doctors():
    """Create sample doctors for testing"""
    
    print("Creating Sample Doctors for Testing")
    print("=" * 40)
    
    # Get the first department
    try:
        department = Department.objects.first()
        if not department:
            print("❌ No departments found! Creating a test department...")
            department = Department.objects.create(
                name="General Medicine",
                description="General medical consultations"
            )
            print(f"✅ Created department: {department.name}")
        else:
            print(f"📋 Using department: {department.name}")
    except Exception as e:
        print(f"❌ Error with departments: {e}")
        return
    
    # Doctor data
    doctors_data = [
        {
            'username': 'dr.smith',
            'password': 'doctor123',
            'email': 'dr.smith@hospital.com',
            'first_name': 'John',
            'last_name': 'Smith',
            'name': 'Dr. John Smith',
            'specialization': 'General Medicine',
            'qualification': 'MBBS, MD',
            'phone': '+1-555-0101'
        },
        {
            'username': 'dr.jones',
            'password': 'doctor123',
            'email': 'dr.jones@hospital.com',
            'first_name': 'Sarah',
            'last_name': 'Jones',
            'name': 'Dr. Sarah Jones',
            'specialization': 'Internal Medicine',
            'qualification': 'MBBS, MD',
            'phone': '+1-555-0102'
        },
        {
            'username': 'dr.kumar',
            'password': 'doctor123',
            'email': 'dr.kumar@hospital.com',
            'first_name': 'Raj',
            'last_name': 'Kumar',
            'name': 'Dr. Raj Kumar',
            'specialization': 'General Physician',
            'qualification': 'MBBS',
            'phone': '+1-555-0103'
        }
    ]
    
    created_count = 0
    
    for doctor_data in doctors_data:
        try:
            # Create or get user
            user, user_created = User.objects.get_or_create(
                username=doctor_data['username'],
                defaults={
                    'email': doctor_data['email'],
                    'first_name': doctor_data['first_name'],
                    'last_name': doctor_data['last_name'],
                    'is_staff': False,  # Don't make them staff
                    'is_active': True
                }
            )
            
            if user_created:
                user.set_password(doctor_data['password'])
                user.save()
                print(f"✅ Created user: {user.username}")
            else:
                print(f"👤 User already exists: {user.username}")
            
            # Create or get doctor profile
            doctor, doctor_created = Doctor.objects.get_or_create(
                user=user,
                defaults={
                    'name': doctor_data['name'],
                    'department': department,
                    'specialization': doctor_data['specialization'],
                    'qualification': doctor_data['qualification'],
                    'phone_number': doctor_data['phone'],
                    'email': doctor_data['email'],
                    'employee_id': f'DOC{user.id:03d}',  # Generate employee ID
                    'license_number': f'LIC{user.id:06d}',  # Generate license number
                    'years_of_experience': 5,  # Correct field name
                    'is_available': True,
                    'is_active': True
                }
            )
            
            if doctor_created:
                created_count += 1
                print(f"🩺 Created doctor: {doctor.name}")
            else:
                print(f"🩺 Doctor already exists: {doctor.name}")
                
        except Exception as e:
            print(f"❌ Error creating doctor {doctor_data['username']}: {e}")
    
    print(f"\n🎉 Summary:")
    print(f"📊 Total doctors in database: {Doctor.objects.count()}")
    print(f"🆕 New doctors created: {created_count}")
    print()
    print("📝 Login Credentials:")
    for doctor_data in doctors_data:
        print(f"👨‍⚕️ Username: {doctor_data['username']}")
        print(f"🔐 Password: {doctor_data['password']}")
        print(f"📍 Department: {department.name}")
        print()
    
    print("🔗 Doctor Login URL: http://127.0.0.1:8000/doctors/login/")

if __name__ == "__main__":
    create_sample_doctors()