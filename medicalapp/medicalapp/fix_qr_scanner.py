#!/usr/bin/env python
"""
Create a working QR code for testing and fix the QR scanner
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
from django.utils import timezone

def create_working_test_booking():
    """Create a proper test booking with valid QR code"""
    print("Creating Working Test Booking")
    print("=" * 40)
    
    try:
        # Get or create patient
        patient, created = Patient.objects.get_or_create(
            phone_number='+918123936830',
            defaults={
                'name': 'Chethan V Kotian',
                'email': 'kotianchethan4@gmail.com',
                'age': 30,
                'gender': 'M'
            }
        )
        print(f"Patient: {patient.name} ({'created' if created else 'existing'})")
        
        # Get active department
        department = Department.objects.filter(is_active=True).first()
        if not department:
            print("❌ No active department found!")
            return None
            
        print(f"Department: {department.name}")
        
        # Create booking manually with proper QR code format
        import uuid
        
        # Create the booking first
        booking = Queue.objects.create(
            patient=patient,
            department=department,
            status='booked',
            is_online_booking=True,
            booked_at=timezone.now(),
            booking_date=timezone.now().date(),
            booking_time_slot='evening',
            appointment_type='in_person',
            notes='Test booking for QR scanner - manually created',
            token_number=0  # Will be assigned when QR is scanned
        )
        
        # Generate proper QR code format: CLINIQ:BOOKING:{id}:{hash}
        qr_hash = uuid.uuid4().hex[:8]
        qr_code = f"CLINIQ:BOOKING:{booking.id}:{qr_hash}"
        
        # Update booking with QR code
        booking.qr_code = qr_code
        booking.save()
        
        print(f"✅ Test booking created successfully!")
        print(f"Booking ID: {booking.id}")
        print(f"QR Code: {qr_code}")
        print(f"Status: {booking.status}")
        print(f"Date: {booking.booking_date}")
        print()
        print("=" * 50)
        print("🧪 TEST QR CODE:")
        print(qr_code)
        print("=" * 50)
        print()
        
        return qr_code
        
    except Exception as e:
        print(f"❌ Error creating test booking: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_qr_processing(qr_code):
    """Test QR code processing"""
    print(f"Testing QR Code Processing: {qr_code}")
    print("-" * 50)
    
    try:
        from patients.booking_service import BookingService
        booking_service = BookingService()
        
        result = booking_service.activate_booking_by_qr(qr_code)
        
        print(f"Processing Result:")
        print(f"  Success: {result['success']}")
        
        if result['success']:
            print(f"  Patient: {result.get('patient_name')}")
            print(f"  Token: {result.get('token_number')}")
            print(f"  Department: {result.get('department')}")
            print(f"  Message: {result.get('message')}")
            print("✅ QR processing is working!")
        else:
            print(f"  Error: {result.get('message')}")
            print("❌ QR processing failed")
            
        return result['success']
        
    except Exception as e:
        print(f"❌ Error testing QR processing: {e}")
        return False

def main():
    """Main function"""
    # Create test booking
    qr_code = create_working_test_booking()
    
    if qr_code:
        print("\nNow testing QR processing...")
        success = test_qr_processing(qr_code)
        
        if success:
            print("\n🎉 QR SCANNER SETUP COMPLETE!")
            print("\nHow to test the scanner:")
            print("1. Go to: http://127.0.0.1:8000/adminpanel/")
            print("2. Login: admin / admin123")
            print("3. Click 'Open QR Scanner'")
            print("4. Click 'Manual Entry'")
            print(f"5. Paste: {qr_code}")
            print("6. Click 'Process QR Code'")
            print("7. ✅ Should show success with token assignment")
            
            # Create another booking for camera testing
            print("\nCreating another booking for camera testing...")
            another_qr = create_working_test_booking()
            if another_qr:
                print(f"\nFor camera testing, create a QR code image containing:")
                print(f"{another_qr}")
        else:
            print("\n❌ QR processing is not working. Check the error above.")
    else:
        print("\n❌ Failed to create test booking")

if __name__ == "__main__":
    main()