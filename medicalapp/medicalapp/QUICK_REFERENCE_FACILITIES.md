# 🎯 Quick Reference: Hospital & Lab Selection System

## Portal Structure

```
CliniQ Patient Portal
├── 📊 Dashboard (Statistics & Recent Activity)
├── 📅 Appointments (Book & Track)
├── 🧪 Labs (Test Results)
├── 🏥 Hospitals (Select Hospital for Appointments)
├── 🔬 Lab Facilities (Select Lab for Tests) ← NEW!
└── 🤖 AI Chatbot (Health Assistant)
```

## Two Selection Systems

### 1. 🏥 **Hospital Selection** (For Appointments)

**Purpose**: Select a hospital to book doctor appointments

**URL**: `/patients/portal/` → Click "Hospitals" tab

**Features**:
- Browse all hospitals
- Find nearby hospitals
- View departments
- See doctors
- Book appointments
- Check queue status

**Use Case**:
> "I need to see a cardiologist" → Select hospital → View cardiology department → Book appointment

---

### 2. 🔬 **Lab Facility Selection** (For Tests)

**Purpose**: Select a diagnostic lab to book tests

**URL**: `/patients/portal/` → Click "Lab Facilities" tab

**Features**:
- Browse all labs
- Find nearby labs
- View available tests
- See custom pricing
- Home collection option
- Book tests

**Use Case**:
> "I need a blood test" → Select lab facility → View blood tests → Book test

---

## Side-by-Side Comparison

| Feature | Hospitals 🏥 | Lab Facilities 🔬 |
|---------|--------------|-------------------|
| **What you book** | Doctor appointments | Diagnostic tests |
| **Browse by** | Departments & specialties | Test categories & pricing |
| **See** | Doctors, bed count | Tests, accreditation |
| **Location search** | ✅ Find nearby | ✅ Find nearby |
| **Ratings** | ✅ Patient reviews | ✅ Patient reviews |
| **Special features** | Emergency, 24/7 | Home collection, discounts |
| **Images** | ✅ Hospital photos | ✅ Lab photos |
| **Book** | Appointment with doctor | Test with date/time |

---

## Quick Access

### From Portal Home:

```
1. Click "Hospitals" tab
   → Browse hospitals
   → Select hospital
   → Book appointment

2. Click "Lab Facilities" tab
   → Browse labs
   → Select lab
   → Book test
```

### Direct URLs:

```bash
# Hospitals
/patients/portal/                    # Portal home (has hospitals tab)

# Lab Facilities
/patients/lab-facilities/            # Browse all labs
/patients/lab-facility/<lab-id>/     # Lab detail with tests

# Find Nearby (via API)
/patients/api/nearby-hospitals/      # Nearby hospitals
/patients/api/labs/nearby/           # Nearby labs
```

---

## Migration Commands

```bash
# Create migrations for new lab facility models
python manage.py makemigrations patients

# Apply migrations
python manage.py migrate

# Access portal (sample data auto-creates)
# Visit: http://localhost:8000/patients/portal/
```

---

## Admin Panel Access

```
/admin/patients/hospital/          → Manage hospitals
/admin/patients/labfacility/       → Manage lab facilities
/admin/patients/labtest/           → Manage lab tests
/admin/patients/labfacilitytestprice/ → Set custom pricing
```

---

## Patient Workflow Examples

### Example 1: Doctor Appointment

```
Patient needs: "See a cardiologist"

1. Login to portal
2. Click "Hospitals" tab
3. See list of hospitals
4. Click "Find Nearby" (optional)
5. Select "City General Hospital"
6. View "Cardiology Department"
7. Choose doctor
8. Book appointment
9. Done! ✅
```

### Example 2: Lab Test

```
Patient needs: "Blood sugar test"

1. Login to portal
2. Click "Lab Facilities" tab
3. See list of diagnostic labs
4. Click "Find Nearby" (optional)
5. Select "Dr. Lal PathLabs"
6. Browse "Blood Tests"
7. Select "Fasting Blood Sugar"
8. Choose date/time
9. Request home collection (optional)
10. Book test
11. Done! ✅
```

---

## Sample Data (Auto-Created)

### Hospitals (from hospital_models.py):
- Auto-creates when first visiting hospitals tab

### Lab Facilities (from lab_facility_models.py):
1. **Dr. Lal PathLabs** - Central Lab, Downtown
   - All test categories
   - 15% discount
   - Home collection
   
2. **SRL Diagnostics** - Express Diagnostics
   - 24/7 service
   - 20% discount
   - Focus on blood/urine
   
3. **Thyrocare** - City Imaging Center
   - Imaging & cardiology
   - 10% discount
   - Advanced equipment

---

## Key Features

### Location-Based Discovery 📍
Both hospitals and labs support:
- "Find Nearby" button
- Uses browser geolocation
- Sorts by distance (km)
- Shows distance on cards

### Filtering 🔍
**Hospitals**: By departments, emergency, 24/7
**Labs**: By verified, 24/7, home collection, discounts

### Booking 📅
**Hospitals**: 
- Select department → doctor → date/time
- Get QR code for check-in

**Labs**:
- Select test → lab facility → date/time
- Optional home collection
- Track order status

---

## Developer Notes

### Models Structure:

```
Hospital Model          LabFacility Model
    ↓                       ↓
Department Model        LabTest Model
    ↓                       ↓
Queue Model             LabOrder Model
    ↓                       ↓
(Appointments)          LabResult Model
```

### Shared Pattern:

Both use same design pattern:
```python
# List view: Show all facilities
def facility_list(request)

# Detail view: Show facility details  
def facility_detail(request, facility_id)

# API: Get nearby
@api_view(['POST'])
def get_nearby(request)
```

---

## Testing Checklist

- [ ] Run migrations successfully
- [ ] Access portal home
- [ ] Click "Hospitals" tab - see hospitals
- [ ] Click "Lab Facilities" tab - see labs (3 auto-created)
- [ ] Test "Find Nearby" on both
- [ ] Select a hospital → view departments
- [ ] Select a lab → view tests
- [ ] Book appointment at hospital
- [ ] Book test at lab
- [ ] Verify both bookings in dashboard

---

## What's Unique About This Implementation

✨ **Dual Selection System**: 
- Most medical apps only have hospitals OR labs
- This has BOTH, working identically

✨ **Patient Choice**:
- Patients choose their preferred facility
- Based on location, rating, pricing, features

✨ **Consistent UX**:
- Same interaction pattern
- Same card design
- Same booking flow
- Easy to understand

---

**Status**: ✅ Fully Implemented & Ready to Use

**Version**: 2.0 (Added Lab Facilities)

**Last Updated**: October 10, 2025
