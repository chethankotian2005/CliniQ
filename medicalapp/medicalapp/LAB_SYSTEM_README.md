# 🧪 CliniQ Lab Management System

A modern, hospital-grade laboratory management system integrated into the CliniQ patient portal.

## 🌟 Features

- **27 Pre-configured Lab Tests** across 6 medical categories
- **Full Booking Workflow**: Browse tests, schedule appointments, track status
- **Result Management**: View results with color-coded status (Normal, Abnormal, Critical)
- **Priority Handling**: Routine, Urgent, and STAT processing
- **Mobile-First Design**: Fully responsive across all devices
- **Modern UI**: Gradient cards, smooth animations, professional look

## 🚀 Quick Setup

### 1. Run Migrations
```bash
python manage.py makemigrations patients
python manage.py migrate
```

### 2. Create Sample Lab Tests
```bash
python manage.py shell < setup_lab_tests.py
```

### 3. Access the Portal
Open your browser and navigate to:
```
http://localhost:8000/patients/portal/
```

## 📋 Lab Test Categories

### Blood Tests (9 tests)
Complete Blood Count, Lipid Profile, Thyroid Function, Blood Sugar, HbA1c, Liver Function, Kidney Function, Vitamin D, Vitamin B12

### Urine Tests (3 tests)
Urine Routine, Urine Culture, 24-Hour Protein

### Imaging (5 tests)
Chest X-Ray, Abdominal Ultrasound, Pelvic Ultrasound, CT Scan, MRI

### Cardiology (4 tests)
ECG, 2D Echo, Treadmill Test, Holter Monitoring

### Microbiology (3 tests)
Blood Culture, Throat Swab, Wound Culture

### Pathology (3 tests)
FNAC, Tissue Biopsy, Pap Smear

## 🎨 UI Components

### Dashboard Features
- **Quick Action Cards**: Book appointments, labs, check queue, AI assistant
- **Statistics Widgets**: Total appointments, pending tests, new results
- **Tabbed Interface**: Dashboard, Appointments, Labs, Hospitals, Chatbot
- **Real-time Updates**: Live clock, status notifications

### Lab-Specific Features
- **Test Catalog**: Browse by category with pricing
- **Booking Form**: Date/time selection with preparation instructions
- **Order Tracking**: Status timeline from order to completion
- **Result Viewer**: Color-coded badges, download option

## 📱 Responsive Design

- **Mobile (< 768px)**: Single column, stacked cards
- **Tablet (768px - 1024px)**: 2-column grid
- **Desktop (> 1024px)**: 4-column layout

## 🎯 Workflow

```
1. Patient browses lab tests by category
2. Selects test and schedules appointment
3. Receives confirmation with preparation instructions
4. Visits hospital for sample collection
5. Lab processes sample
6. Results uploaded by lab technician
7. Doctor verifies results
8. Patient views results in portal
9. Can download or share results
```

## 🔐 Security

- All views require authentication
- Patients can only access their own data
- CSRF protection on all forms
- Secure file uploads for result attachments

## 🛠️ Tech Stack

- **Backend**: Django 5.2.7, Django REST Framework
- **Frontend**: Bootstrap 5, FontAwesome, Vanilla JS
- **Database**: SQLite (dev), PostgreSQL (prod ready)
- **Storage**: Local filesystem for attachments

## 📊 Database Models

### LabTest
- Test catalog with name, category, price, duration
- Preparation instructions
- Active/inactive status

### LabOrder
- Patient and test references
- Status workflow (6 stages)
- Priority levels (routine, urgent, STAT)
- Scheduling information

### LabResult
- Result values with reference ranges
- Status (normal, abnormal, critical, pending)
- Doctor verification
- File attachments

## 🔗 API Endpoints

### Template Routes
```
/patients/labs/                    → Browse tests
/patients/labs/book/<test_id>/     → Book test
/patients/labs/orders/             → View orders
/patients/labs/results/            → View results
```

### API Routes
```
/patients/api/labs/stats/                    → Dashboard stats
/patients/api/labs/search/?q=<query>         → Search tests
/patients/api/labs/order/<id>/cancel/        → Cancel order
/patients/api/labs/order/<id>/reschedule/    → Reschedule
/patients/api/labs/result/<id>/download/     → Download result
```

## 📖 Documentation

- **LAB_FEATURE_IMPLEMENTATION.md**: Technical documentation (500+ lines)
- **IMPLEMENTATION_SUMMARY.md**: Quick reference guide (600+ lines)
- **FINAL_IMPLEMENTATION_REPORT.md**: Complete feature report (700+ lines)

## 🧪 Testing

Run the test checklist:
1. Database migration
2. Sample data creation
3. User authentication
4. Test booking
5. Order tracking
6. Result viewing
7. Mobile responsiveness

See `FINAL_IMPLEMENTATION_REPORT.md` for detailed testing checklist.

## 🎨 Color Scheme

- **Primary**: Purple-blue gradient (#667eea → #764ba2)
- **Success**: Green gradient (#11998e → #38ef7d)
- **Info**: Blue gradient (#4facfe → #00f2fe)
- **Warning**: Pink-yellow gradient (#fa709a → #fee140)
- **Danger**: Red gradient (#ff0844 → #ffb199)

## 📞 Support

For issues or questions:
1. Check documentation in markdown files
2. Review Django error logs
3. Verify migrations: `python manage.py showmigrations`
4. Check admin panel: `/admin/patients/labtest/`

## 🚀 Future Enhancements

Potential additions:
- PDF generation for results
- Email/SMS notifications
- Payment gateway integration
- QR codes for sample tracking
- Doctor portal
- Lab technician interface
- Result trending charts
- Critical result auto-alerts

## 📝 License

Part of the CliniQ Medical Token Management System

## 👥 Contributors

Developed for modern hospital laboratory management

---

**Version**: 1.0.0  
**Status**: Production Ready  
**Last Updated**: October 10, 2025
