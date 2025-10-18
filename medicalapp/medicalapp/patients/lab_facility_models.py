"""
Laboratory Facility Models
Separate lab facilities that patients can select and book tests from
Similar to Hospital selection but for diagnostic labs
"""
from django.db import models
from django.contrib.auth.models import User
from geopy.distance import geodesic
import uuid


class LabFacility(models.Model):
    """Model representing a diagnostic laboratory facility"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    brand_name = models.CharField(max_length=100, blank=True, help_text="Lab chain name (e.g., Dr. Lal PathLabs, SRL)")
    
    # Address
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    
    # Contact
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    website = models.URLField(blank=True)
    
    # Location data for distance calculation
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Lab details
    description = models.TextField(blank=True)
    established_year = models.IntegerField(null=True, blank=True)
    accreditation = models.CharField(max_length=200, blank=True, help_text="NABL, CAP, ISO certifications")
    
    # Services offered
    home_sample_collection = models.BooleanField(default=True)
    online_reports = models.BooleanField(default=True)
    emergency_services = models.BooleanField(default=False)
    
    # Test categories available
    offers_blood_tests = models.BooleanField(default=True)
    offers_urine_tests = models.BooleanField(default=True)
    offers_imaging = models.BooleanField(default=False)
    offers_cardiology = models.BooleanField(default=False)
    offers_pathology = models.BooleanField(default=True)
    offers_microbiology = models.BooleanField(default=True)
    
    # Operating hours
    opens_at = models.TimeField(default='07:00')
    closes_at = models.TimeField(default='21:00')
    is_24_hours = models.BooleanField(default=False)
    
    # Pricing
    average_turnaround_hours = models.IntegerField(default=24, help_text="Average time for routine tests")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Standard discount %")
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False, help_text="Admin verified lab")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Rating
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=4.5)
    total_reviews = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-is_verified', 'name']
        verbose_name = 'Lab Facility'
        verbose_name_plural = 'Lab Facilities'
    
    def __str__(self):
        if self.brand_name:
            return f"{self.brand_name} - {self.name}"
        return self.name
    
    def get_distance_from(self, latitude, longitude):
        """Calculate distance from given coordinates"""
        if self.latitude and self.longitude:
            lab_coords = (float(self.latitude), float(self.longitude))
            user_coords = (latitude, longitude)
            return round(geodesic(lab_coords, user_coords).kilometers, 2)
        return None
    
    def get_available_tests_count(self):
        """Get count of tests available at this lab"""
        from patients.lab_models import LabTest
        # Count active tests that match this lab's capabilities
        count = 0
        if self.offers_blood_tests:
            count += LabTest.objects.filter(category='blood', is_active=True).count()
        if self.offers_urine_tests:
            count += LabTest.objects.filter(category='urine', is_active=True).count()
        if self.offers_imaging:
            count += LabTest.objects.filter(category='imaging', is_active=True).count()
        if self.offers_cardiology:
            count += LabTest.objects.filter(category='cardiology', is_active=True).count()
        if self.offers_pathology:
            count += LabTest.objects.filter(category='biopsy', is_active=True).count()
        if self.offers_microbiology:
            count += LabTest.objects.filter(category='culture', is_active=True).count()
        return count
    
    def get_test_categories(self):
        """Get list of test categories offered"""
        categories = []
        if self.offers_blood_tests:
            categories.append('Blood Tests')
        if self.offers_urine_tests:
            categories.append('Urine Tests')
        if self.offers_imaging:
            categories.append('Imaging')
        if self.offers_cardiology:
            categories.append('Cardiology')
        if self.offers_pathology:
            categories.append('Pathology')
        if self.offers_microbiology:
            categories.append('Microbiology')
        return categories


class LabFacilityImage(models.Model):
    """Images for lab facilities"""
    lab_facility = models.ForeignKey(LabFacility, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='lab_facility_images/')
    title = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'created_at']
        verbose_name = 'Lab Facility Image'
        verbose_name_plural = 'Lab Facility Images'
    
    def __str__(self):
        return f"Image for {self.lab_facility.name}"


class LabFacilityReview(models.Model):
    """Patient reviews for lab facilities"""
    lab_facility = models.ForeignKey(LabFacility, on_delete=models.CASCADE, related_name='reviews')
    patient_name = models.CharField(max_length=200)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    
    # Review aspects
    service_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    accuracy_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    speed_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    cleanliness_rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)], default=5)
    
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Lab Facility Review'
        verbose_name_plural = 'Lab Facility Reviews'
    
    def __str__(self):
        return f"{self.patient_name} - {self.lab_facility.name} ({self.rating}★)"


class LabFacilityTestPrice(models.Model):
    """Custom pricing for tests at specific lab facilities"""
    lab_facility = models.ForeignKey(LabFacility, on_delete=models.CASCADE, related_name='test_prices')
    test = models.ForeignKey('patients.LabTest', on_delete=models.CASCADE, related_name='facility_prices')
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Availability
    is_available = models.BooleanField(default=True)
    turnaround_hours = models.IntegerField(default=24, help_text="Result delivery time")
    
    # Home collection
    home_collection_available = models.BooleanField(default=True)
    home_collection_charge = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['lab_facility', 'test']
        ordering = ['price']
        verbose_name = 'Lab Test Price'
        verbose_name_plural = 'Lab Test Prices'
    
    def __str__(self):
        return f"{self.test.name} at {self.lab_facility.name} - ₹{self.price}"
    
    def get_final_price(self):
        """Get final price after discount"""
        if self.discounted_price:
            return self.discounted_price
        return self.price
