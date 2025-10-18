from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import json

from .models import Patient, Department, Queue, PatientFeedback
from .services import QueueService
from adminpanel.models import AuditLog

@api_view(['GET'])
@permission_classes([AllowAny])
def get_departments(request):
    """Get list of active departments"""
    try:
        # Fetch active departments and dedupe by (id) to avoid accidental duplicates
        departments = Department.objects.filter(is_active=True).order_by('id')
        department_list = []
        seen = set()

        for dept in departments:
            if dept.id in seen:
                continue
            seen.add(dept.id)
            department_list.append({
                'id': dept.id,
                'name': dept.name,
                'description': dept.description,
                'waiting_count': dept.get_waiting_count(),
                'current_token': dept.get_current_token_number() - 1  # Last issued token
            })
        
        return Response({
            'success': True,
            'departments': department_list
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error fetching departments: {str(e)}'
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_queue_status(request, department_id):
    """Get queue status for a department"""
    try:
        queue_service = QueueService()
        result = queue_service.get_queue_status(department_id)
        return Response(result)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error fetching queue status: {str(e)}'
        }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_patient_status(request, patient_id):
    """Get patient's current queue status"""
    try:
        queue_service = QueueService()
        result = queue_service.get_patient_status(patient_id)
        return Response(result)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error fetching patient status: {str(e)}'
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def check_patient_by_phone(request):
    """Check if patient exists by phone number"""
    try:
        phone_number = request.data.get('phone_number')
        if not phone_number:
            return Response({
                'success': False,
                'message': 'Phone number is required'
            }, status=400)
        
        # Get all patients with this phone number
        patients = Patient.objects.filter(phone_number=phone_number)
        
        if not patients.exists():
            return Response({
                'success': True,
                'exists': False,
                'patients': [],
                'message': 'No patients found with this phone number'
            })
        
        # Get patient data with recent bookings
        patient_data = []
        recent_booking = None
        
        for patient in patients:
            # Get most recent booking for this patient
            latest_booking = Queue.objects.filter(
                patient=patient,
                status__in=['booked', 'arrived', 'waiting', 'called', 'in_consultation']
            ).order_by('-created_at').first()
            
            patient_info = {
                'id': patient.id,
                'name': patient.name,
                'phone_number': patient.phone_number,
                'email': patient.email,
                'has_active_booking': bool(latest_booking),
                'latest_booking': {
                    'id': latest_booking.id,
                    'token_number': latest_booking.token_number,
                    'department': latest_booking.department.name,
                    'status': latest_booking.status,
                    'booking_date': latest_booking.booking_date.isoformat() if latest_booking.booking_date else None,
                    'created_at': latest_booking.created_at.isoformat()
                } if latest_booking else None
            }
            
            patient_data.append(patient_info)
            
            # Keep track of most recent booking across all patients
            if latest_booking and (not recent_booking or latest_booking.created_at > recent_booking.created_at):
                recent_booking = latest_booking
        
        return Response({
            'success': True,
            'exists': True,
            'patients': patient_data,
            'recent_booking': {
                'id': recent_booking.id,
                'patient_name': recent_booking.patient.name,
                'token_number': recent_booking.token_number,
                'department': recent_booking.department.name,
                'status': recent_booking.status,
            } if recent_booking else None
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error checking patient: {str(e)}'
        }, status=500)

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_feedback(request):
    """Submit patient feedback after consultation"""
    try:
        data = request.data
        queue_id = data.get('queue_id')
        
        if not queue_id:
            return Response({
                'success': False,
                'message': 'Queue ID is required'
            }, status=400)
        
        try:
            queue_entry = Queue.objects.get(id=queue_id, status='completed')
            
            # Check if feedback already exists
            if hasattr(queue_entry, 'patientfeedback'):
                return Response({
                    'success': False,
                    'message': 'Feedback already submitted for this consultation'
                }, status=400)
            
            # Create feedback
            feedback = PatientFeedback.objects.create(
                queue_entry=queue_entry,
                rating=data.get('rating', 5),
                feedback_text=data.get('feedback_text', ''),
                wait_time_satisfaction=data.get('wait_time_satisfaction'),
                doctor_satisfaction=data.get('doctor_satisfaction'),
                overall_experience=data.get('overall_experience')
            )
            
            return Response({
                'success': True,
                'message': 'Feedback submitted successfully',
                'feedback_id': feedback.id
            })
            
        except Queue.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Queue entry not found or consultation not completed'
            }, status=404)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error submitting feedback: {str(e)}'
        }, status=500)

# Template views for patient interface
def patient_status(request, patient_id):
    """Patient status page"""
    patient = get_object_or_404(Patient, id=patient_id)
    return render(request, 'patients/status.html', {
        'patient': patient
    })

def queue_display(request, department_id):
    """Public queue display for a department"""
    department = get_object_or_404(Department, id=department_id, is_active=True)
    return render(request, 'patients/queue_display.html', {
        'department': department
    })

def feedback_form(request, queue_id):
    """Feedback form after consultation"""
    queue_entry = get_object_or_404(Queue, id=queue_id, status='completed')
    return render(request, 'patients/feedback.html', {
        'queue_entry': queue_entry
    })

def debug_page(request):
    """Debug page for testing"""
    return render(request, 'patients/debug.html')

@api_view(['GET'])
@permission_classes([AllowAny])
def dashboard_stats_api(request):
    """Get dashboard statistics for admin"""
    from django.utils import timezone
    
    today = timezone.now().date()
    
    # Get today's statistics
    total_checkins = Queue.objects.filter(
        arrived_at__date=today
    ).count()
    
    current_waiting = Queue.objects.filter(
        status='waiting',
        created_at__date=today
    ).count()
    
    return Response({
        'success': True,
        'total_checkins': total_checkins,
        'current_waiting': current_waiting
    })
