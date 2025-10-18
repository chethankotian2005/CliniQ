"""
SMS Configuration and Management
Configure SMS settings and test integration
"""

# Twilio Configuration - Load from environment variables for security
import os

TWILIO_CONFIG = {
    'account_sid': os.getenv('TWILIO_ACCOUNT_SID'),
    'auth_token': os.getenv('TWILIO_AUTH_TOKEN'),
    'from_phone': os.getenv('TWILIO_PHONE_NUMBER'),
    'demo_to_phone': os.getenv('DEMO_PHONE_NUMBER', '+1234567890')  # Demo number from env
}

# SMS Templates Configuration
SMS_TEMPLATES = {
    'booking_confirmation': {
        'emoji': '🏥',
        'title': 'APPOINTMENT CONFIRMED!',
        'include_fields': ['patient_name', 'department', 'date', 'time', 'booking_id', 'hospital', 'instructions'],
        'max_length': 1600
    },
    'arrival_notification': {
        'emoji': '🎫',
        'title': 'CHECKED IN SUCCESSFULLY!',
        'include_fields': ['patient_name', 'token_number', 'department', 'position', 'wait_time', 'instructions'],
        'max_length': 1600
    },
    'doctor_call': {
        'emoji': '🩺',
        'title': 'YOUR TURN NOW!',
        'include_fields': ['token_number', 'patient_name', 'department', 'doctor', 'instructions'],
        'max_length': 1600
    },
    'appointment_reminder': {
        'emoji': '⏰',
        'title': 'APPOINTMENT REMINDER',
        'include_fields': ['patient_name', 'date', 'time', 'department', 'booking_id', 'instructions'],
        'max_length': 1600
    },
    'cancellation': {
        'emoji': '❌',
        'title': 'APPOINTMENT CANCELLED',
        'include_fields': ['patient_name', 'booking_id', 'department', 'date', 'instructions'],
        'max_length': 1600
    }
}

# SMS Settings
SMS_SETTINGS = {
    'enabled': True,
    'retry_failed': True,
    'retry_attempts': 3,
    'log_messages': True,
    'demo_mode': False,  # Set to True to only send to demo number
    'rate_limit': {
        'max_per_minute': 30,
        'max_per_hour': 100
    }
}

# Common instructions for different scenarios
INSTRUCTIONS = {
    'booking': [
        "Scan your QR code at reception",
        "Arrive 15 minutes early", 
        "Bring valid ID"
    ],
    'arrival': [
        "Watch the display screen for your token number",
        "We'll call your number when it's your turn"
    ],
    'doctor_call': [
        "Report to the reception desk immediately"
    ],
    'reminder': [
        "Arrive 15 minutes early",
        "Bring your QR code",
        "Carry valid ID"
    ],
    'cancellation': [
        "You can book a new appointment anytime through our portal",
        "Need help? Contact hospital directly"
    ]
}

def get_twilio_config():
    """Get Twilio configuration"""
    return TWILIO_CONFIG

def get_sms_template(template_type):
    """Get SMS template configuration"""
    return SMS_TEMPLATES.get(template_type, {})

def is_sms_enabled():
    """Check if SMS is enabled"""
    return SMS_SETTINGS.get('enabled', True)

def get_demo_phone():
    """Get demo phone number for testing"""
    return TWILIO_CONFIG.get('demo_to_phone')