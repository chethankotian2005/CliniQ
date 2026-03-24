"""
Booking Views - Online booking and QR scanning
"""

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.utils import DatabaseError
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import json
import logging
from datetime import datetime, timedelta
from django.utils import timezone

from .models import Patient, Department, Queue
from .booking_service import BookingService
from doctors.models import Doctor

logger = logging.getLogger(__name__)


class OnlineBookingView(View):
    """Handle online booking creation"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            
            # Validate required fields
            required_fields = ['name', 'phone_number', 'department_id']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({
                        'success': False,
                        'message': f'{field} is required'
                    }, status=400)
            
            # Create booking
            booking_service = BookingService()
            result = booking_service.create_online_booking(
                patient_data=data,
                department_id=data['department_id'],
                doctor_id=data.get('doctor_id'),
                booking_date=data.get('booking_date'),
                time_slot=data.get('time_slot')
            )
            
            return JsonResponse(result, status=200 if result['success'] else 400)
            
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


class QRScanView(View):
    """Handle QR code scanning at hospital reception"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            qr_code = data.get('qr_code')
            
            if not qr_code:
                return JsonResponse({
                    'success': False,
                    'message': 'QR code is required'
                }, status=400)
            
            # Activate booking
            booking_service = BookingService()
            result = booking_service.activate_booking_by_qr(qr_code)
            
            return JsonResponse(result, status=200 if result['success'] else 400)
            
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
def get_booking_details(request, booking_id):
    """Get details of a specific booking"""
    try:
        booking_service = BookingService()
        result = booking_service.get_booking_details(booking_id)
        return Response(result)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@api_view(['POST'])
@permission_classes([AllowAny])
def cancel_booking(request, booking_id):
    """Cancel a booking"""
    try:
        booking_service = BookingService()
        result = booking_service.cancel_booking(booking_id)
        return Response(result)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_available_slots(request, department_id):
    """Get available time slots for a department"""
    try:
        date_str = request.GET.get('date')
        if date_str:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            date = timezone.now().date()
        
        booking_service = BookingService()
        result = booking_service.get_available_time_slots(department_id, date)
        return Response(result)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_department_doctors(request, department_id):
    """Get list of doctors in a department"""
    try:
        department = Department.objects.get(id=department_id, is_active=True)
        doctors = Doctor.objects.filter(department=department, is_available=True)
        
        doctor_list = []
        for doctor in doctors:
            doctor_list.append({
                'id': doctor.id,
                'name': doctor.name,
                'specialization': doctor.specialization,
                # Model field is `years_of_experience` — include it under that key
                'years_of_experience': doctor.years_of_experience,
                'is_on_duty': doctor.is_on_duty(),
            })
        
        return Response({
            'success': True,
            'doctors': doctor_list
        })
    except Department.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Department not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


def online_booking_page(request):
    """Online booking page template"""
    try:
        departments = Department.objects.filter(is_active=True)
        if not departments.exists():
            from .portal_views import create_sample_hospitals
            create_sample_hospitals()
            departments = Department.objects.filter(is_active=True)

        return render(request, 'patients/booking.html', {
            'departments': departments
        })
    except DatabaseError as exc:
        logger.exception("Booking page DB error: %s", exc)
        return render(request, 'patients/booking.html', {
            'departments': []
        })
    except Exception as exc:
        logger.exception("Booking page render error: %s", exc)
        return HttpResponse("Booking page is temporarily unavailable. Please retry in a moment.", status=503)

def hospital_booking_page(request, hospital_id):
    """Hospital-specific booking page"""
    from .hospital_models import Hospital
    hospital = get_object_or_404(Hospital, id=hospital_id, is_active=True)
    departments = Department.objects.filter(hospital=hospital, is_active=True)
    
    return render(request, 'patients/hospital_booking.html', {
        'hospital': hospital,
        'departments': departments
    })


def qr_scanner_page(request):
    """QR scanner page for hospital reception"""
    return render(request, 'patients/qr_scanner.html')


def booking_confirmation_page(request, booking_id):
    """Booking confirmation page with QR code"""
    booking = get_object_or_404(Queue, id=booking_id)
    
    # Generate QR code image (use existing QR code data if available)
    booking_service = BookingService()
    if booking.qr_code:
        # Use existing QR code data to regenerate image
        _, qr_code_image = booking_service.generate_booking_qr_code(booking.id, booking.qr_code)
    else:
        # Generate new QR code
        qr_code_data, qr_code_image = booking_service.generate_booking_qr_code(booking.id)
        booking.qr_code = qr_code_data
        booking.save()
    
    return render(request, 'patients/booking_confirmation.html', {
        'booking': booking,
        'qr_code_image': qr_code_image
    })


def patient_queue_view(request, booking_id):
    """Show patient's current queue position and estimated wait time"""
    booking = get_object_or_404(Queue, id=booking_id)
    
    # Get current queue position
    queue_position = Queue.objects.filter(
        department=booking.department,
        created_at__date=booking.created_at.date(),
        created_at__lt=booking.created_at,
        status__in=['waiting', 'called']
    ).count() + 1
    
    # Get total patients ahead
    patients_ahead = Queue.objects.filter(
        department=booking.department,
        created_at__date=booking.created_at.date(),
        created_at__lt=booking.created_at,
        status='waiting'
    ).count()
    
    # Calculate estimated wait time (assume 15 minutes per patient)
    estimated_wait_minutes = patients_ahead * 15
    estimated_wait_time = None
    if estimated_wait_minutes > 0:
        current_time = timezone.now()
        estimated_wait_time = current_time + timedelta(minutes=estimated_wait_minutes)
    
    # Get current token being served
    current_token = Queue.objects.filter(
        department=booking.department,
        created_at__date=booking.created_at.date(),
        status='called'
    ).first()
    
    return render(request, 'patients/patient_queue.html', {
        'booking': booking,
        'queue_position': queue_position,
        'patients_ahead': patients_ahead,
        'estimated_wait_time': estimated_wait_time,
        'current_token': current_token,
        'estimated_wait_minutes': estimated_wait_minutes
    })
