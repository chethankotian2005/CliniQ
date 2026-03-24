"""
Hospital selection and patient portal views
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db.utils import DatabaseError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import json
from geopy.distance import geodesic
import logging

from .hospital_models import Hospital, HospitalReview, HospitalImage
from .models import Department
from .chatbot_service import MedicalChatbotService

logger = logging.getLogger(__name__)

def patient_portal_home(request):
    """Patient portal homepage with hospital selection"""
    try:
        # Get all active hospitals
        hospitals = Hospital.objects.filter(is_active=True).prefetch_related('images', 'departments')

        # Add sample data if no hospitals exist
        if not hospitals.exists():
            create_sample_hospitals()
            hospitals = Hospital.objects.filter(is_active=True).prefetch_related('images', 'departments')

        return render(request, 'patients/portal_home.html', {
            'hospitals': hospitals
        })
    except DatabaseError as exc:
        # Avoid crashing the portal page when production DB/migrations are not ready.
        logger.exception("Portal load failed due to database error: %s", exc)
        return render(request, 'patients/portal_home.html', {
            'hospitals': []
        })
    except Exception as exc:
        logger.exception("Portal load failed unexpectedly: %s", exc)
        return render(request, 'patients/portal_home.html', {
            'hospitals': []
        })

def hospital_detail(request, hospital_id):
    """Hospital detail page with departments and booking"""
    hospital = get_object_or_404(Hospital, id=hospital_id, is_active=True)
    departments = Department.objects.filter(hospital=hospital, is_active=True)
    reviews = HospitalReview.objects.filter(hospital=hospital, is_verified=True)[:5]
    
    return render(request, 'patients/hospital_detail.html', {
        'hospital': hospital,
        'departments': departments,
        'reviews': reviews
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def get_nearby_hospitals(request):
    """Get hospitals sorted by distance from user location"""
    try:
        data = request.data
        user_lat = float(data.get('latitude', 0))
        user_lng = float(data.get('longitude', 0))
        
        hospitals = Hospital.objects.filter(is_active=True)
        hospital_data = []
        
        for hospital in hospitals:
            distance = hospital.get_distance_from(user_lat, user_lng)
            hospital_data.append({
                'id': str(hospital.id),
                'name': hospital.name,
                'address': hospital.address,
                'city': hospital.city,
                'phone': hospital.phone,
                'distance': distance,
                'rating': float(hospital.rating),
                'departments_count': hospital.get_departments_count(),
                'emergency_services': hospital.emergency_services,
                'is_24_hours': hospital.is_24_hours,
                'image_url': hospital.images.filter(is_primary=True).first().image.url if hospital.images.filter(is_primary=True).exists() else None
            })
        
        # Sort by distance
        hospital_data.sort(key=lambda x: x['distance'] if x['distance'] else float('inf'))
        
        return Response({
            'success': True,
            'hospitals': hospital_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)

class ChatbotView(View):
    """Handle chatbot conversations"""
    
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').strip()
            conversation_history = data.get('history', [])
            
            if not user_message:
                return JsonResponse({
                    'success': False,
                    'message': 'Message is required'
                }, status=400)
            
            # Initialize chatbot service
            try:
                chatbot = MedicalChatbotService()
            except Exception as init_error:
                print(f"🤖 Chatbot initialization error: {init_error}")
                return JsonResponse({
                    'success': False,
                    'response': f'Chatbot service initialization failed: {str(init_error)}',
                    'error': 'initialization_failed'
                }, status=500)
            
            # Get response
            response_data = chatbot.get_chat_response(user_message, conversation_history)
            
            # Add department recommendations if relevant
            if response_data.get('type') == 'symptoms':
                recommendations = chatbot.get_department_recommendations(user_message)
                response_data['department_recommendations'] = recommendations
            
            return JsonResponse(response_data)
            
        except Exception as e:
            # Log detailed error for debugging
            print(f"🚨 Chatbot API Error:")
            print(f"   Error Type: {type(e).__name__}")
            print(f"   Error Message: {str(e)}")
            print(f"   User Message: {user_message}")
            
            # Check for specific error types
            error_str = str(e).lower()
            if 'gemini_api_key' in error_str or 'api_key' in error_str:
                error_response = 'API key configuration error. Please check Gemini API setup.'
            elif 'quota' in error_str or 'billing' in error_str:
                error_response = 'API quota exceeded. Please check your Google Cloud billing.'
            elif 'network' in error_str or 'connection' in error_str:
                error_response = 'Network connection issue. Please check your internet connection.'
            else:
                error_response = f'I apologize, but I\'m experiencing technical difficulties: {str(e)}. Please try again later.'
            
            return JsonResponse({
                'success': False,
                'message': f'Error: {str(e)}',
                'response': error_response,
                'error_type': type(e).__name__
            }, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_hospital_departments(request, hospital_id):
    """Get departments for a specific hospital"""
    try:
        hospital = Hospital.objects.get(id=hospital_id, is_active=True)
        # Ensure departments are unique by id to prevent duplicates
        departments = Department.objects.filter(hospital=hospital, is_active=True).order_by('id')
        
        department_data = []
        seen = set()
        for dept in departments:
            if dept.id in seen:
                continue
            seen.add(dept.id)
            department_data.append({
                'id': dept.id,
                'name': dept.name,
                'description': dept.description,
                'waiting_count': dept.get_waiting_count(),
                'current_token': dept.get_current_token_number() - 1
            })
        
        return Response({
            'success': True,
            'hospital': {
                'id': str(hospital.id),
                'name': hospital.name,
                'address': hospital.address
            },
            'departments': department_data
        })
        
    except Hospital.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Hospital not found'
        }, status=404)
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)

def create_sample_hospitals():
    """Create sample hospital data for demonstration"""
    sample_hospitals = [
        {
            'name': 'City General Hospital',
            'address': '123 Main Street, Downtown',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'zip_code': '400001',
            'phone': '+91-22-1234-5678',
            'email': 'info@citygeneral.com',
            'latitude': 19.0760,
            'longitude': 72.8777,
            'description': 'A leading multi-specialty hospital with state-of-the-art facilities and experienced doctors.',
            'established_year': 1985,
            'total_beds': 500,
            'rating': 4.5,
            'total_reviews': 1250
        },
        {
            'name': 'Metro Medical Center',
            'address': '456 Health Avenue, Central',
            'city': 'Mumbai',
            'state': 'Maharashtra', 
            'zip_code': '400002',
            'phone': '+91-22-2345-6789',
            'email': 'contact@metromedical.com',
            'latitude': 19.0825,
            'longitude': 72.8811,
            'description': 'Modern healthcare facility specializing in cardiac care, orthopedics, and emergency services.',
            'established_year': 1998,
            'total_beds': 350,
            'rating': 4.3,
            'total_reviews': 890
        },
        {
            'name': 'Sunrise Specialty Hospital',
            'address': '789 Wellness Road, Suburbs',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'zip_code': '400003', 
            'phone': '+91-22-3456-7890',
            'email': 'help@sunrisehealth.com',
            'latitude': 19.1136,
            'longitude': 72.8697,
            'description': 'Premium healthcare with focus on women and child care, oncology, and neurology.',
            'established_year': 2005,
            'total_beds': 200,
            'rating': 4.7,
            'total_reviews': 567,
            'is_24_hours': True
        },
        {
            'name': 'Community Care Hospital',
            'address': '321 Care Street, Eastside',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'zip_code': '400004',
            'phone': '+91-22-4567-8901',
            'email': 'info@communitycare.com',
            'latitude': 19.0955,
            'longitude': 72.9074,
            'description': 'Affordable healthcare for the community with comprehensive medical services.',
            'established_year': 1992,
            'total_beds': 150,
            'rating': 4.1,
            'total_reviews': 723
        }
    ]
    
    for hospital_data in sample_hospitals:
        hospital, created = Hospital.objects.get_or_create(
            name=hospital_data['name'],
            defaults=hospital_data
        )
        
        if created:
            # Create sample departments for each hospital
            departments = [
                {'name': 'General Medicine', 'description': 'General health checkups and common illnesses'},
                {'name': 'Cardiology', 'description': 'Heart and cardiovascular care'},
                {'name': 'Orthopedics', 'description': 'Bone, joint, and muscle care'},
                {'name': 'Pediatrics', 'description': 'Child healthcare and vaccinations'},
                {'name': 'Gynecology', 'description': 'Women\'s health and maternity care'},
                {'name': 'Emergency', 'description': '24/7 emergency medical services'}
            ]
            
            for dept_data in departments:
                Department.objects.get_or_create(
                    name=dept_data['name'],
                    hospital=hospital,
                    defaults={'description': dept_data['description']}
                )