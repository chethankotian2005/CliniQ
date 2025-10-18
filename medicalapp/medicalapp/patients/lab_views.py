"""
Lab Management Views
Handles lab test browsing, booking, order tracking, and results viewing
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Count
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .lab_models import LabTest, LabOrder, LabResult
from .lab_facility_models import LabFacility, LabFacilityImage, LabFacilityReview, LabFacilityTestPrice
from .models import Patient
from doctors.models import Doctor

import json
from datetime import datetime, timedelta


# ============== Lab Facility Views ==============

def lab_facilities_list(request):
    """Display all available lab facilities for selection"""
    
    # Get all active lab facilities
    lab_facilities = LabFacility.objects.filter(is_active=True).prefetch_related('images', 'reviews')
    
    # Add sample data if no labs exist
    if not lab_facilities.exists():
        create_sample_lab_facilities()
        lab_facilities = LabFacility.objects.filter(is_active=True).prefetch_related('images', 'reviews')
    
    context = {
        'lab_facilities': lab_facilities,
        'total_labs': lab_facilities.count()
    }
    
    return render(request, 'patients/lab_facilities_list.html', context)


def lab_facility_detail(request, facility_id):
    """Lab facility detail page with available tests"""
    
    lab_facility = get_object_or_404(LabFacility, id=facility_id, is_active=True)
    
    # Get all tests available at this lab
    available_tests = LabTest.objects.filter(is_active=True)
    
    # Filter by lab capabilities
    test_categories = []
    if lab_facility.offers_blood_tests:
        test_categories.append('blood')
    if lab_facility.offers_urine_tests:
        test_categories.append('urine')
    if lab_facility.offers_imaging:
        test_categories.append('imaging')
    if lab_facility.offers_cardiology:
        test_categories.append('cardiology')
    if lab_facility.offers_pathology:
        test_categories.append('biopsy')
    if lab_facility.offers_microbiology:
        test_categories.append('culture')
    
    available_tests = available_tests.filter(category__in=test_categories)
    
    # Get custom pricing if available
    test_prices = LabFacilityTestPrice.objects.filter(
        lab_facility=lab_facility,
        is_available=True
    ).select_related('test')
    
    # Get reviews
    reviews = LabFacilityReview.objects.filter(
        lab_facility=lab_facility,
        is_verified=True
    )[:10]
    
    context = {
        'lab_facility': lab_facility,
        'available_tests': available_tests,
        'test_prices': test_prices,
        'reviews': reviews,
        'categories': lab_facility.get_test_categories(),
        'total_tests': available_tests.count()
    }
    
    return render(request, 'patients/lab_facility_detail.html', context)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_nearby_labs(request):
    """Get lab facilities sorted by distance from user location"""
    
    try:
        data = request.data
        user_lat = float(data.get('latitude', 0))
        user_lng = float(data.get('longitude', 0))
        
        labs = LabFacility.objects.filter(is_active=True)
        lab_data = []
        
        for lab in labs:
            distance = lab.get_distance_from(user_lat, user_lng)
            lab_data.append({
                'id': str(lab.id),
                'name': lab.name,
                'brand_name': lab.brand_name,
                'address': lab.address,
                'city': lab.city,
                'phone': lab.phone,
                'distance': distance,
                'rating': float(lab.rating),
                'tests_count': lab.get_available_tests_count(),
                'home_sample_collection': lab.home_sample_collection,
                'is_24_hours': lab.is_24_hours,
                'categories': lab.get_test_categories(),
                'discount_percentage': float(lab.discount_percentage) if lab.discount_percentage else 0,
                'image_url': lab.images.filter(is_primary=True).first().image.url if lab.images.filter(is_primary=True).exists() else None
            })
        
        # Sort by distance
        lab_data.sort(key=lambda x: x['distance'] if x['distance'] else float('inf'))
        
        return Response({
            'success': True,
            'labs': lab_data
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error: {str(e)}'
        }, status=500)


def create_sample_lab_facilities():
    """Create sample lab facilities for testing"""
    
    labs_data = [
        {
            'name': 'Central Lab - Downtown',
            'brand_name': 'Dr. Lal PathLabs',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'address': '123 MG Road, Andheri West, Mumbai',
            'zip_code': '400053',
            'phone': '+91 22 1234 5678',
            'email': 'downtown@lalpathlab.com',
            'latitude': 19.1136,
            'longitude': 72.8697,
            'offers_blood_tests': True,
            'offers_urine_tests': True,
            'offers_imaging': True,
            'offers_cardiology': True,
            'offers_pathology': True,
            'offers_microbiology': True,
            'home_sample_collection': True,
            'discount_percentage': 15,
            'accreditation': 'NABL, CAP, ISO 9001:2015',
            'description': 'Full-service diagnostic center with state-of-the-art equipment',
        },
        {
            'name': 'Express Diagnostics',
            'brand_name': 'SRL Diagnostics',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'address': '456 Linking Road, Bandra West, Mumbai',
            'zip_code': '400050',
            'phone': '+91 22 9876 5432',
            'email': 'bandra@srldiagnostics.com',
            'latitude': 19.0596,
            'longitude': 72.8295,
            'offers_blood_tests': True,
            'offers_urine_tests': True,
            'offers_imaging': False,
            'offers_cardiology': False,
            'offers_pathology': True,
            'offers_microbiology': True,
            'home_sample_collection': True,
            'discount_percentage': 20,
            'is_24_hours': True,
            'accreditation': 'NABL, ISO 9001:2015',
            'description': '24/7 lab services with home collection available',
        },
        {
            'name': 'City Imaging Center',
            'brand_name': 'Thyrocare',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'address': '789 SV Road, Goregaon East, Mumbai',
            'zip_code': '400063',
            'phone': '+91 22 5555 6666',
            'email': 'goregaon@thyrocare.com',
            'latitude': 19.1663,
            'longitude': 72.8526,
            'offers_blood_tests': True,
            'offers_urine_tests': True,
            'offers_imaging': True,
            'offers_cardiology': True,
            'offers_pathology': False,
            'offers_microbiology': True,
            'home_sample_collection': True,
            'discount_percentage': 10,
            'accreditation': 'NABL',
            'description': 'Specialized in imaging and cardiac diagnostics',
        },
    ]
    
    for lab_data in labs_data:
        LabFacility.objects.get_or_create(
            name=lab_data['name'],
            city=lab_data['city'],
            defaults=lab_data
        )
    
    print(f"Created {len(labs_data)} sample lab facilities")


@login_required
def lab_list_view(request):
    """Display all available lab tests grouped by category"""
    
    # Get all active lab tests
    lab_tests = LabTest.objects.filter(is_active=True).order_by('category', 'name')
    
    # Group by category
    tests_by_category = {}
    for test in lab_tests:
        category = test.get_category_display()
        if category not in tests_by_category:
            tests_by_category[category] = []
        tests_by_category[category].append(test)
    
    context = {
        'tests_by_category': tests_by_category,
        'total_tests': lab_tests.count(),
    }
    
    return render(request, 'patients/lab_list.html', context)


@login_required
def lab_booking_view(request, test_id, facility_id=None):
    """Handle lab test booking at a specific facility"""
    
    lab_test = get_object_or_404(LabTest, id=test_id, is_active=True)
    
    # Get selected lab facility if provided
    lab_facility = None
    custom_price = None
    if facility_id:
        lab_facility = get_object_or_404(LabFacility, id=facility_id, is_active=True)
        # Check for custom pricing
        try:
            custom_price = LabFacilityTestPrice.objects.get(
                lab_facility=lab_facility,
                test=lab_test,
                is_available=True
            )
        except LabFacilityTestPrice.DoesNotExist:
            pass
    
    if request.method == 'POST':
        try:
            # Get patient
            patient = get_object_or_404(Patient, user=request.user)
            
            # Get booking details
            scheduled_date_str = request.POST.get('scheduled_date')
            scheduled_time = request.POST.get('scheduled_time')
            priority = request.POST.get('priority', 'routine')
            clinical_notes = request.POST.get('clinical_notes', '')
            facility_id_post = request.POST.get('facility_id')
            home_collection = request.POST.get('home_collection') == 'true'
            
            # Parse scheduled datetime
            scheduled_datetime = datetime.strptime(
                f"{scheduled_date_str} {scheduled_time}", 
                "%Y-%m-%d %H:%M"
            )
            
            # Get lab facility for booking
            selected_facility = None
            if facility_id_post:
                selected_facility = LabFacility.objects.get(id=facility_id_post)
            
            # Create lab order
            lab_order = LabOrder.objects.create(
                patient=patient,
                test=lab_test,
                ordered_by=None,  # Self-booking, can be assigned doctor later
                status='ordered',
                priority=priority,
                scheduled_date=scheduled_datetime,
                clinical_notes=clinical_notes
            )
            
            # Store facility info in clinical notes if selected
            if selected_facility:
                lab_order.clinical_notes += f"\n[Lab: {selected_facility.name}]"
                if home_collection:
                    lab_order.clinical_notes += "\n[Home Collection Requested]"
                lab_order.save()
            
            # Send confirmation (can integrate with SMS service)
            # TODO: Add SMS/Email notification
            
            return JsonResponse({
                'success': True,
                'message': f'Lab test "{lab_test.name}" booked successfully!',
                'order_id': lab_order.id,
                'scheduled_date': scheduled_datetime.strftime('%Y-%m-%d %H:%M'),
                'facility': selected_facility.name if selected_facility else 'Default'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Booking failed: {str(e)}'
            }, status=400)
    
    # GET request - show booking form
    # Get all available facilities for this test
    available_facilities = LabFacility.objects.filter(is_active=True)
    
    # Filter by test category
    category_field_map = {
        'blood': 'offers_blood_tests',
        'urine': 'offers_urine_tests',
        'imaging': 'offers_imaging',
        'cardiology': 'offers_cardiology',
        'biopsy': 'offers_pathology',
        'culture': 'offers_microbiology',
    }
    
    if lab_test.category in category_field_map:
        filter_dict = {category_field_map[lab_test.category]: True}
        available_facilities = available_facilities.filter(**filter_dict)
    
    context = {
        'lab_test': lab_test,
        'lab_facility': lab_facility,
        'custom_price': custom_price,
        'available_facilities': available_facilities,
        'min_date': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        'preparation_instructions': lab_test.preparation_instructions
    }
    
    return render(request, 'patients/lab_booking.html', context)


@login_required
def lab_orders_view(request):
    """Display patient's lab orders (pending and completed)"""
    
    try:
        patient = get_object_or_404(Patient, user=request.user)
        
        # Get all orders for the patient
        orders = LabOrder.objects.filter(patient=patient).select_related(
            'test', 'ordered_by'
        ).order_by('-ordered_date')
        
        # Separate pending and completed
        pending_orders = orders.filter(
            status__in=['ordered', 'scheduled', 'sample_collected', 'in_progress']
        )
        completed_orders = orders.filter(status='completed')
        cancelled_orders = orders.filter(status='cancelled')
        
        context = {
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'total_orders': orders.count()
        }
        
        return render(request, 'patients/lab_orders.html', context)
        
    except Patient.DoesNotExist:
        return render(request, 'patients/error.html', {
            'message': 'Patient profile not found. Please contact support.'
        })


@login_required
def lab_results_view(request, order_id=None):
    """Display lab results for a specific order or all results"""
    
    try:
        patient = get_object_or_404(Patient, user=request.user)
        
        if order_id:
            # Show specific result
            order = get_object_or_404(
                LabOrder, 
                id=order_id, 
                patient=patient,
                status='completed'
            )
            
            try:
                result = LabResult.objects.get(order=order)
                
                context = {
                    'order': order,
                    'result': result,
                    'is_critical': result.status == 'critical',
                    'is_abnormal': result.status == 'abnormal'
                }
                
                return render(request, 'patients/lab_result_detail.html', context)
                
            except LabResult.DoesNotExist:
                return render(request, 'patients/error.html', {
                    'message': 'Lab result not available yet. Please check back later.'
                })
        
        else:
            # Show all results
            completed_orders = LabOrder.objects.filter(
                patient=patient,
                status='completed'
            ).select_related('test').order_by('-completed_date')
            
            # Get results for completed orders
            results = []
            for order in completed_orders:
                try:
                    result = LabResult.objects.get(order=order)
                    results.append({
                        'order': order,
                        'result': result
                    })
                except LabResult.DoesNotExist:
                    continue
            
            context = {
                'results': results,
                'total_results': len(results)
            }
            
            return render(request, 'patients/lab_results_list.html', context)
            
    except Patient.DoesNotExist:
        return render(request, 'patients/error.html', {
            'message': 'Patient profile not found. Please contact support.'
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_lab_order(request, order_id):
    """Cancel a lab order (only if not yet sample collected)"""
    
    try:
        patient = get_object_or_404(Patient, user=request.user)
        order = get_object_or_404(LabOrder, id=order_id, patient=patient)
        
        # Check if cancellation is allowed
        if order.status in ['sample_collected', 'in_progress', 'completed']:
            return Response({
                'success': False,
                'message': 'Cannot cancel order - sample already collected or processing started'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update order status
        order.status = 'cancelled'
        order.save()
        
        return Response({
            'success': True,
            'message': 'Lab order cancelled successfully'
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Cancellation failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reschedule_lab_order(request, order_id):
    """Reschedule a lab order"""
    
    try:
        patient = get_object_or_404(Patient, user=request.user)
        order = get_object_or_404(LabOrder, id=order_id, patient=patient)
        
        # Check if rescheduling is allowed
        if order.status not in ['ordered', 'scheduled']:
            return Response({
                'success': False,
                'message': 'Cannot reschedule - order already in progress'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get new scheduled date
        new_date_str = request.data.get('scheduled_date')
        new_time = request.data.get('scheduled_time')
        
        if not new_date_str or not new_time:
            return Response({
                'success': False,
                'message': 'Please provide both date and time'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse new datetime
        new_datetime = datetime.strptime(
            f"{new_date_str} {new_time}",
            "%Y-%m-%d %H:%M"
        )
        
        # Update order
        order.scheduled_date = new_datetime
        order.status = 'scheduled'
        order.save()
        
        return Response({
            'success': True,
            'message': 'Lab order rescheduled successfully',
            'new_date': new_datetime.strftime('%Y-%m-%d %H:%M')
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Rescheduling failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_lab_result(request, order_id):
    """Generate PDF download of lab result"""
    
    try:
        patient = get_object_or_404(Patient, user=request.user)
        order = get_object_or_404(LabOrder, id=order_id, patient=patient, status='completed')
        result = get_object_or_404(LabResult, order=order)
        
        # TODO: Implement PDF generation
        # For now, return JSON data
        data = {
            'test_name': order.test.name,
            'patient_name': patient.name,
            'result_value': result.result_value,
            'reference_range': result.reference_range,
            'unit': result.unit,
            'status': result.get_status_display(),
            'interpretation': result.interpretation,
            'completed_date': order.completed_date.strftime('%Y-%m-%d'),
            'verified_by': result.verified_by.name if result.verified_by else 'Pending',
            'verified_date': result.verified_date.strftime('%Y-%m-%d') if result.verified_date else 'Pending'
        }
        
        return Response(data)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Download failed: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def lab_stats(request):
    """Get patient's lab statistics for dashboard"""
    
    try:
        patient = get_object_or_404(Patient, user=request.user)
        
        # Count orders by status
        total_orders = LabOrder.objects.filter(patient=patient).count()
        pending_orders = LabOrder.objects.filter(
            patient=patient,
            status__in=['ordered', 'scheduled', 'sample_collected', 'in_progress']
        ).count()
        completed_orders = LabOrder.objects.filter(
            patient=patient,
            status='completed'
        ).count()
        
        # Count new results (completed in last 7 days)
        seven_days_ago = timezone.now() - timedelta(days=7)
        new_results = LabOrder.objects.filter(
            patient=patient,
            status='completed',
            completed_date__gte=seven_days_ago
        ).count()
        
        # Get critical results
        critical_results = LabResult.objects.filter(
            order__patient=patient,
            status='critical'
        ).count()
        
        return Response({
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'new_results': new_results,
            'critical_results': critical_results
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Failed to fetch stats: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Search and Filter Functions
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_lab_tests(request):
    """Search lab tests by name or category"""
    
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    tests = LabTest.objects.filter(is_active=True)
    
    if query:
        tests = tests.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    if category:
        tests = tests.filter(category=category)
    
    results = []
    for test in tests:
        results.append({
            'id': test.id,
            'name': test.name,
            'category': test.get_category_display(),
            'price': str(test.price),
            'duration_minutes': test.duration_minutes,
            'preparation_required': test.preparation_required
        })
    
    return Response(results)
