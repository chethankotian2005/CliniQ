"""
Quick import test for SMS service
"""

try:
    print("Testing SMS service import...")
    from medicalapp.patients.sms_service import SMSService, format_booking_date
    print("✅ SMS service imported successfully")
    
    # Test the date formatting function
    print("Testing date formatting...")
    test_date = "2025-10-10"
    formatted = format_booking_date(test_date)
    print(f"✅ Date formatted: '{test_date}' → '{formatted}'")
    
    # Test SMS service creation
    print("Testing SMS service creation...")
    sms_service = SMSService()
    print("✅ SMS service created successfully")
    print(f"   Account SID: {sms_service.account_sid[:10]}...")
    print(f"   From Phone: {sms_service.from_phone}")
    
    print("\n🎉 All SMS service components are working!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")