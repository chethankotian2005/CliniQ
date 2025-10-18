# Quick Start Guide - QR Code Booking System

## Prerequisites
- Python 3.8+ installed
- Django project setup complete
- Required packages installed (see requirements.txt)

## Installation Steps

### 1. Install Required Packages
```bash
# Navigate to your medicalapp directory
cd medicalapp

# Install QR code dependencies (if not already installed)
pip install qrcode[pil]==8.2
pip install Pillow==11.3.0

# Or install all requirements
pip install -r requirements.txt
```

### 2. Database Setup
```bash
# Run migrations to ensure QR fields are in database
python manage.py makemigrations
python manage.py migrate

# Create superuser if needed
python manage.py createsuperuser
```

### 3. Start Development Server
```bash
python manage.py runserver
```

## Testing the QR Booking System

### 📱 For Patients (Online Booking):

1. **Visit Booking Page**
   - Open: `http://localhost:8000/patients/booking/`
   - Fill out the booking form
   - Select department and preferred doctor
   - Submit the form

2. **Get QR Code**
   - You'll be redirected to confirmation page
   - QR code will be displayed
   - Download or screenshot the QR code
   - Print the page if needed

3. **Test Data for Quick Testing**
   ```
   Name: John Doe
   Phone: +1234567890
   Email: john@example.com
   Age: 30
   Department: [Select from dropdown]
   ```

### 🏥 For Admin/Reception (QR Scanning):

1. **Access QR Scanner**
   - Login as admin user
   - Visit: `http://localhost:8000/patients/qr-scanner/`
   - Click "Start Scanner"

2. **Scan QR Code**
   - Point camera at QR code from booking confirmation
   - Or use "Manual Entry" to paste QR code data
   - System will check in the patient and assign token

3. **Verify Check-in**
   - Patient status changes from "Booked" to "Waiting"
   - Token number is assigned
   - Queue position is calculated

## Troubleshooting

### Camera Issues:
- **Browser asks for camera permission** → Click "Allow"
- **Scanner not working** → Try manual entry option
- **Mobile issues** → Use "Manual Entry" as fallback

### QR Code Issues:
- **QR not generating** → Check if qrcode package is installed
- **Image not displaying** → Check Pillow installation
- **Scanner not reading** → Try manual entry with QR data

### Database Issues:
- **Migration errors** → Run `python manage.py migrate`
- **Missing departments** → Create departments in admin panel
- **Token conflicts** → Check token generation logic

## URLs Reference

### Patient URLs:
- **Home Page**: `http://localhost:8000/`
- **Online Booking**: `http://localhost:8000/patients/booking/`
- **Booking Confirmation**: `http://localhost:8000/patients/booking/confirmation/{id}/`

### Admin URLs:
- **QR Scanner**: `http://localhost:8000/patients/qr-scanner/`
- **Admin Panel**: `http://localhost:8000/admin/`
- **Department Management**: `http://localhost:8000/adminpanel/`

### API Endpoints:
- **Create Booking**: `POST /patients/api/booking/create/`
- **Scan QR**: `POST /patients/api/booking/qr-scan/`
- **Get Booking**: `GET /patients/api/booking/{id}/`

## File Structure

```
medicalapp/
├── patients/
│   ├── booking_service.py      # QR generation & booking logic
│   ├── booking_views.py        # QR booking views
│   ├── models.py              # Queue model with QR fields
│   └── urls.py                # QR booking URLs
├── templates/
│   ├── patients/
│   │   ├── booking.html           # Online booking form
│   │   ├── booking_confirmation.html  # QR code display
│   │   └── qr_scanner.html        # QR scanner interface
│   ├── base.html              # Updated navigation
│   └── home.html              # Updated with QR features
└── requirements.txt           # Dependencies
```

## Production Deployment Notes

### Security:
- Enable HTTPS for camera access
- Restrict QR scanner access to admin users
- Implement rate limiting for booking API

### Performance:
- Consider QR code caching
- Optimize camera/scanner performance
- Monitor database performance for queue operations

### Monitoring:
- Track QR scan success rates
- Monitor booking completion rates
- Log failed scans for debugging

## Support

If you encounter issues:
1. Check browser console for errors
2. Verify camera permissions
3. Test with manual QR entry
4. Check Django logs for backend errors
5. Ensure all dependencies are installed

## Success Indicators

✅ **Booking System Working**:
- Form submits successfully
- QR code appears on confirmation page
- QR code can be downloaded/printed

✅ **Scanner System Working**:
- Camera starts successfully
- QR codes scan and process
- Patients get checked in with tokens
- Manual entry works as fallback

The QR booking system is now ready for use! 🎉