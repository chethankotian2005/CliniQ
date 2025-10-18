from django.contrib import admin
from .models import Patient, Department, Queue, PatientFeedback
from .lab_models import LabTest, LabOrder, LabResult
from .lab_facility_models import LabFacility, LabFacilityImage, LabFacilityReview, LabFacilityTestPrice

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at', 'get_waiting_count']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    def get_waiting_count(self, obj):
        return obj.get_waiting_count()
    get_waiting_count.short_description = 'Current Waiting'

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone_number', 'email', 'age', 'gender', 'created_at', 'is_active']
    list_filter = ['gender', 'is_active', 'created_at']
    search_fields = ['name', 'phone_number', 'email', 'medical_record_number']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ['token_number', 'patient', 'department', 'status', 'priority', 'created_at', 'assigned_doctor']
    list_filter = ['status', 'priority', 'department', 'created_at']
    search_fields = ['patient__name', 'patient__phone_number', 'token_number']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'actual_wait_time']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'department', 'assigned_doctor')

@admin.register(PatientFeedback)
class PatientFeedbackAdmin(admin.ModelAdmin):
    list_display = ['queue_entry', 'rating', 'wait_time_satisfaction', 'doctor_satisfaction', 'created_at']
    list_filter = ['rating', 'wait_time_satisfaction', 'doctor_satisfaction', 'created_at']
    search_fields = ['queue_entry__patient__name', 'feedback_text']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


# Lab Management Admin
@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'duration_minutes', 'preparation_required', 'is_active']
    list_filter = ['category', 'is_active', 'preparation_required']
    search_fields = ['name', 'description']
    ordering = ['category', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'description', 'is_active')
        }),
        ('Pricing & Duration', {
            'fields': ('price', 'duration_minutes')
        }),
        ('Preparation Instructions', {
            'fields': ('preparation_required', 'preparation_instructions')
        }),
    )


@admin.register(LabOrder)
class LabOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'test', 'status', 'priority', 'ordered_date', 'scheduled_date', 'ordered_by']
    list_filter = ['status', 'priority', 'ordered_date', 'scheduled_date']
    search_fields = ['patient__name', 'test__name', 'patient__phone_number']
    ordering = ['-ordered_date']
    readonly_fields = ['ordered_date']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('patient', 'test', 'ordered_by', 'status', 'priority')
        }),
        ('Scheduling', {
            'fields': ('ordered_date', 'scheduled_date', 'sample_collected_date', 'completed_date')
        }),
        ('Clinical Notes', {
            'fields': ('clinical_notes',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('patient', 'test', 'ordered_by')


@admin.register(LabResult)
class LabResultAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'result_value', 'reference_range', 'verified_by', 'verified_date']
    list_filter = ['status', 'verified_date']
    search_fields = ['order__patient__name', 'order__test__name']
    ordering = ['-verified_date']
    readonly_fields = ['verified_date']
    
    fieldsets = (
        ('Test Information', {
            'fields': ('order',)
        }),
        ('Results', {
            'fields': ('result_value', 'reference_range', 'unit', 'status')
        }),
        ('Interpretation', {
            'fields': ('interpretation', 'attachments')
        }),
        ('Verification', {
            'fields': ('verified_by', 'verified_date')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order__patient', 'order__test', 'verified_by')


# Lab Facility Admin
@admin.register(LabFacility)
class LabFacilityAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand_name', 'city', 'rating', 'is_verified', 'is_active', 'home_sample_collection']
    list_filter = ['is_active', 'is_verified', 'city', 'state', 'home_sample_collection', 'is_24_hours']
    search_fields = ['name', 'brand_name', 'city', 'phone', 'email']
    ordering = ['-is_verified', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'brand_name', 'is_active', 'is_verified')
        }),
        ('Contact Details', {
            'fields': ('address', 'city', 'state', 'zip_code', 'phone', 'email', 'website')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Lab Details', {
            'fields': ('description', 'established_year', 'accreditation', 'average_turnaround_hours', 'discount_percentage')
        }),
        ('Services Offered', {
            'fields': ('home_sample_collection', 'online_reports', 'emergency_services')
        }),
        ('Test Categories', {
            'fields': ('offers_blood_tests', 'offers_urine_tests', 'offers_imaging', 'offers_cardiology', 'offers_pathology', 'offers_microbiology')
        }),
        ('Operating Hours', {
            'fields': ('opens_at', 'closes_at', 'is_24_hours')
        }),
        ('Rating', {
            'fields': ('rating', 'total_reviews')
        }),
    )


@admin.register(LabFacilityImage)
class LabFacilityImageAdmin(admin.ModelAdmin):
    list_display = ['lab_facility', 'title', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['lab_facility__name', 'title']
    ordering = ['-is_primary', '-created_at']


@admin.register(LabFacilityReview)
class LabFacilityReviewAdmin(admin.ModelAdmin):
    list_display = ['lab_facility', 'patient_name', 'rating', 'is_verified', 'created_at']
    list_filter = ['rating', 'is_verified', 'created_at']
    search_fields = ['lab_facility__name', 'patient_name', 'comment']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(LabFacilityTestPrice)
class LabFacilityTestPriceAdmin(admin.ModelAdmin):
    list_display = ['test', 'lab_facility', 'price', 'discounted_price', 'is_available', 'home_collection_available']
    list_filter = ['is_available', 'home_collection_available', 'lab_facility']
    search_fields = ['test__name', 'lab_facility__name']
    ordering = ['test__name', 'price']
    
    fieldsets = (
        ('Test & Facility', {
            'fields': ('lab_facility', 'test', 'is_available')
        }),
        ('Pricing', {
            'fields': ('price', 'discounted_price')
        }),
        ('Service Details', {
            'fields': ('turnaround_hours', 'home_collection_available', 'home_collection_charge')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('lab_facility', 'test')
