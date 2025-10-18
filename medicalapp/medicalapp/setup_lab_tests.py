"""
Lab System Setup Script
Creates sample lab tests for the CliniQ system

Run this after migrating the lab_models:
python manage.py shell < setup_lab_tests.py
"""

from patients.lab_models import LabTest

def create_sample_lab_tests():
    """Create comprehensive lab test catalog"""
    
    tests = [
        # Blood Tests
        {
            'name': 'Complete Blood Count (CBC)',
            'category': 'blood',
            'description': 'Measures red blood cells, white blood cells, hemoglobin, hematocrit, and platelets. Helps diagnose anemia, infections, and blood disorders.',
            'price': 500.00,
            'preparation_required': False,
            'duration_minutes': 30
        },
        {
            'name': 'Lipid Profile',
            'category': 'blood',
            'description': 'Measures total cholesterol, HDL, LDL, and triglycerides. Assesses cardiovascular risk.',
            'price': 800.00,
            'preparation_required': True,
            'preparation_instructions': 'Fasting for 12 hours required. Only water allowed.',
            'duration_minutes': 45
        },
        {
            'name': 'Thyroid Function Test (TFT)',
            'category': 'blood',
            'description': 'Measures TSH, T3, and T4 levels to evaluate thyroid function.',
            'price': 900.00,
            'preparation_required': False,
            'duration_minutes': 60
        },
        {
            'name': 'Fasting Blood Sugar (FBS)',
            'category': 'blood',
            'description': 'Measures glucose levels after fasting. Screens for diabetes.',
            'price': 200.00,
            'preparation_required': True,
            'preparation_instructions': 'Fasting for 8-10 hours required.',
            'duration_minutes': 15
        },
        {
            'name': 'HbA1c (Glycated Hemoglobin)',
            'category': 'blood',
            'description': 'Measures average blood sugar over past 2-3 months. Diabetes management.',
            'price': 600.00,
            'preparation_required': False,
            'duration_minutes': 45
        },
        {
            'name': 'Liver Function Test (LFT)',
            'category': 'blood',
            'description': 'Measures enzymes and proteins to evaluate liver health.',
            'price': 700.00,
            'preparation_required': False,
            'duration_minutes': 45
        },
        {
            'name': 'Kidney Function Test (KFT)',
            'category': 'blood',
            'description': 'Measures creatinine, urea, and electrolytes to assess kidney function.',
            'price': 700.00,
            'preparation_required': False,
            'duration_minutes': 45
        },
        {
            'name': 'Vitamin D Test',
            'category': 'blood',
            'description': 'Measures 25-hydroxyvitamin D levels.',
            'price': 1200.00,
            'preparation_required': False,
            'duration_minutes': 60
        },
        {
            'name': 'Vitamin B12 Test',
            'category': 'blood',
            'description': 'Measures vitamin B12 levels to diagnose deficiency.',
            'price': 800.00,
            'preparation_required': False,
            'duration_minutes': 45
        },
        
        # Urine Tests
        {
            'name': 'Urine Routine & Microscopy',
            'category': 'urine',
            'description': 'Complete urinalysis including physical, chemical, and microscopic examination.',
            'price': 300.00,
            'preparation_required': False,
            'duration_minutes': 30
        },
        {
            'name': 'Urine Culture',
            'category': 'urine',
            'description': 'Identifies bacteria causing urinary tract infections.',
            'price': 500.00,
            'preparation_required': True,
            'preparation_instructions': 'Clean catch midstream sample required. Follow collection instructions.',
            'duration_minutes': 2880  # 48 hours
        },
        {
            'name': '24-Hour Urine Protein',
            'category': 'urine',
            'description': 'Measures total protein excretion over 24 hours.',
            'price': 600.00,
            'preparation_required': True,
            'preparation_instructions': 'Collect all urine for 24 hours in provided container. Keep refrigerated.',
            'duration_minutes': 60
        },
        
        # Imaging
        {
            'name': 'Chest X-Ray',
            'category': 'imaging',
            'description': 'Radiography of chest to evaluate lungs, heart, and chest wall.',
            'price': 600.00,
            'preparation_required': False,
            'duration_minutes': 15
        },
        {
            'name': 'Abdominal Ultrasound',
            'category': 'imaging',
            'description': 'Ultrasound imaging of abdominal organs (liver, gallbladder, kidneys, spleen).',
            'price': 1500.00,
            'preparation_required': True,
            'preparation_instructions': 'Fasting for 6 hours. Drink 4-5 glasses of water 1 hour before test.',
            'duration_minutes': 30
        },
        {
            'name': 'Pelvic Ultrasound',
            'category': 'imaging',
            'description': 'Ultrasound imaging of pelvic organs (uterus, ovaries, bladder).',
            'price': 1500.00,
            'preparation_required': True,
            'preparation_instructions': 'Full bladder required. Drink 4-5 glasses of water 1 hour before test.',
            'duration_minutes': 30
        },
        {
            'name': 'CT Scan (Head)',
            'category': 'imaging',
            'description': 'Computed tomography of brain and skull.',
            'price': 3500.00,
            'preparation_required': False,
            'duration_minutes': 20
        },
        {
            'name': 'MRI Scan (Brain)',
            'category': 'imaging',
            'description': 'Magnetic resonance imaging of brain.',
            'price': 6000.00,
            'preparation_required': True,
            'preparation_instructions': 'Remove all metal objects. Inform if you have implants or pacemaker.',
            'duration_minutes': 45
        },
        
        # Cardiology
        {
            'name': 'ECG (Electrocardiogram)',
            'category': 'cardiology',
            'description': 'Records heart\'s electrical activity. Detects arrhythmias and heart problems.',
            'price': 300.00,
            'preparation_required': False,
            'duration_minutes': 10
        },
        {
            'name': 'Echocardiogram (2D Echo)',
            'category': 'cardiology',
            'description': 'Ultrasound of heart to evaluate structure and function.',
            'price': 2000.00,
            'preparation_required': False,
            'duration_minutes': 30
        },
        {
            'name': 'Treadmill Test (TMT)',
            'category': 'cardiology',
            'description': 'Exercise stress test to evaluate heart function during physical activity.',
            'price': 1500.00,
            'preparation_required': True,
            'preparation_instructions': 'Wear comfortable shoes. Avoid heavy meals 2 hours before test.',
            'duration_minutes': 45
        },
        {
            'name': 'Holter Monitoring (24-hour)',
            'category': 'cardiology',
            'description': 'Continuous ECG recording for 24 hours to detect arrhythmias.',
            'price': 2500.00,
            'preparation_required': False,
            'duration_minutes': 1440  # 24 hours
        },
        
        # Microbiology/Culture
        {
            'name': 'Blood Culture',
            'category': 'culture',
            'description': 'Identifies bacteria or fungi in bloodstream (sepsis detection).',
            'price': 1000.00,
            'preparation_required': False,
            'duration_minutes': 2880  # 48 hours
        },
        {
            'name': 'Throat Swab Culture',
            'category': 'culture',
            'description': 'Identifies bacteria causing throat infections.',
            'price': 500.00,
            'preparation_required': False,
            'duration_minutes': 2880  # 48 hours
        },
        {
            'name': 'Wound Culture',
            'category': 'culture',
            'description': 'Identifies bacteria in wound infections.',
            'price': 600.00,
            'preparation_required': False,
            'duration_minutes': 2880  # 48 hours
        },
        
        # Pathology/Biopsy
        {
            'name': 'FNAC (Fine Needle Aspiration Cytology)',
            'category': 'biopsy',
            'description': 'Tissue sample examination for diagnosis of lumps/masses.',
            'price': 1500.00,
            'preparation_required': False,
            'duration_minutes': 2880  # 48 hours for report
        },
        {
            'name': 'Tissue Biopsy',
            'category': 'biopsy',
            'description': 'Microscopic examination of tissue sample.',
            'price': 2000.00,
            'preparation_required': False,
            'duration_minutes': 4320  # 72 hours
        },
        {
            'name': 'Pap Smear',
            'category': 'biopsy',
            'description': 'Cervical cancer screening test.',
            'price': 800.00,
            'preparation_required': True,
            'preparation_instructions': 'Avoid intercourse, douching, or vaginal medications for 48 hours before test.',
            'duration_minutes': 2880  # 48 hours
        },
    ]
    
    created_count = 0
    updated_count = 0
    
    for test_data in tests:
        test, created = LabTest.objects.get_or_create(
            name=test_data['name'],
            defaults=test_data
        )
        
        if created:
            created_count += 1
            print(f"✓ Created: {test.name} ({test.get_category_display()})")
        else:
            # Update existing test
            for key, value in test_data.items():
                setattr(test, key, value)
            test.save()
            updated_count += 1
            print(f"↻ Updated: {test.name} ({test.get_category_display()})")
    
    print(f"\n{'='*60}")
    print(f"Lab Tests Setup Complete!")
    print(f"Created: {created_count} tests")
    print(f"Updated: {updated_count} tests")
    print(f"Total: {LabTest.objects.count()} tests in database")
    print(f"{'='*60}")
    
    # Print summary by category
    print("\nTests by Category:")
    categories = LabTest.objects.values_list('category', flat=True).distinct()
    for category in categories:
        count = LabTest.objects.filter(category=category).count()
        display_name = dict(LabTest.CATEGORY_CHOICES).get(category, category)
        print(f"  {display_name}: {count} tests")


if __name__ == '__main__':
    print("Setting up lab tests...")
    create_sample_lab_tests()
