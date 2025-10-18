from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from .hospital_models import Hospital

# Import lab models so they are registered with Django
from .lab_models import LabTest, LabOrder, LabResult
from .lab_facility_models import LabFacility, LabFacilityImage, LabFacilityReview, LabFacilityTestPrice

class Department(models.Model):
    name = models.CharField(max_length=100)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='departments', null=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['name', 'hospital']
    
    def __str__(self):
        if self.hospital:
            return f"{self.name} - {self.hospital.name}"
        return self.name
    
    def get_current_token_number(self):
        """Get the next token number for this department today"""
        today = timezone.now().date()
        last_token = Queue.objects.filter(
            department=self,
            created_at__date=today
        ).order_by('-token_number').first()
        
        return (last_token.token_number + 1) if last_token else 1
    
    def get_waiting_count(self):
        """Get count of patients waiting in queue"""
        return Queue.objects.filter(
            department=self,
            status='waiting',
            created_at__date=timezone.now().date()
        ).count()

class Patient(models.Model):
    # Basic Information
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(blank=True, null=True)
    age = models.IntegerField(null=True, blank=True)
    gender_choices = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    ]
    gender = models.CharField(max_length=1, choices=gender_choices, blank=True)
    
    # Medical Information
    medical_record_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    address = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=15, blank=True)
    
    # System Information
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.phone_number}"
    
    def get_current_queue_entry(self):
        """Get patient's current queue entry for today"""
        today = timezone.now().date()
        return Queue.objects.filter(
            patient=self,
            created_at__date=today,
            status__in=['waiting', 'called', 'in_consultation']
        ).first()

class Queue(models.Model):
    STATUS_CHOICES = [
        ('booked', 'Booked Online'),  # NEW: Patient booked from home
        ('arrived', 'Arrived at Hospital'),  # NEW: Scanned QR at reception
        ('waiting', 'Waiting'),
        ('called', 'Called'),
        ('in_consultation', 'In Consultation'),
        ('completed', 'Completed'),
        ('skipped', 'Skipped'),
        ('late_entry', 'Late Entry'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low Priority'),
        ('normal', 'Normal Priority'),
        ('high', 'High Priority'),
        ('emergency', 'Emergency'),
    ]
    
    APPOINTMENT_TYPE_CHOICES = [
        ('in_person', 'In-Person Appointment'),
        ('telemedicine', 'Telemedicine Appointment'),
    ]
    
    # Core Information
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    token_number = models.IntegerField()
    
    # Booking Information (NEW)
    is_online_booking = models.BooleanField(default=False, help_text="True if booked online from home")
    qr_code = models.CharField(max_length=100, unique=True, null=True, blank=True, help_text="Unique QR code for this booking")
    booked_at = models.DateTimeField(null=True, blank=True, help_text="When booking was made online")
    arrived_at = models.DateTimeField(null=True, blank=True, help_text="When patient arrived and scanned QR")
    preferred_doctor = models.ForeignKey('doctors.Doctor', on_delete=models.SET_NULL, null=True, blank=True, related_name='preferred_bookings', help_text="Doctor requested by patient")
    booking_date = models.DateField(null=True, blank=True, help_text="Date for which booking was made")
    booking_time_slot = models.CharField(max_length=20, null=True, blank=True, help_text="Preferred time slot")
    
    # Status Information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='waiting')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    appointment_type = models.CharField(max_length=20, choices=APPOINTMENT_TYPE_CHOICES, default='in_person', help_text="Type of appointment - in-person or telemedicine")
    
    # Timing Information
    created_at = models.DateTimeField(auto_now_add=True)  # When token was issued
    called_at = models.DateTimeField(null=True, blank=True)  # When patient was called
    consultation_started_at = models.DateTimeField(null=True, blank=True)
    consultation_ended_at = models.DateTimeField(null=True, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True, help_text="Additional notes about the visit")
    estimated_wait_time = models.IntegerField(null=True, blank=True, help_text="Estimated wait time in minutes")
    actual_wait_time = models.IntegerField(null=True, blank=True, help_text="Actual wait time in minutes")
    
    # Doctor assignment (will be linked later)
    assigned_doctor = models.ForeignKey('doctors.Doctor', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['created_at', 'token_number']
    
    def __str__(self):
        return f"Token {self.token_number} - {self.patient.name} ({self.department.name})"
    
    def save(self, *args, **kwargs):
        if not self.token_number:
            self.token_number = self.department.get_current_token_number()
        super().save(*args, **kwargs)
    
    def get_position_in_queue(self):
        """Get current position in the waiting queue"""
        if self.status != 'waiting':
            return 0
        
        return Queue.objects.filter(
            department=self.department,
            created_at__date=self.created_at.date(),
            status='waiting',
            created_at__lt=self.created_at
        ).count() + 1
    
    def calculate_estimated_wait_time(self):
        """Calculate estimated wait time based on queue position and average consultation time"""
        position = self.get_position_in_queue()
        if position <= 1:
            return 0
        
        # Get average consultation time for this department (default 15 minutes)
        from doctors.models import Doctor
        doctors_in_dept = Doctor.objects.filter(department=self.department, is_available=True)
        avg_consultation_time = 15  # minutes
        
        if doctors_in_dept.exists():
            # Calculate based on number of available doctors
            estimated_time = ((position - 1) * avg_consultation_time) // doctors_in_dept.count()
        else:
            estimated_time = (position - 1) * avg_consultation_time
        
        self.estimated_wait_time = estimated_time
        self.save(update_fields=['estimated_wait_time'])
        return estimated_time
    
    def mark_as_called(self):
        """Mark patient as called"""
        self.status = 'called'
        self.called_at = timezone.now()
        self.save(update_fields=['status', 'called_at'])
    
    def start_consultation(self, doctor=None):
        """Start consultation"""
        self.status = 'in_consultation'
        self.consultation_started_at = timezone.now()
        if doctor:
            self.assigned_doctor = doctor
        if self.called_at:
            self.actual_wait_time = int((self.consultation_started_at - self.created_at).total_seconds() / 60)
        self.save()
    
    def complete_consultation(self):
        """Complete consultation"""
        self.status = 'completed'
        self.consultation_ended_at = timezone.now()
        self.save(update_fields=['status', 'consultation_ended_at'])

class PatientFeedback(models.Model):
    queue_entry = models.OneToOneField(Queue, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], help_text="Rating from 1 to 5")
    feedback_text = models.TextField(blank=True)
    wait_time_satisfaction = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    doctor_satisfaction = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    overall_experience = models.IntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback for {self.queue_entry.patient.name} - Rating: {self.rating}"

class TeleAppointment(models.Model):
    """
    Model to handle telemedicine-specific data for appointments
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ready', 'Ready to Start'),
        ('in_progress', 'Video Call in Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'Patient No Show'),
        ('technical_issue', 'Technical Issue'),
    ]
    
    # Core relationship
    queue_entry = models.OneToOneField(Queue, on_delete=models.CASCADE, related_name='tele_appointment')
    
    # Video call details
    meeting_url = models.URLField(blank=True, null=True, help_text="Video call meeting URL")
    meeting_id = models.CharField(max_length=100, blank=True, null=True, help_text="Meeting ID for the video call")
    meeting_password = models.CharField(max_length=50, blank=True, null=True, help_text="Meeting password if required")
    
    # Platform details
    platform_choices = [
        ('zoom', 'Zoom'),
        ('google_meet', 'Google Meet'),
        ('microsoft_teams', 'Microsoft Teams'),
        ('webrtc', 'WebRTC (Browser-based)'),
        ('other', 'Other'),
    ]
    platform = models.CharField(max_length=20, choices=platform_choices, default='webrtc')
    
    # Timing information
    scheduled_start_time = models.DateTimeField(help_text="Scheduled start time for the video call")
    actual_start_time = models.DateTimeField(null=True, blank=True)
    actual_end_time = models.DateTimeField(null=True, blank=True)
    
    # Technical requirements
    patient_device_info = models.JSONField(default=dict, blank=True, help_text="Patient's device and browser info")
    connection_quality = models.CharField(max_length=20, choices=[
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ], null=True, blank=True)
    
    # Communication
    pre_call_instructions = models.TextField(default="Please ensure you have a stable internet connection and are in a quiet, private space for your appointment.", help_text="Instructions sent to patient before the call")
    technical_notes = models.TextField(blank=True, help_text="Technical notes or issues during the call")
    
    # Notifications
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    meeting_link_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Status tracking
    tele_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_start_time']
    
    def __str__(self):
        return f"TeleAppointment: {self.queue_entry.patient.name} - {self.scheduled_start_time.strftime('%Y-%m-%d %H:%M')}"
    
    def is_ready_to_start(self):
        """Check if the appointment is ready to start"""
        if self.tele_status != 'scheduled':
            return False
        
        now = timezone.now()
        # Allow starting 15 minutes before scheduled time
        start_window = self.scheduled_start_time - timedelta(minutes=15)
        # Don't allow starting more than 30 minutes after scheduled time
        end_window = self.scheduled_start_time + timedelta(minutes=30)
        
        return start_window <= now <= end_window
    
    def get_meeting_duration(self):
        """Get the duration of the meeting in minutes"""
        if self.actual_start_time and self.actual_end_time:
            duration = self.actual_end_time - self.actual_start_time
            return int(duration.total_seconds() / 60)
        return None
    
    def start_meeting(self):
        """Start the telemedicine meeting"""
        self.tele_status = 'in_progress'
        self.actual_start_time = timezone.now()
        self.save(update_fields=['tele_status', 'actual_start_time'])
        
        # Also update the main queue entry
        self.queue_entry.start_consultation()
    
    def end_meeting(self):
        """End the telemedicine meeting"""
        self.tele_status = 'completed'
        self.actual_end_time = timezone.now()
        self.save(update_fields=['tele_status', 'actual_end_time'])
        
        # Also update the main queue entry
        self.queue_entry.complete_consultation()
