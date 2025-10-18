# SmartQueue Medical App

A comprehensive medical appointment management system built with Django, featuring QR code booking, SMS notifications, real-time updates, and AI-powered medical chatbot.

## Features

- 🏥 **Hospital Management**: Multi-doctor appointment system
- 📱 **QR Code Booking**: Quick appointment booking via QR codes
- 💬 **AI Medical Chatbot**: Powered by Google Gemini AI
- 📧 **SMS Notifications**: Real-time appointment updates via Twilio
- 👨‍⚕️ **Doctor Dashboard**: Manage appointments and patient queues
- 🔄 **Real-time Updates**: Live queue status using WebSockets
- 📋 **Lab Facilities**: Lab test management and scheduling
- 📞 **Teleappointments**: Virtual consultation support

## Tech Stack

- **Backend**: Django 5.2.7, Django REST Framework
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (development) / PostgreSQL (production)
- **Real-time**: Django Channels with WebSockets
- **SMS**: Twilio API
- **AI**: Google Gemini API
- **Authentication**: Firebase Auth (optional)

## Quick Start

### Prerequisites

- Python 3.8+
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smartqueue-medical.git
   cd smartqueue-medical
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   cd medicalapp
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   ```

5. **Configure Environment Variables**
   
   Edit `.env` file with your actual values:
   ```env
   # Django Settings
   SECRET_KEY=your_django_secret_key_here
   DEBUG=True
   
   # Gemini AI API Key for Medical Chatbot
   GEMINI_API_KEY=your_gemini_api_key_here
   
   # Twilio Configuration (for SMS notifications)
   TWILIO_ACCOUNT_SID=your_twilio_account_sid_here
   TWILIO_AUTH_TOKEN=your_twilio_auth_token_here
   TWILIO_PHONE_NUMBER=+1234567890
   ```

6. **Database Setup**
   ```bash
   python manage.py migrate
   python manage.py collectstatic
   ```

7. **Create Admin User**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run the Development Server**
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000` to access the application.

## API Keys Setup

### 1. Google Gemini AI API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Add it to your `.env` file as `GEMINI_API_KEY`

### 2. Twilio SMS Configuration

1. Sign up at [Twilio Console](https://console.twilio.com/)
2. Get your Account SID, Auth Token, and Phone Number
3. Add them to your `.env` file

## Project Structure

```
medicalapp/
├── smartqueue/           # Main Django project
│   ├── settings.py      # Project settings
│   ├── urls.py          # URL routing
│   └── wsgi.py          # WSGI config
├── patients/            # Patient management app
├── doctors/             # Doctor management app
├── adminpanel/          # Admin interface
├── notifications/       # SMS/notification system
├── auth/               # Authentication system
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── media/              # User uploads
├── requirements.txt    # Python dependencies
└── manage.py           # Django management script
```

## Key Features Guide

### QR Code Booking
- Generate QR codes for quick appointment booking
- Scan QR code to book appointment without registration
- Real-time queue position updates

### AI Medical Chatbot
- Powered by Google Gemini AI
- Provides medical information and guidance
- Predefined responses for common queries
- **Note**: Not a replacement for professional medical advice

### SMS Notifications
- Appointment confirmations
- Queue position updates
- Doctor availability notifications
- Appointment reminders

### Doctor Dashboard
- View and manage patient queue
- Update appointment status
- Real-time patient notifications

## Deployment

### Environment Variables for Production

```env
SECRET_KEY=your_production_secret_key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL recommended for production)
DATABASE_URL=postgresql://user:password@localhost:5432/smartqueue

# Security Settings
SECURE_SSL_REDIRECT=True
SECURE_BROWSER_XSS_FILTER=True
SECURE_CONTENT_TYPE_NOSNIFF=True
```

### Production Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Configure proper `ALLOWED_HOSTS`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set up proper static file serving
- [ ] Configure Redis for Channels (WebSocket support)
- [ ] Set up SSL/HTTPS
- [ ] Configure proper logging
- [ ] Set strong `SECRET_KEY`

## API Documentation

### Authentication
Most endpoints require authentication. Use session authentication or Firebase tokens.

### Key Endpoints
- `GET /api/doctors/` - List all doctors
- `POST /api/appointments/` - Create new appointment
- `GET /api/queue/{doctor_id}/` - Get current queue status
- `POST /api/chatbot/` - Send message to AI chatbot

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Errors**
   ```bash
   python manage.py migrate
   ```

3. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic
   ```

4. **SMS Not Working**
   - Check Twilio credentials in `.env`
   - Verify phone number format (+1234567890)
   - Check Twilio account balance

5. **Chatbot Not Responding**
   - Verify `GEMINI_API_KEY` in `.env`
   - Check API quota limits
   - Ensure internet connectivity

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Security

- Never commit `.env` files or API keys
- Use environment variables for all sensitive data
- Keep dependencies updated
- Follow Django security best practices

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the troubleshooting guide above
- Review the documentation in the project files

## Acknowledgments

- Django and Django REST Framework teams
- Twilio for SMS services
- Google for Gemini AI API
- All contributors and testers

---

**⚠️ Medical Disclaimer**: This application is for educational and administrative purposes only. The AI chatbot provides general information and should not be considered as professional medical advice. Always consult with qualified healthcare professionals for medical decisions.