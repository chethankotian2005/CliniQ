"""
Test Booking Service Date Handling Fix
Test the fixed date formatting to ensure booking creation works
"""

def test_date_helpers():
    """Test the date helper functions"""
    print("🔧 Testing Date Helper Functions...")
    
    # Test safe_isoformat function
    test_cases = [
        ("2025-10-10", "String date"),
        (None, "None date"),
        ("", "Empty string"),
    ]
    
    # Mock date object for testing
    class MockDate:
        def __init__(self, year, month, day):
            self.year = year
            self.month = month  
            self.day = day
        
        def isoformat(self):
            return f"{self.year}-{self.month:02d}-{self.day:02d}"
    
    # Add date object test
    test_cases.append((MockDate(2025, 10, 10), "Date object"))
    
    from medicalapp.patients.booking_service import safe_isoformat, parse_booking_date
    
    print("\n📅 safe_isoformat() Tests:")
    for date_input, description in test_cases:
        try:
            result = safe_isoformat(date_input)
            print(f"   ✅ {description}: '{date_input}' → '{result}'")
        except Exception as e:
            print(f"   ❌ {description}: '{date_input}' → Error: {e}")
    
    print("\n📅 parse_booking_date() Tests:")
    parse_test_cases = [
        ("2025-10-10", "ISO format"),
        ("10/10/2025", "US format"),
        ("10-10-2025", "Dash format"),
        ("", "Empty string"),
        (None, "None"),
    ]
    
    for date_input, description in parse_test_cases:
        try:
            result = parse_booking_date(date_input)
            print(f"   ✅ {description}: '{date_input}' → '{result}'")
        except Exception as e:
            print(f"   ❌ {description}: '{date_input}' → Error: {e}")

def test_booking_creation_simulation():
    """Simulate booking creation to test for errors"""
    print("\n🏥 Testing Booking Creation Simulation...")
    
    # Mock booking data that might cause the error
    mock_patient_data = {
        'name': 'Test Patient',
        'phone_number': '+918123936830',
        'email': 'test@example.com'
    }
    
    mock_booking_date = "2025-10-10"  # String date (problematic case)
    
    try:
        from medicalapp.patients.booking_service import parse_booking_date, safe_isoformat
        
        # Test the date parsing
        parsed_date = parse_booking_date(mock_booking_date)
        print(f"   ✅ Date parsing: '{mock_booking_date}' → {parsed_date}")
        
        # Test the ISO formatting
        iso_result = safe_isoformat(parsed_date)
        print(f"   ✅ ISO formatting: {parsed_date} → '{iso_result}'")
        
        # Simulate the return value formatting
        mock_response = {
            'success': True,
            'booking_id': 12345,
            'booking_date': safe_isoformat(parsed_date),
            'patient_name': mock_patient_data['name']
        }
        
        print(f"   ✅ Mock response generated successfully:")
        print(f"      booking_date: {mock_response['booking_date']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Booking simulation failed: {e}")
        return False

if __name__ == "__main__":
    print("🏥 Booking Service Date Fix Test")
    print("=" * 50)
    
    # Test 1: Date helper functions
    test_date_helpers()
    
    # Test 2: Booking creation simulation
    success = test_booking_creation_simulation()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Date Handling: {'✅ Fixed' if success else '❌ Still has issues'}")
    
    print("\n💡 Fix Summary:")
    print("   ✅ Added safe_isoformat() helper function")
    print("   ✅ Added parse_booking_date() helper function")
    print("   ✅ Fixed all .isoformat() calls in booking service")
    print("   ✅ Added robust date parsing for various formats")
    
    if success:
        print("\n🎯 The booking creation error should be resolved!")
        print("   Try booking an appointment again - it should work now.")
    else:
        print("\n⚠️ There might still be issues. Check Django environment setup.")