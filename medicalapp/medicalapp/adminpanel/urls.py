from django.urls import path
from . import views

app_name = 'adminpanel'

urlpatterns = [
    # Authentication
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    
    # Dashboard views
    path('', views.admin_dashboard, name='dashboard'),
    path('simple/', views.simple_admin_dashboard, name='simple_dashboard'),
    path('departments/', views.departments_management, name='departments'),
    path('doctors/', views.doctors_management, name='doctors'),
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('queue/', views.queue_management, name='queue'),
    path('notifications/', views.notifications_management, name='notifications'),
    path('qr-scanner/', views.admin_qr_scanner, name='qr_scanner'),
    
    # API endpoints
    path('api/', views.AdminApiView.as_view(), name='api'),
]