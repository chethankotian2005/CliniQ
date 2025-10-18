# 📹 Teleappointment Feature - CLINIQ

## Overview

The Teleappointment feature extends CLINIQ's existing appointment system to support video consultations, allowing patients to receive medical care remotely through secure video calls.

## 🎯 Features

### For Patients
- 📅 **Online Booking**: Book teleappointments from home
- 📹 **Video Consultations**: Browser-based video calls (no app needed)
- 📱 **SMS/Email Notifications**: Automatic appointment confirmations and reminders
- 🔄 **Rescheduling**: Easy appointment rescheduling
- 💬 **In-call Chat**: Text messaging during video consultations
- 📋 **Pre-call Instructions**: Automatic setup guidance

### For Healthcare Providers
- 🖥️ **Management Dashboard**: View and manage all teleappointments
- 👨‍⚕️ **Multi-platform Support**: Zoom, Google Meet, Teams, or WebRTC
- 📊 **Real-time Status**: Track appointment progress
- 🔧 **Technical Support**: Built-in device testing and troubleshooting
- 📈 **Analytics**: Call duration and quality metrics

## 🏗️ Architecture

### New Models
1. **TeleAppointment**: Manages video call details and status
2. **Queue.appointment_type**: Distinguishes between in-person and telemedicine

### Key Components
- `telemedicine_service.py`: Core business logic
- `teleappointment_views.py`: API and template views  
- `teleappointment_booking.html`: Patient booking interface
- `video_call_room.html`: Video call interface
- `teleappointment_management.html`: Staff management dashboard

## 🚀 Installation

### 1. Prerequisites
```bash
# Required Python packages
pip install django djangorestframework qrcode pillow
```

### 2. Database Migration
```bash
python manage.py makemigrations patients
python manage.py migrate
```

### 3. Run Setup Script
```bash
python setup_teleappointment.py
```

### 4. Settings Configuration
Add to your `settings.py`:

```python
# Teleappointment Settings
SITE_URL = 'https://yourdomain.com'
DEFAULT_FROM_EMAIL = 'noreply@yourdomain.com'

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'

# Time Zone
TIME_ZONE = 'Asia/Kolkata'
USE_TZ = True
```

## 📱 Usage

### Patient Workflow
1. **Book Appointment**: Visit `/patients/teleappointment/`
2. **Receive Confirmation**: Get SMS/email with meeting details
3. **Join Call**: Click meeting link 15 minutes before appointment
4. **Device Check**: Test camera/microphone before joining
5. **Video Consultation**: Attend video call with doctor
6. **Feedback**: Provide post-consultation feedback

### Staff Workflow
1. **View Dashboard**: Access `/patients/teleappointment/management/`
2. **Join Calls**: Start video sessions with patients
3. **Manage Appointments**: Reschedule or cancel as needed
4. **Monitor Status**: Track real-time appointment progress

## 🔗 API Endpoints

### Booking
```
POST /patients/api/teleappointment/book/
GET  /patients/api/teleappointment/slots/{department_id}/
```

### Management
```
GET  /patients/api/teleappointment/{appointment_id}/
POST /patients/api/teleappointment/start/
POST /patients/api/teleappointment/end/
POST /patients/api/teleappointment/reschedule/
```

### Patient Data
```
GET /patients/api/teleappointment/patient/{phone_number}/
```

## 📋 Database Schema

### Queue Model Changes
```python
class Queue(models.Model):
    # ... existing fields ...
    appointment_type = models.CharField(
        max_length=20,
        choices=[
            ('in_person', 'In-Person Appointment'),
            ('telemedicine', 'Telemedicine Appointment'),
        ],
        default='in_person'
    )
```

### TeleAppointment Model
```python
class TeleAppointment(models.Model):
    queue_entry = models.OneToOneField(Queue, on_delete=models.CASCADE)
    meeting_url = models.URLField()
    meeting_id = models.CharField(max_length=100)
    platform = models.CharField(max_length=20, default='webrtc')
    scheduled_start_time = models.DateTimeField()
    tele_status = models.CharField(max_length=20, default='scheduled')
    # ... additional fields for call management
```

## 🎨 User Interface

### Responsive Design
- 📱 **Mobile-first**: Optimized for smartphones and tablets
- 🖥️ **Desktop-friendly**: Full-featured desktop interface
- 🎯 **Accessibility**: Screen reader compatible

### Key Pages
1. **Booking Form**: Intuitive appointment scheduling
2. **Video Call Room**: Professional video consultation interface
3. **Management Dashboard**: Comprehensive staff tools

## 🔧 Technical Features

### Video Technology
- **WebRTC**: Browser-based video calls (default)
- **Platform Integration**: Zoom, Google Meet, Microsoft Teams support
- **Device Testing**: Pre-call camera/microphone verification
- **Quality Monitoring**: Connection quality tracking

### Security
- **Secure Meetings**: Unique meeting IDs for each appointment
- **Access Control**: Time-based meeting access
- **Data Protection**: Patient information security

### Performance
- **Auto-refresh**: Real-time status updates
- **Mobile Optimization**: Efficient bandwidth usage
- **Error Handling**: Graceful failure recovery

## 📊 Sample API Requests

### Book Teleappointment
```javascript
fetch('/patients/api/teleappointment/book/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        name: 'John Doe',
        phone_number: '9876543210',
        department_id: 1,
        appointment_date: '2024-12-15',
        appointment_time: '14:00',
        platform: 'webrtc'
    })
})
```

### Start Video Session
```javascript
fetch('/patients/api/teleappointment/start/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        appointment_id: 123
    })
})
```

## 🛠️ Customization

### Video Platforms
Modify `telemedicine_service.py` to add new video platforms:

```python
def generate_meeting_url(self, tele_appointment):
    if tele_appointment.platform == 'custom_platform':
        return f"https://custom.platform.com/meeting/{tele_appointment.meeting_id}"
    # ... existing platforms
```

### Notifications
Customize SMS/email templates in `telemedicine_service.py`:

```python
def send_appointment_confirmation(self, tele_appointment):
    # Customize message content
    sms_message = f"Your teleappointment is confirmed..."
```

### UI Themes
Modify CSS in templates to match your branding:

```css
.appointment-type-selector {
    background: linear-gradient(135deg, #your-color1, #your-color2);
}
```

## 🧪 Testing

### Manual Testing
1. Book a test teleappointment
2. Join video call from different devices
3. Test rescheduling functionality
4. Verify SMS/email notifications

### Automated Testing
```python
# Add to your test suite
class TeleappointmentTestCase(TestCase):
    def test_booking_creation(self):
        # Test teleappointment booking
        pass
    
    def test_video_session_start(self):
        # Test video session management
        pass
```

## 🔍 Troubleshooting

### Common Issues

1. **Video not working**
   - Check browser permissions for camera/microphone
   - Ensure modern browser (Chrome, Firefox, Safari, Edge)
   - Test internet connection speed

2. **SMS not sending**
   - Verify SMS service configuration in `sms_service.py`
   - Check API credentials and phone number format

3. **Email notifications failing**
   - Verify SMTP settings in Django settings
   - Check email server connectivity

4. **Database errors**
   - Run migrations: `python manage.py migrate`
   - Check for model conflicts

### Browser Compatibility
- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+

## 📈 Performance Tips

1. **Optimize for Mobile**: Ensure video calls work well on mobile networks
2. **Bandwidth Management**: Implement quality adjustments based on connection
3. **Caching**: Cache meeting URLs and appointment data appropriately
4. **Database Indexing**: Add indexes on frequently queried fields

## 🔒 Security Considerations

1. **Meeting Access**: Implement time-based access controls
2. **Patient Privacy**: Ensure video calls are secure and private
3. **Data Encryption**: Use HTTPS for all teleappointment communications
4. **Audit Logging**: Track video session activities for compliance

## 🚀 Future Enhancements

### Planned Features
- 📹 **Screen Sharing**: Enable document sharing during calls
- 🤖 **AI Assistant**: Automated appointment scheduling
- 📊 **Advanced Analytics**: Detailed consultation metrics
- 🔄 **Integration**: EHR and billing system integration
- 📱 **Mobile App**: Dedicated mobile application

### Scalability
- **Load Balancing**: Support for multiple video servers
- **CDN Integration**: Global video delivery optimization
- **Microservices**: Separate telehealth service architecture

## 📞 Support

For technical support or feature requests:
- 📧 Email: support@cliniq.com
- 🐛 Issues: GitHub repository issues
- 📖 Documentation: Full API documentation available

## 📄 License

This teleappointment feature is part of the CLINIQ project and follows the same license terms.

---

**Note**: This implementation provides a solid foundation for telehealth services. For production use, consider additional security measures, compliance requirements (HIPAA, etc.), and integration with existing healthcare systems.