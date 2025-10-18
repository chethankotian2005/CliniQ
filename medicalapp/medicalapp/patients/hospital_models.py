"""
Hospital models for managing multiple hospital locations
"""
from django.db import models
from django.contrib.auth.models import User
import uuid

class Hospital(models.Model):
    """Model representing a hospital location"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    
    # Location data
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Hospital details
    description = models.TextField(blank=True)
    established_year = models.IntegerField(null=True, blank=True)
    total_beds = models.IntegerField(default=0)
    emergency_services = models.BooleanField(default=True)
    
    # Features
    has_parking = models.BooleanField(default=True)
    has_pharmacy = models.BooleanField(default=True)
    has_lab = models.BooleanField(default=True)
    has_ambulance = models.BooleanField(default=True)
    
    # Operating hours
    opens_at = models.TimeField(default='08:00')
    closes_at = models.TimeField(default='20:00')
    is_24_hours = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Rating
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.5)
    total_reviews = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.city}"
    
    def get_distance_from(self, latitude, longitude):
        """Calculate distance from given coordinates using geopy"""
        if self.latitude and self.longitude:
            from geopy.distance import geodesic
            hospital_coords = (float(self.latitude), float(self.longitude))
            user_coords = (latitude, longitude)
            return round(geodesic(hospital_coords, user_coords).kilometers, 2)
        return None
    
    def get_departments_count(self):
        """Get count of departments in this hospital"""
        from patients.models import Department
        return Department.objects.filter(hospital=self, is_active=True).count()

class HospitalImage(models.Model):
    """Images for hospitals"""
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='hospital_images/')
    title = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'created_at']
    
    def __str__(self):
        return f"{self.hospital.name} - {self.title or 'Image'}"

class HospitalReview(models.Model):
    """Patient reviews for hospitals"""
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='reviews')
    patient_name = models.CharField(max_length=100)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.hospital.name} - {self.rating} stars by {self.patient_name}"