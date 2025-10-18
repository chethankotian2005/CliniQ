from django.urls import path
from . import views, booking_views, portal_views, lab_views, teleappointment_views

app_name = 'patients'

urlpatterns = [
    # Patient Portal URLs
    path('portal/', portal_views.patient_portal_home, name='portal_home'),
    path('hospital/<uuid:hospital_id>/', portal_views.hospital_detail, name='hospital_detail'),
    path('hospital/<uuid:hospital_id>/book/', booking_views.hospital_booking_page, name='hospital_booking'),
    
    # Lab Facility URLs (similar to hospital selection)
    path('lab-facilities/', lab_views.lab_facilities_list, name='lab_facilities_list'),
    path('lab-facility/<uuid:facility_id>/', lab_views.lab_facility_detail, name='lab_facility_detail'),
    
    # Lab URLs
    path('labs/', lab_views.lab_list_view, name='lab_list'),
    path('labs/book/<int:test_id>/', lab_views.lab_booking_view, name='lab_booking'),
    path('labs/book/<int:test_id>/facility/<uuid:facility_id>/', lab_views.lab_booking_view, name='lab_booking_with_facility'),
    path('labs/orders/', lab_views.lab_orders_view, name='lab_orders'),
    path('labs/results/', lab_views.lab_results_view, name='lab_results_list'),
    path('labs/results/<int:order_id>/', lab_views.lab_results_view, name='lab_result_detail'),
    
    # Lab API endpoints
    path('api/labs/nearby/', lab_views.get_nearby_labs, name='api_nearby_labs'),
    path('api/labs/stats/', lab_views.lab_stats, name='api_lab_stats'),
    path('api/labs/search/', lab_views.search_lab_tests, name='api_lab_search'),
    path('api/labs/order/<int:order_id>/cancel/', lab_views.cancel_lab_order, name='api_lab_cancel'),
    path('api/labs/order/<int:order_id>/reschedule/', lab_views.reschedule_lab_order, name='api_lab_reschedule'),
    path('api/labs/result/<int:order_id>/download/', lab_views.download_lab_result, name='api_lab_download'),
    
    # API endpoints
    path('api/departments/', views.get_departments, name='api_departments'),
    path('api/queue/<int:department_id>/', views.get_queue_status, name='api_queue_status'),
    path('api/patient/<int:patient_id>/status/', views.get_patient_status, name='api_patient_status'),
    path('api/check-patient/', views.check_patient_by_phone, name='api_check_patient'),
    path('api/feedback/', views.submit_feedback, name='api_feedback'),
    path('api/dashboard-stats/', views.dashboard_stats_api, name='api_dashboard_stats'),
    
    # Portal API endpoints
    path('api/nearby-hospitals/', portal_views.get_nearby_hospitals, name='api_nearby_hospitals'),
    path('api/chatbot/', portal_views.ChatbotView.as_view(), name='api_chatbot'),
    path('api/hospital/<uuid:hospital_id>/departments/', portal_views.get_hospital_departments, name='api_hospital_departments'),
    
    # Booking API endpoints
    path('api/booking/create/', booking_views.OnlineBookingView.as_view(), name='api_booking_create'),
    path('api/booking/<int:booking_id>/', booking_views.get_booking_details, name='api_booking_details'),
    path('api/booking/<int:booking_id>/cancel/', booking_views.cancel_booking, name='api_booking_cancel'),
    path('api/booking/qr-scan/', booking_views.QRScanView.as_view(), name='api_qr_scan'),
    path('api/booking/slots/<int:department_id>/', booking_views.get_available_slots, name='api_available_slots'),
    path('api/department/<int:department_id>/doctors/', booking_views.get_department_doctors, name='api_department_doctors'),
    
    # Teleappointment API endpoints
    path('api/teleappointment/book/', teleappointment_views.TeleAppointmentBookingView.as_view(), name='api_teleappointment_book'),
    path('api/teleappointment/<int:appointment_id>/', teleappointment_views.get_teleappointment_status, name='api_teleappointment_status'),
    path('api/teleappointment/patient/<str:phone_number>/', teleappointment_views.get_patient_teleappointments, name='api_patient_teleappointments'),
    path('api/teleappointment/start/', teleappointment_views.start_video_session, name='api_start_video_session'),
    path('api/teleappointment/end/', teleappointment_views.end_video_session, name='api_end_video_session'),
    path('api/teleappointment/reschedule/', teleappointment_views.reschedule_teleappointment, name='api_reschedule_teleappointment'),
    path('api/teleappointment/slots/<int:department_id>/', teleappointment_views.get_available_slots, name='api_teleappointment_slots'),
    
    # Template views  
    path('status/<int:patient_id>/', views.patient_status, name='status'),
    path('queue/<int:department_id>/', views.queue_display, name='queue_display'),
    path('feedback/<int:queue_id>/', views.feedback_form, name='feedback'),
    path('debug/', views.debug_page, name='debug'),
    
    # Booking template views
    path('booking/', booking_views.online_booking_page, name='booking'),
    path('booking/confirmation/<int:booking_id>/', booking_views.booking_confirmation_page, name='booking_confirmation'),
    path('queue/my-position/<int:booking_id>/', booking_views.patient_queue_view, name='patient_queue'),
    path('qr-scanner/', booking_views.qr_scanner_page, name='qr_scanner'),
    
    # Teleappointment template views
    path('teleappointment/', teleappointment_views.teleappointment_booking_page, name='teleappointment_booking'),
    path('video-call/<str:meeting_id>/', teleappointment_views.video_call_room, name='video_call_room'),
    path('teleappointment/management/', teleappointment_views.teleappointment_management, name='teleappointment_management'),
]