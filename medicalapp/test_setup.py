#!/usr/bin/env python
"""
Quick test script to verify the chatbot and hospital portal setup
"""
import os
import sys
import django

# Add the medicalapp directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'medicalapp'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartqueue.settings')
django.setup()

def test_hospital_models():
    """Test hospital model creation"""
    try:
        from patients.hospital_models import Hospital
        print("✓ Hospital models imported successfully")
        
        # Test creating a hospital
        hospital = Hospital(
            name="Test Hospital",
            address="123 Test St",
            city="Test City",
            state="Test State",
            zip_code="12345",
            phone="+1-234-567-8900",
            email="test@hospital.com"
        )
        print("✓ Hospital model creation test passed")
        return True
    except Exception as e:
        print(f"✗ Hospital models test failed: {e}")
        return False

def test_chatbot_service():
    """Test chatbot service (requires API key)"""
    try:
        from patients.chatbot_service import MedicalChatbotService
        print("✓ Chatbot service imported successfully")
        
        # Check if API key is set
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("⚠ GEMINI_API_KEY not set - chatbot will not work")
            return False
        
        # Test chatbot initialization
        chatbot = MedicalChatbotService()
        print("✓ Chatbot service initialized successfully")
        
        # Test simple query (this will use API quota)
        response = chatbot.get_chat_response("Hello, can you help me?")
        if response.get('success'):
            print("✓ Chatbot response test passed")
            print(f"  Sample response: {response['response'][:100]}...")
        else:
            print(f"✗ Chatbot response test failed: {response.get('error')}")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Chatbot service test failed: {e}")
        return False

def test_portal_views():
    """Test portal views can be imported"""
    try:
        from patients.portal_views import patient_portal_home, create_sample_hospitals
        print("✓ Portal views imported successfully")
        return True
    except Exception as e:
        print(f"✗ Portal views test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Patient Portal & Chatbot Setup")
    print("=" * 50)
    
    tests = [
        ("Hospital Models", test_hospital_models),
        ("Portal Views", test_portal_views),
        ("Chatbot Service", test_chatbot_service),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\nTesting {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("Test Results Summary:")
    print("=" * 50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 All tests passed! The system is ready to use.")
    else:
        print("⚠ Some tests failed. Check the setup guide for troubleshooting.")
    
    print("\nNext steps:")
    print("1. Set GEMINI_API_KEY environment variable")
    print("2. Run: python manage.py makemigrations patients")
    print("3. Run: python manage.py migrate")
    print("4. Start server: python manage.py runserver")
    print("5. Visit: http://localhost:8000/patients/portal/")

if __name__ == "__main__":
    main()