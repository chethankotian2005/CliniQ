from django.db import models
from django.utils import timezone
from django.conf import settings

class LabTest(models.Model):
    """Available lab tests in the hospital"""
    TEST_CATEGORIES = [
        ('blood', 'Blood Tests'),
        ('urine', 'Urine Tests'),
        ('imaging', 'Imaging (X-Ray, CT, MRI)'),
        ('cardio', 'Cardiac Tests'),
        ('culture', 'Culture Tests'),
        ('biopsy', 'Biopsy'),
        ('other', 'Other Tests'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=TEST_CATEGORIES)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    preparation_required = models.TextField(blank=True, help_text="Special preparation needed (fasting, etc.)")
    duration_minutes = models.IntegerField(help_text="Approximate duration in minutes")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class LabOrder(models.Model):
    """Patient's lab test orders"""
    STATUS_CHOICES = [
        ('ordered', 'Ordered'),
        ('scheduled', 'Scheduled'),
        ('sample_collected', 'Sample Collected'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PRIORITY_CHOICES = [
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('stat', 'STAT (Immediate)'),
    ]
    
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='lab_orders')
    test = models.ForeignKey(LabTest, on_delete=models.CASCADE)
    ordered_by = models.ForeignKey('doctors.Doctor', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey('patients.Department', on_delete=models.SET_NULL, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='routine')
    
    # Dates and Times
    ordered_date = models.DateTimeField(default=timezone.now)
    scheduled_date = models.DateTimeField(null=True, blank=True)
    sample_collected_date = models.DateTimeField(null=True, blank=True)
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Notes and Instructions
    clinical_notes = models.TextField(blank=True, help_text="Clinical indication for test")
    special_instructions = models.TextField(blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-ordered_date']
    
    def __str__(self):
        return f"{self.patient.name} - {self.test.name} ({self.get_status_display()})"
    
    def is_result_ready(self):
        return self.status == 'completed'


class LabResult(models.Model):
    """Lab test results"""
    RESULT_STATUS = [
        ('normal', 'Normal'),
        ('abnormal', 'Abnormal'),
        ('critical', 'Critical'),
        ('pending', 'Pending Review'),
    ]
    
    order = models.OneToOneField(LabOrder, on_delete=models.CASCADE, related_name='result')
    
    # Result Data
    result_value = models.TextField(help_text="Main result value or findings")
    reference_range = models.CharField(max_length=200, blank=True)
    unit = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=RESULT_STATUS, default='pending')
    
    # Additional Information
    interpretation = models.TextField(blank=True, help_text="Doctor's interpretation")
    attachments = models.FileField(upload_to='lab_results/', blank=True, null=True)
    
    # Verification
    verified_by = models.ForeignKey('doctors.Doctor', on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_results')
    verified_date = models.DateTimeField(null=True, blank=True)
    
    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Result for {self.order.test.name} - {self.order.patient.name}"
    
    def is_abnormal(self):
        return self.status in ['abnormal', 'critical']