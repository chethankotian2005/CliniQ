# QR Code Booking System Implementation

## Overview

I have successfully implemented a comprehensive QR code booking system for your medical appointment project. This feature allows patients to book appointments from home and use QR codes to check in at the hospital.

## Features Implemented

### 1. **Online Booking System**
- **URL**: `/patients/booking/`
- **Template**: `templates/patients/booking.html`
- **Functionality**: 
  - Patients can book appointments online
  - Select department and preferred doctor
  - Choose date and time slots
  - Automatically generates unique QR code for each booking

### 2. **QR Code Generation**
- **Service**: `patients/booking_service.py`
- **Method**: `generate_booking_qr_code()`
- **Features**:
  - Creates unique QR code data: `SMARTQUEUE:BOOKING:{booking_id}:{unique_hash}`
  - Generates QR code image as base64 PNG
  - Stores QR code reference in database

### 3. **Booking Confirmation Page**
- **URL**: `/patients/booking/confirmation/{booking_id}/`
- **Template**: `templates/patients/booking_confirmation.html`
- **Features**:
  - Displays booking details
  - Shows QR code for download/print
  - Instructions for using the QR code
  - Print-friendly layout

### 4. **QR Code Scanner for Admin/Reception**
- **URL**: `/patients/qr-scanner/`
- **Template**: `templates/patients/qr_scanner.html`
- **Features**:
  - Camera-based QR code scanning
  - Manual QR code entry option
  - Real-time patient check-in
  - Automatic token number assignment
  - Recent scans history

### 5. **Backend API Endpoints**
- **Booking Creation**: `POST /patients/api/booking/create/`
- **QR Scanning**: `POST /patients/api/booking/qr-scan/`
- **Booking Details**: `GET /patients/api/booking/{id}/`
- **Cancel Booking**: `POST /patients/api/booking/{id}/cancel/`

## How the QR System Works

### For Patients:
1. **Book Online**: Visit `/patients/booking/` and fill the form
2. **Get QR Code**: Receive unique QR code on confirmation page
3. **Save QR Code**: Download/screenshot the QR code
4. **Visit Hospital**: Come on booking date
5. **Scan at Reception**: Show QR code to reception staff
6. **Get Token**: Receive token number and join queue

### For Admin/Reception:
1. **Open Scanner**: Visit `/patients/qr-scanner/`
2. **Start Camera**: Click "Start Scanner" button
3. **Scan QR Code**: Point camera at patient's QR code
4. **Check In Patient**: System automatically assigns token
5. **View Details**: See patient info and queue position

## Database Changes

The `Queue` model already had QR code fields implemented:
- `qr_code`: Stores unique QR code data
- `is_online_booking`: Boolean flag for online bookings
- `booked_at`: Timestamp of online booking
- `arrived_at`: Timestamp when QR was scanned
- `booking_date`: Date for which booking was made
- `status`: Includes 'booked' status for online bookings

## Files Created/Modified

### New Templates:
1. `templates/patients/booking.html` - Online booking form
2. `templates/patients/booking_confirmation.html` - QR code display
3. `templates/patients/qr_scanner.html` - QR scanner interface

### Modified Templates:
1. `templates/base.html` - Added navigation links and Font Awesome icons
2. `templates/home.html` - Added QR booking feature showcase

### Enhanced Services:
1. `patients/booking_service.py` - Enhanced QR generation method
2. `patients/booking_views.py` - Fixed QR code image regeneration

## Dependencies

The following packages are already included in `requirements.txt`:
- `qrcode==8.2` - QR code generation
- `Pillow==11.3.0` - Image processing for QR codes

## Navigation Updates

Added new navigation links:
- **"Book Online"** - For all users to access online booking
- **"QR Scanner"** - For admin users to scan QR codes

## Testing the Implementation

### To test online booking:
1. Visit the homepage and click "Book Online"
2. Fill out the booking form
3. Submit and receive QR code
4. Save/print the QR code

### To test QR scanning:
1. Log in as admin user
2. Visit "QR Scanner" from navigation
3. Click "Start Scanner"
4. Scan the QR code from booking confirmation
5. Verify patient check-in and token assignment

## Mobile Compatibility

The QR scanner uses the HTML5 QRCode library which supports:
- Camera access on mobile devices
- Responsive design for tablets and phones
- Manual entry fallback if camera fails

## Security Features

- Unique QR codes with booking ID + random hash
- QR codes are only valid for the booking date
- Cannot reuse QR codes once scanned
- Admin authentication required for scanner access

## Error Handling

The system handles:
- Invalid QR codes
- Expired bookings
- Already scanned QR codes
- Camera permission issues
- Network connectivity problems

## Next Steps for Production

1. **Test the booking flow end-to-end**
2. **Configure camera permissions** for QR scanner
3. **Train reception staff** on QR scanner usage
4. **Set up backup manual entry** procedures
5. **Monitor QR code scanning success rates**

## API Usage Examples

### Create Booking:
```javascript
fetch('/patients/api/booking/create/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        name: 'John Doe',
        phone_number: '+1234567890',
        department_id: 1,
        doctor_id: 2,
        booking_date: '2025-10-10'
    })
})
```

### Scan QR Code:
```javascript
fetch('/patients/api/booking/qr-scan/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        qr_code: 'SMARTQUEUE:BOOKING:123:abc123'
    })
})
```

The QR code booking system is now fully implemented and ready for testing!