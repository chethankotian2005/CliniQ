"""
SMS Service for sending appointment notifications via Twilio
"""

from twilio.rest import Client
from django.conf import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def format_booking_date(date_obj):
    """Helper function to safely format booking dates"""
    if not date_obj:
        return "Today"
    
    if hasattr(date_obj, 'strftime'):
        # It's a date/datetime object
        return date_obj.strftime("%B %d, %Y")
    else:
        # It's already a string
        return str(date_obj)


def is_sms_enabled():
    """Check if SMS credentials are configured."""
    return bool(
        getattr(settings, 'TWILIO_ACCOUNT_SID', None)
        and getattr(settings, 'TWILIO_AUTH_TOKEN', None)
        and getattr(settings, 'TWILIO_PHONE_NUMBER', None)
    )


class SMSService:
    """Service for sending SMS notifications to patients"""
    
    def __init__(self):
        # Use Twilio credentials from Django settings (updated with working credentials)
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_phone = settings.TWILIO_PHONE_NUMBER
        
        self.client = None

        if is_sms_enabled():
            try:
                self.client = Client(self.account_sid, self.auth_token)
            except Exception as exc:
                logger.warning(f"Twilio client init failed; SMS disabled for this request: {exc}")

    def _sms_unavailable(self):
        return {
            'success': False,
            'error': 'SMS service is not configured. Booking created without SMS notification.'
        }
    
    def send_booking_confirmation_sms(self, booking):
        """Send SMS confirmation when appointment is booked"""
        if not self.client:
            return self._sms_unavailable()
            
        try:
            # Format booking date and time
            booking_date = format_booking_date(booking.booking_date)
            time_slot = booking.booking_time_slot.title() if booking.booking_time_slot else "Any time"
            
            # Create simplified message content (better for trial accounts and India delivery)
            message_body = f"""CliniQ Medical Center

APPOINTMENT CONFIRMED

Patient: {booking.patient.name}
Department: {booking.department.name}
Date: {booking_date}
Time: {time_slot}
Booking ID: #{booking.id}

Hospital: {booking.department.hospital.name if booking.department.hospital else 'CliniQ Hospital'}

Instructions:
- Arrive 15 minutes early
- Bring valid ID
- Scan QR code at reception

Questions? Call hospital directly.

Thank you for choosing CliniQ."""

            # Send SMS
            message = self.client.messages.create(
                from_=self.from_phone,
                body=message_body,
                to=booking.patient.phone_number
            )
            
            # Log detailed information for debugging
            logger.info(f"Booking confirmation SMS sent to {booking.patient.phone_number}")
            logger.info(f"Message SID: {message.sid}, Status: {message.status}")
            logger.info(f"Price: {message.price}, Direction: {message.direction}")
            if message.error_code:
                logger.warning(f"SMS Error Code: {message.error_code}, Message: {message.error_message}")
            
            # Print debug info to console as well
            print(f"📱 SMS Debug Info:")
            print(f"   To: {booking.patient.phone_number}")
            print(f"   From: {self.from_phone}")
            print(f"   SID: {message.sid}")
            print(f"   Status: {message.status}")
            print(f"   Error Code: {message.error_code}")
            print(f"   Error Message: {message.error_message}")
            
            return {
                'success': True,
                'message_sid': message.sid,
                'to': booking.patient.phone_number,
                'status': message.status,
                'error_code': message.error_code,
                'error_message': message.error_message
            }
            
        except Exception as e:
            logger.error(f"Failed to send booking confirmation SMS: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_arrival_notification_sms(self, booking):
        """Send SMS when patient arrives and gets token number"""
        if not self.client:
            return self._sms_unavailable()

        try:
            message_body = f"""CliniQ Medical Center

CHECKED IN SUCCESSFULLY

Hello {booking.patient.name}

Your token number: {booking.token_number}
Department: {booking.department.name}
Position in queue: {booking.get_position_in_queue()}
Estimated wait: {booking.estimated_wait_time} minutes

Watch the display screen for your token number.
We will call your number when it's your turn.

Thank you for your patience."""

            # Send SMS
            message = self.client.messages.create(
                from_=self.from_phone,
                body=message_body,
                to=booking.patient.phone_number
            )
            
            logger.info(f"Arrival notification SMS sent to {booking.patient.phone_number}, SID: {message.sid}")
            return {
                'success': True,
                'message_sid': message.sid,
                'to': booking.patient.phone_number
            }
            
        except Exception as e:
            logger.error(f"Failed to send arrival notification SMS: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_doctor_call_notification_sms(self, booking):
        """Send SMS when doctor calls the patient"""
        if not self.client:
            return self._sms_unavailable()

        try:
            message_body = f"""🩺 YOUR TURN NOW!

Token #{booking.token_number}
{booking.patient.name}

👨‍⚕️ Please proceed to:
Department: {booking.department.name}
{f"Doctor: Dr. {booking.preferred_doctor.name}" if booking.preferred_doctor else ""}

📍 Report to the reception desk immediately

- CliniQ Team"""

            # Send SMS
            message = self.client.messages.create(
                from_=self.from_phone,
                body=message_body,
                to=booking.patient.phone_number
            )
            
            logger.info(f"Doctor call notification SMS sent to {booking.patient.phone_number}, SID: {message.sid}")
            return {
                'success': True,
                'message_sid': message.sid,
                'to': booking.patient.phone_number
            }
            
        except Exception as e:
            logger.error(f"Failed to send doctor call notification SMS: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_appointment_reminder_sms(self, booking):
        """Send SMS reminder before appointment (can be scheduled via Celery)"""
        if not self.client:
            return self._sms_unavailable()

        try:
            # Format booking date and time
            booking_date = format_booking_date(booking.booking_date)
            time_slot = booking.booking_time_slot.title() if booking.booking_time_slot else "Any time"
            
            message_body = f"""⏰ APPOINTMENT REMINDER

Hello {booking.patient.name},

Your appointment is scheduled for:
📅 Date: {booking_date}
🕐 Time: {time_slot}
🏥 Department: {booking.department.name}

💡 Remember to:
• Arrive 15 minutes early
• Bring your QR code
• Carry valid ID

Booking ID: #{booking.id}

- CliniQ Team"""

            # Send SMS
            message = self.client.messages.create(
                from_=self.from_phone,
                body=message_body,
                to=booking.patient.phone_number
            )
            
            logger.info(f"Appointment reminder SMS sent to {booking.patient.phone_number}, SID: {message.sid}")
            return {
                'success': True,
                'message_sid': message.sid,
                'to': booking.patient.phone_number
            }
            
        except Exception as e:
            logger.error(f"Failed to send appointment reminder SMS: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_cancellation_sms(self, booking):
        """Send SMS when appointment is cancelled"""
        if not self.client:
            return self._sms_unavailable()

        try:
            # Format booking date
            formatted_date = format_booking_date(booking.booking_date)
            if formatted_date == "Today":
                formatted_date = "N/A"
                
            message_body = f"""❌ APPOINTMENT CANCELLED

Hello {booking.patient.name},

Your appointment has been cancelled:
Booking ID: #{booking.id}
Department: {booking.department.name}
Original Date: {formatted_date}

💡 You can book a new appointment anytime through our portal.

Need help? Contact hospital directly.

- CliniQ Team"""

            # Send SMS
            message = self.client.messages.create(
                from_=self.from_phone,
                body=message_body,
                to=booking.patient.phone_number
            )
            
            logger.info(f"Cancellation SMS sent to {booking.patient.phone_number}, SID: {message.sid}")
            return {
                'success': True,
                'message_sid': message.sid,
                'to': booking.patient.phone_number
            }
            
        except Exception as e:
            logger.error(f"Failed to send cancellation SMS: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }