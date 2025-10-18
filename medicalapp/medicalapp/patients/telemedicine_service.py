"""
Telemedicine Service for Managing Teleappointments
Handles: Video call setup, meeting management, notifications
"""

import uuid
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from django.db import models
from django.conf import settings
from django.core.mail import send_mail

from .models import TeleAppointment, Queue, Patient
from .sms_service import SMSService


class TelemedicineService:
    """Service to handle telemedicine appointments"""
    
    def __init__(self):
        self.sms_service = SMSService()
    
    def create_teleappointment(self, queue_entry, scheduled_time, platform='webrtc'):
        """Create a new telemedicine appointment"""
        try:
            with transaction.atomic():
                # Update queue entry to telemedicine type
                queue_entry.appointment_type = 'telemedicine'
                queue_entry.save(update_fields=['appointment_type'])
                
                # Create TeleAppointment record
                tele_appointment = TeleAppointment.objects.create(
                    queue_entry=queue_entry,
                    platform=platform,
                    scheduled_start_time=scheduled_time,
                    meeting_id=self.generate_meeting_id(),
                    tele_status='scheduled'
                )
                
                # Generate meeting URL based on platform
                tele_appointment.meeting_url = self.generate_meeting_url(tele_appointment)
                tele_appointment.save(update_fields=['meeting_url'])
                
                # Send confirmation to patient
                self.send_appointment_confirmation(tele_appointment)
                
                return {
                    'success': True,
                    'message': 'Teleappointment created successfully',
                    'appointment_id': tele_appointment.id,
                    'meeting_url': tele_appointment.meeting_url,
                    'meeting_id': tele_appointment.meeting_id,
                    'scheduled_time': tele_appointment.scheduled_start_time.isoformat()
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Error creating teleappointment: {str(e)}'
            }
    
    def generate_meeting_id(self):
        """Generate a unique meeting ID"""
        return f"CLINIQ-{uuid.uuid4().hex[:8].upper()}"
    
    def generate_meeting_url(self, tele_appointment):
        """Generate meeting URL based on platform"""
        if tele_appointment.platform == 'webrtc':
            # For WebRTC, create a custom meeting room URL
            return f"/video-call/{tele_appointment.meeting_id}/"
        elif tele_appointment.platform == 'zoom':
            # For Zoom, this would integrate with Zoom API
            return f"https://zoom.us/j/{tele_appointment.meeting_id}"
        elif tele_appointment.platform == 'google_meet':
            # For Google Meet integration
            return f"https://meet.google.com/{tele_appointment.meeting_id}"
        else:
            # Default to WebRTC
            return f"/video-call/{tele_appointment.meeting_id}/"
    
    def send_appointment_confirmation(self, tele_appointment):
        """Send appointment confirmation via SMS and email"""
        try:
            patient = tele_appointment.queue_entry.patient
            doctor = tele_appointment.queue_entry.assigned_doctor or tele_appointment.queue_entry.preferred_doctor
            
            # Format the appointment time in IST
            appointment_time = tele_appointment.scheduled_start_time.strftime('%Y-%m-%d %H:%M IST')
            
            # SMS message
            sms_message = f"""
🏥 CLINIQ Teleappointment Confirmed

📅 Date: {appointment_time}
👨‍⚕️ Doctor: {doctor.name if doctor else 'TBD'}
🏥 Department: {tele_appointment.queue_entry.department.name}

💻 Join your video consultation:
{tele_appointment.meeting_url}

📱 Meeting ID: {tele_appointment.meeting_id}

⏰ Please join 5 minutes early. Ensure stable internet connection.

Questions? Call: +91-XXXXXXXXXX
            """.strip()
            
            # Send SMS
            sms_result = self.sms_service.send_sms(
                phone_number=patient.phone_number,
                message=sms_message
            )
            
            # Send email if available
            if patient.email:
                self.send_email_confirmation(tele_appointment)
            
            # Update notification timestamp
            tele_appointment.meeting_link_sent_at = timezone.now()
            tele_appointment.save(update_fields=['meeting_link_sent_at'])
            
            return sms_result
            
        except Exception as e:
            print(f"Error sending confirmation: {str(e)}")
            return {'success': False, 'message': str(e)}
    
    def send_email_confirmation(self, tele_appointment):
        """Send email confirmation for teleappointment"""
        try:
            patient = tele_appointment.queue_entry.patient
            doctor = tele_appointment.queue_entry.assigned_doctor or tele_appointment.queue_entry.preferred_doctor
            
            subject = f"CLINIQ Teleappointment Confirmation - {tele_appointment.scheduled_start_time.strftime('%B %d, %Y')}"
            
            message = f"""
Dear {patient.name},

Your teleappointment has been confirmed with the following details:

📅 Date & Time: {tele_appointment.scheduled_start_time.strftime('%B %d, %Y at %I:%M %p IST')}
👨‍⚕️ Doctor: {doctor.name if doctor else 'To be assigned'}
🏥 Department: {tele_appointment.queue_entry.department.name}

💻 Video Call Details:
Meeting URL: {tele_appointment.meeting_url}
Meeting ID: {tele_appointment.meeting_id}

📋 Pre-appointment Instructions:
- Test your device's camera and microphone before the appointment
- Ensure you have a stable internet connection
- Find a quiet, private space for the consultation
- Have your medical records and current medications ready
- Join the meeting 5 minutes early

🔧 Technical Requirements:
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Camera and microphone enabled
- Stable internet connection

If you need to reschedule or have any questions, please contact us at +91-XXXXXXXXXX

Thank you for choosing CLINIQ for your healthcare needs.

Best regards,
CLINIQ Medical Team
            """
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[patient.email],
                fail_silently=False,
            )
            
            return True
            
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def send_reminder(self, tele_appointment, minutes_before=30):
        """Send reminder before the appointment"""
        try:
            patient = tele_appointment.queue_entry.patient
            
            reminder_message = f"""
🔔 CLINIQ Teleappointment Reminder

Your video consultation is in {minutes_before} minutes!

⏰ Time: {tele_appointment.scheduled_start_time.strftime('%H:%M IST')}
💻 Join here: {tele_appointment.meeting_url}
📱 Meeting ID: {tele_appointment.meeting_id}

Please join now to avoid delays.
            """.strip()
            
            result = self.sms_service.send_sms(
                phone_number=patient.phone_number,
                message=reminder_message
            )
            
            # Update reminder timestamp
            tele_appointment.reminder_sent_at = timezone.now()
            tele_appointment.save(update_fields=['reminder_sent_at'])
            
            return result
            
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    def get_upcoming_appointments(self, patient_id=None, doctor_id=None, limit=10):
        """Get upcoming teleappointments"""
        try:
            now = timezone.now()
            queryset = TeleAppointment.objects.filter(
                scheduled_start_time__gte=now,
                tele_status__in=['scheduled', 'ready']
            ).select_related('queue_entry__patient', 'queue_entry__assigned_doctor')
            
            if patient_id:
                queryset = queryset.filter(queue_entry__patient_id=patient_id)
            
            if doctor_id:
                queryset = queryset.filter(
                    models.Q(queue_entry__assigned_doctor_id=doctor_id) |
                    models.Q(queue_entry__preferred_doctor_id=doctor_id)
                )
            
            appointments = queryset.order_by('scheduled_start_time')[:limit]
            
            result = []
            for appointment in appointments:
                result.append({
                    'id': appointment.id,
                    'patient_name': appointment.queue_entry.patient.name,
                    'patient_phone': appointment.queue_entry.patient.phone_number,
                    'doctor_name': (appointment.queue_entry.assigned_doctor.name 
                                  if appointment.queue_entry.assigned_doctor 
                                  else 'TBD'),
                    'department': appointment.queue_entry.department.name,
                    'scheduled_time': appointment.scheduled_start_time.isoformat(),
                    'meeting_url': appointment.meeting_url,
                    'meeting_id': appointment.meeting_id,
                    'status': appointment.tele_status,
                    'platform': appointment.platform,
                    'is_ready': appointment.is_ready_to_start()
                })
            
            return {
                'success': True,
                'appointments': result
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Error fetching appointments: {str(e)}'
            }
    
    def start_video_session(self, appointment_id):
        """Start a video session"""
        try:
            appointment = TeleAppointment.objects.get(id=appointment_id)
            
            if not appointment.is_ready_to_start():
                return {
                    'success': False,
                    'message': 'Appointment is not ready to start yet'
                }
            
            appointment.start_meeting()
            
            return {
                'success': True,
                'message': 'Video session started',
                'meeting_url': appointment.meeting_url,
                'meeting_id': appointment.meeting_id
            }
            
        except TeleAppointment.DoesNotExist:
            return {
                'success': False,
                'message': 'Appointment not found'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error starting session: {str(e)}'
            }
    
    def end_video_session(self, appointment_id, notes=""):
        """End a video session"""
        try:
            appointment = TeleAppointment.objects.get(id=appointment_id)
            
            if appointment.tele_status != 'in_progress':
                return {
                    'success': False,
                    'message': 'No active session to end'
                }
            
            # Add any technical notes
            if notes:
                appointment.technical_notes = notes
                appointment.save(update_fields=['technical_notes'])
            
            appointment.end_meeting()
            
            # Send completion SMS
            patient = appointment.queue_entry.patient
            completion_message = f"""
✅ CLINIQ Teleappointment Completed

Thank you for your consultation!

📋 Your appointment summary will be sent shortly.
💊 Please follow the prescribed treatment plan.

Rate your experience: {settings.SITE_URL}/feedback/{appointment.queue_entry.id}/

Questions? Call: +91-XXXXXXXXXX
            """.strip()
            
            self.sms_service.send_sms(
                phone_number=patient.phone_number,
                message=completion_message
            )
            
            return {
                'success': True,
                'message': 'Video session ended successfully',
                'duration_minutes': appointment.get_meeting_duration()
            }
            
        except TeleAppointment.DoesNotExist:
            return {
                'success': False,
                'message': 'Appointment not found'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error ending session: {str(e)}'
            }
    
    def reschedule_appointment(self, appointment_id, new_time):
        """Reschedule a teleappointment"""
        try:
            appointment = TeleAppointment.objects.get(id=appointment_id)
            
            if appointment.tele_status in ['completed', 'cancelled']:
                return {
                    'success': False,
                    'message': 'Cannot reschedule completed or cancelled appointment'
                }
            
            old_time = appointment.scheduled_start_time
            appointment.scheduled_start_time = new_time
            appointment.tele_status = 'scheduled'
            appointment.save()
            
            # Send reschedule notification
            patient = appointment.queue_entry.patient
            reschedule_message = f"""
📅 CLINIQ Teleappointment Rescheduled

Your appointment has been moved:

❌ OLD: {old_time.strftime('%B %d, %Y at %I:%M %p IST')}
✅ NEW: {new_time.strftime('%B %d, %Y at %I:%M %p IST')}

💻 Same meeting link: {appointment.meeting_url}
📱 Meeting ID: {appointment.meeting_id}

Please update your calendar.
            """.strip()
            
            self.sms_service.send_sms(
                phone_number=patient.phone_number,
                message=reschedule_message
            )
            
            return {
                'success': True,
                'message': 'Appointment rescheduled successfully',
                'new_time': new_time.isoformat()
            }
            
        except TeleAppointment.DoesNotExist:
            return {
                'success': False,
                'message': 'Appointment not found'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'Error rescheduling: {str(e)}'
            }