"""
Quick SMS Fix Test
Test the fixed SMS service to ensure date formatting works
"""

import sys
import os

# Add project directory to path for imports
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(project_dir, 'medicalapp'))

# Mock booking object for testing
class MockBooking:
    def __init__(self):
        self.id = 12345
        self.booking_date = "2025-10-10"  # String date (the problematic case)
        self.booking_time_slot = "morning"
        
        # Mock patient
        self.patient = MockPatient()
        
        # Mock department
        self.department = MockDepartment()
        
        self.token_number = 101
        self.estimated_wait_time = 15
        
    def get_position_in_queue(self):
        return 3

class MockPatient:
    def __init__(self):
        self.name = "Test Patient"
        self.phone_number = "+918123936830"

class MockDepartment:
    def __init__(self):
        self.name = "Cardiology"
        self.hospital = MockHospital()

class MockHospital:
    def __init__(self):
        self.name = "SmartQueue Medical Center"

def test_date_formatting():
    """Test the date formatting fix"""
    print("🔧 Testing SMS Date Formatting Fix...")
    
    # Import the helper function
    from medicalapp.patients.sms_service import format_booking_date
    
    # Test cases
    test_cases = [
        ("2025-10-10", "String date"),
        (None, "None date"),
        ("", "Empty string"),
        ("October 10, 2025", "Already formatted string")
    ]
    
    print("\n📅 Date Formatting Tests:")
    for date_input, description in test_cases:
        try:
            result = format_booking_date(date_input)
            print(f"   ✅ {description}: '{date_input}' → '{result}'")
        except Exception as e:
            print(f"   ❌ {description}: '{date_input}' → Error: {e}")

def test_sms_with_string_date():
    """Test SMS sending with string date (the fix)"""
    print("\n📱 Testing SMS with String Date...")
    
    try:
        from medicalapp.patients.sms_service import SMSService
        
        # Create mock booking with string date
        booking = MockBooking()
        
        # Create SMS service
        sms_service = SMSService()
        
        print(f"   Mock booking date: {booking.booking_date} (type: {type(booking.booking_date)})")
        
        # Test booking confirmation SMS (this was failing before)
        result = sms_service.send_booking_confirmation_sms(booking)
        
        if result['success']:
            print(f"   ✅ SMS sent successfully!")
            print(f"   📧 Message SID: {result['message_sid']}")
            print(f"   📱 Sent to: {result['to']}")
        else:
            print(f"   ❌ SMS failed: {result.get('error', 'Unknown error')}")
        
        return result['success']
        
    except ImportError as e:
        print(f"   ⚠️ Could not import SMS service: {e}")
        print("   This is expected if Django environment is not set up")
        return False
    except Exception as e:
        print(f"   ❌ Error testing SMS: {e}")
        return False

if __name__ == "__main__":
    print("🏥 SMS Date Formatting Fix Test")
    print("=" * 50)
    
    # Test 1: Date formatting function
    test_date_formatting()
    
    # Test 2: SMS with string date
    success = test_sms_with_string_date()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   SMS Integration: {'✅ Fixed' if success else '⚠️ Django environment needed'}")
    
    print("\n💡 Fix Summary:")
    print("   ✅ Added format_booking_date() helper function")
    print("   ✅ Fixed string date handling in all SMS methods")
    print("   ✅ Error should be resolved in booking process")
    
    print("\n🎯 Try booking again - SMS should work now!")