"""
Telemedicine Views - Handle teleappointment booking and management
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import json
from datetime import datetime, timedelta
from django.utils import timezone

from .models import Patient, Department, Queue, TeleAppointment
from .telemedicine_service import TelemedicineService
from .booking_service import BookingService
from doctors.models import Doctor


class TeleAppointmentBookingView(View):
    """Handle teleappointment booking creation"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['name', 'phone_number', 'department_id', 'appointment_date', 'appointment_time']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'success': False,
                        'message': f'{field} is required for teleappointment'
                    }, status=400)
            
            # Parse appointment datetime
            appointment_date = data.get('appointment_date')
            appointment_time = data.get('appointment_time')
            
            try:
                # Combine date and time
                appointment_datetime = datetime.strptime(
                    f"{appointment_date} {appointment_time}", 
                    "%Y-%m-%d %H:%M"
                )
                # Make timezone aware
                appointment_datetime = timezone.make_aware(appointment_datetime)
                
                # Validate that appointment is in the future
                if appointment_datetime <= timezone.now():
                    return JsonResponse({
                        'success': False,
                        'message': 'Appointment must be scheduled for a future date and time'
                    }, status=400)
                
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'message': 'Invalid date or time format. Use YYYY-MM-DD for date and HH:MM for time'
                }, status=400)
            
            # First create the regular booking
            booking_service = BookingService()
            booking_result = booking_service.create_online_booking(
                patient_data=data,
                department_id=data['department_id'],
                doctor_id=data.get('doctor_id'),
                booking_date=appointment_date,
                time_slot=appointment_time,
                appointment_type='telemedicine'  # Specify this is a teleappointment
            )
            
            if not booking_result['success']:
                return JsonResponse(booking_result, status=400)
            
            # Get the created queue entry
            queue_entry = Queue.objects.get(id=booking_result['booking_id'])
            
            # Create teleappointment
            telemedicine_service = TelemedicineService()
            tele_result = telemedicine_service.create_teleappointment(
                queue_entry=queue_entry,
                scheduled_time=appointment_datetime,
                platform=data.get('platform', 'webrtc')
            )
            
            if tele_result['success']:
                # Combine the results
                return JsonResponse({
                    'success': True,
                    'message': 'Teleappointment booked successfully',
                    'booking_id': booking_result['booking_id'],
                    'appointment_id': tele_result['appointment_id'],
                    'meeting_url': tele_result['meeting_url'],
                    'meeting_id': tele_result['meeting_id'],
                    'scheduled_time': tele_result['scheduled_time'],
                    'patient_name': data['name'],
                    'department': queue_entry.department.name,
                    'doctor': queue_entry.preferred_doctor.name if queue_entry.preferred_doctor else 'To be assigned'
                })
            else:
                # If teleappointment creation fails, we should clean up
                # but for now just return the error
                return JsonResponse(tele_result, status=400)
            
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Server error: {str(e)}'
            }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_teleappointment_status(request, appointment_id):
    """Get teleappointment status and details"""
    try:
        appointment = get_object_or_404(TeleAppointment, id=appointment_id)
        
        return Response({
            'success': True,
            'appointment': {
                'id': appointment.id,
                'patient_name': appointment.queue_entry.patient.name,
                'patient_phone': appointment.queue_entry.patient.phone_number,
                'doctor_name': (appointment.queue_entry.assigned_doctor.name 
                              if appointment.queue_entry.assigned_doctor 
                              else (appointment.queue_entry.preferred_doctor.name 
                                   if appointment.queue_entry.preferred_doctor 
                                   else 'To be assigned')),
                'department': appointment.queue_entry.department.name,
                'scheduled_time': appointment.scheduled_start_time.isoformat(),
                'status': appointment.tele_status,
                'meeting_url': appointment.meeting_url,
                'meeting_id': appointment.meeting_id,
                'platform': appointment.platform,
                'is_ready': appointment.is_ready_to_start(),
                'pre_call_instructions': appointment.pre_call_instructions,
                'actual_start_time': appointment.actual_start_time.isoformat() if appointment.actual_start_time else None,
                'actual_end_time': appointment.actual_end_time.isoformat() if appointment.actual_end_time else None,
                'duration_minutes': appointment.get_meeting_duration()
            }
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error fetching appointment: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_patient_teleappointments(request, phone_number):
    """Get all teleappointments for a patient by phone number"""
    try:
        patient = get_object_or_404(Patient, phone_number=phone_number)
        
        appointments = TeleAppointment.objects.filter(
            queue_entry__patient=patient
        ).select_related(
            'queue_entry__department',
            'queue_entry__assigned_doctor',
            'queue_entry__preferred_doctor'
        ).order_by('-scheduled_start_time')[:10]  # Last 10 appointments
        
        appointment_list = []
        for appointment in appointments:
            appointment_list.append({
                'id': appointment.id,
                'scheduled_time': appointment.scheduled_start_time.isoformat(),
                'status': appointment.tele_status,
                'department': appointment.queue_entry.department.name,
                'doctor': (appointment.queue_entry.assigned_doctor.name 
                          if appointment.queue_entry.assigned_doctor 
                          else (appointment.queue_entry.preferred_doctor.name 
                               if appointment.queue_entry.preferred_doctor 
                               else 'To be assigned')),
                'meeting_url': appointment.meeting_url if appointment.tele_status in ['scheduled', 'ready', 'in_progress'] else None,
                'meeting_id': appointment.meeting_id,
                'platform': appointment.platform,
                'is_ready': appointment.is_ready_to_start(),
                'duration_minutes': appointment.get_meeting_duration()
            })
        
        return Response({
            'success': True,
            'patient_name': patient.name,
            'appointments': appointment_list
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error fetching appointments: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def start_video_session(request):
    """Start a video session"""
    try:
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')
        
        if not appointment_id:
            return Response({
                'success': False,
                'message': 'appointment_id is required'
            }, status=400)
        
        telemedicine_service = TelemedicineService()
        result = telemedicine_service.start_video_session(appointment_id)
        
        return Response(result, status=200 if result['success'] else 400)
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Server error: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def end_video_session(request):
    """End a video session"""
    try:
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')
        notes = data.get('notes', '')
        
        if not appointment_id:
            return Response({
                'success': False,
                'message': 'appointment_id is required'
            }, status=400)
        
        telemedicine_service = TelemedicineService()
        result = telemedicine_service.end_video_session(appointment_id, notes)
        
        return Response(result, status=200 if result['success'] else 400)
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Server error: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def reschedule_teleappointment(request):
    """Reschedule a teleappointment"""
    try:
        data = json.loads(request.body)
        appointment_id = data.get('appointment_id')
        new_date = data.get('new_date')
        new_time = data.get('new_time')
        
        if not all([appointment_id, new_date, new_time]):
            return Response({
                'success': False,
                'message': 'appointment_id, new_date, and new_time are required'
            }, status=400)
        
        try:
            # Parse new datetime
            new_datetime = datetime.strptime(
                f"{new_date} {new_time}", 
                "%Y-%m-%d %H:%M"
            )
            new_datetime = timezone.make_aware(new_datetime)
            
            if new_datetime <= timezone.now():
                return Response({
                    'success': False,
                    'message': 'New appointment time must be in the future'
                }, status=400)
                
        except ValueError:
            return Response({
                'success': False,
                'message': 'Invalid date or time format'
            }, status=400)
        
        telemedicine_service = TelemedicineService()
        result = telemedicine_service.reschedule_appointment(appointment_id, new_datetime)
        
        return Response(result, status=200 if result['success'] else 400)
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Server error: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_available_slots(request, department_id):
    """Get available time slots for teleappointments"""
    try:
        department = get_object_or_404(Department, id=department_id)
        
        # Get the next 7 days
        today = timezone.now().date()
        available_slots = []
        
        for days_ahead in range(1, 8):  # Next 7 days, starting tomorrow
            date = today + timedelta(days=days_ahead)
            
            # Define time slots (assuming 9 AM to 5 PM with 30-minute slots)
            time_slots = []
            start_hour = 9
            end_hour = 17
            
            for hour in range(start_hour, end_hour):
                for minute in [0, 30]:
                    if hour == end_hour - 1 and minute == 30:
                        continue  # Don't include 5:30 PM
                    
                    slot_time = f"{hour:02d}:{minute:02d}"
                    slot_datetime = timezone.make_aware(
                        datetime.combine(date, datetime.strptime(slot_time, "%H:%M").time())
                    )
                    
                    # Check if slot is already booked
                    existing_appointment = TeleAppointment.objects.filter(
                        queue_entry__department=department,
                        scheduled_start_time=slot_datetime,
                        tele_status__in=['scheduled', 'ready', 'in_progress']
                    ).exists()
                    
                    if not existing_appointment:
                        time_slots.append({
                            'time': slot_time,
                            'datetime': slot_datetime.isoformat(),
                            'available': True
                        })
            
            if time_slots:  # Only include days with available slots
                available_slots.append({
                    'date': date.isoformat(),
                    'day_name': date.strftime('%A'),
                    'slots': time_slots
                })
        
        return Response({
            'success': True,
            'department_name': department.name,
            'available_slots': available_slots
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error fetching available slots: {str(e)}'
        }, status=500)


# Template views
def teleappointment_booking_page(request):
    """Teleappointment booking page template"""
    departments = Department.objects.filter(is_active=True)
    doctors = Doctor.objects.filter(is_active=True, is_available=True)
    
    context = {
        'departments': departments,
        'doctors': doctors,
        'page_title': 'Book Teleappointment',
        'form_type': 'teleappointment'
    }
    return render(request, 'patients/teleappointment_booking.html', context)


def video_call_room(request, meeting_id):
    """Video call room template"""
    try:
        appointment = get_object_or_404(TeleAppointment, meeting_id=meeting_id)
        
        # Check if the user should have access to this meeting
        # For now, we'll allow anyone with the meeting ID
        
        context = {
            'appointment': appointment,
            'meeting_id': meeting_id,
            'patient_name': appointment.queue_entry.patient.name,
            'doctor_name': (appointment.queue_entry.assigned_doctor.name 
                           if appointment.queue_entry.assigned_doctor 
                           else 'Doctor'),
            'department': appointment.queue_entry.department.name,
            'scheduled_time': appointment.scheduled_start_time,
            'is_ready': appointment.is_ready_to_start()
        }
        
        return render(request, 'patients/video_call_room.html', context)
        
    except Exception as e:
        return render(request, 'patients/error.html', {
            'error_message': f'Meeting not found: {str(e)}'
        })


def teleappointment_management(request):
    """Teleappointment management page for staff"""
    # This would typically require staff authentication
    
    today = timezone.now().date()
    upcoming_appointments = TeleAppointment.objects.filter(
        scheduled_start_time__date__gte=today,
        tele_status__in=['scheduled', 'ready', 'in_progress']
    ).select_related(
        'queue_entry__patient',
        'queue_entry__department',
        'queue_entry__assigned_doctor'
    ).order_by('scheduled_start_time')[:20]
    
    context = {
        'appointments': upcoming_appointments,
        'page_title': 'Teleappointment Management'
    }
    
    return render(request, 'patients/teleappointment_management.html', context)