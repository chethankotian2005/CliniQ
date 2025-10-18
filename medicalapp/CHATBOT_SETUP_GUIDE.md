# AI Chatbot & Hospital Portal Setup Guide

## Overview
This guide explains how to set up the new patient portal with AI chatbot functionality and multi-hospital support.

## Features Added

### 1. Patient Portal with Hospital Selection
- **Hospital Selection Page**: Patients can choose from multiple demo hospitals
- **Distance Calculation**: Uses geolocation to show nearby hospitals
- **Hospital Details**: Each hospital has detailed information, departments, and reviews
- **Smart Navigation**: Seamless flow from hospital selection to appointment booking

### 2. Gemini AI Medical Chatbot
- **Medical Assistant**: AI-powered chatbot for answering medical questions
- **Symptom Analysis**: Provides department recommendations based on symptoms
- **Emergency Detection**: Automatically detects emergency situations
- **Contextual Help**: Assists with appointment booking and hospital services

### 3. Enhanced QR Booking System
- **Hospital-specific Booking**: QR codes now include hospital information
- **Multi-hospital Support**: Patients can book at different hospitals
- **Improved Workflow**: Better integration with hospital selection

## Setup Instructions

### 1. Install Required Packages

```bash
# Navigate to project directory
cd medicalapp

# Install new dependencies
pip install google-generativeai>=0.3.0
pip install geopy>=2.4.0

# Or install from updated requirements.txt
pip install -r requirements.txt
```

### 2. Configure Gemini AI API

#### Step 1: Get Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key

#### Step 2: Set Environment Variable
**Windows (PowerShell):**
```powershell
# For current session
$env:GEMINI_API_KEY = "your_api_key_here"

# For permanent (add to system environment variables)
[Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "your_api_key_here", "User")
```

**Linux/Mac:**
```bash
# For current session
export GEMINI_API_KEY="your_api_key_here"

# For permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Database Migration
```bash
# Create migrations for new hospital models
python manage.py makemigrations patients

# Apply migrations
python manage.py migrate
```

### 4. Create Sample Data
The system will automatically create sample hospitals when you first visit the patient portal. Alternatively, you can create them manually:

```python
# Run Django shell
python manage.py shell

# Create sample hospitals
from patients.portal_views import create_sample_hospitals
create_sample_hospitals()
```

### 5. Test the Setup

#### Test Patient Portal
1. Start the server: `python manage.py runserver`
2. Visit: `http://localhost:8000/patients/portal/`
3. You should see 4 demo hospitals

#### Test AI Chatbot
1. On the patient portal page, use the chat interface
2. Try asking: "What department should I visit for chest pain?"
3. The AI should respond with medical advice and department recommendations

#### Test Hospital Booking
1. Click on any hospital
2. View hospital details
3. Click "Book Appointment"
4. Fill the form and complete booking
5. You should receive a QR code

### 6. Configuration Options

#### Customize Hospital Data
Edit `patients/portal_views.py` in the `create_sample_hospitals()` function to modify hospital information.

#### Chatbot Behavior
Modify `patients/chatbot_service.py` to customize:
- System prompts
- Emergency detection keywords
- Department recommendations
- Response formatting

#### Location Services
The system uses geopy for distance calculations. You can customize the distance calculation method in `patients/hospital_models.py`.

## URL Structure

### New Patient Portal URLs
- `/patients/portal/` - Hospital selection page
- `/patients/hospital/<hospital_id>/` - Hospital details
- `/patients/hospital/<hospital_id>/book/` - Hospital-specific booking

### API Endpoints
- `/patients/api/nearby-hospitals/` - Get hospitals by distance
- `/patients/api/chatbot/` - Chat with AI assistant
- `/patients/api/hospital/<hospital_id>/departments/` - Get hospital departments

## Usage Workflow

### For Patients
1. **Visit Patient Portal**: Go to the portal home page
2. **Choose Hospital**: Select from available hospitals (optionally use location services)
3. **Chat with AI**: Ask questions about symptoms or services
4. **View Hospital Details**: See departments, facilities, and reviews
5. **Book Appointment**: Fill form and receive QR code
6. **Visit Hospital**: Scan QR code at reception to get token

### For Hospital Staff
1. **QR Scanner**: Use the QR scanner page to process patient QR codes
2. **Token Assignment**: System automatically assigns tokens when QR is scanned
3. **Queue Management**: Use existing doctor dashboard for queue management

## Troubleshooting

### Common Issues

#### 1. Gemini API Key Not Working
- Verify the API key is correctly set in environment variables
- Check if the API key has proper permissions
- Ensure you have credits/quota available

#### 2. Location Services Not Working
- Ensure HTTPS is used for production (required for geolocation)
- Check browser permissions for location access
- Verify geopy package is installed

#### 3. Hospital Data Not Showing
- Run the sample data creation script
- Check database migrations are applied
- Verify no errors in Django logs

#### 4. Chat Not Responding
- Check Gemini API key configuration
- Look for error messages in browser console
- Verify network connectivity

### Debug Commands
```bash
# Check if Gemini API is working
python manage.py shell
>>> from patients.chatbot_service import MedicalChatbotService
>>> chatbot = MedicalChatbotService()
>>> response = chatbot.get_chat_response("Hello")
>>> print(response)

# Check hospital data
>>> from patients.hospital_models import Hospital
>>> Hospital.objects.all()
```

## Security Considerations

### API Key Security
- Never commit API keys to version control
- Use environment variables or secret management systems
- Rotate API keys regularly
- Monitor API usage and costs

### Data Privacy
- Patient chat conversations are not stored by default
- QR codes contain booking references, not personal data
- Location data is only used for distance calculations

### Rate Limiting
- Gemini API has rate limits - monitor usage
- Implement client-side debouncing for chat
- Consider caching common responses

## Future Enhancements

### Potential Improvements
1. **Multi-language Support**: Add language selection for chatbot
2. **Voice Interface**: Integrate speech-to-text for accessibility
3. **Image Analysis**: Allow patients to upload symptoms photos
4. **Appointment Reminders**: SMS/email reminders with QR codes
5. **Integration**: Connect with hospital management systems
6. **Analytics**: Track chatbot effectiveness and popular queries

### Scaling Considerations
- Consider using Redis for chat session storage
- Implement proper caching for hospital data
- Use CDN for static assets (hospital images)
- Monitor database performance with increased usage

## Support

For issues or questions:
1. Check Django logs for error details
2. Verify all environment variables are set
3. Test API endpoints individually
4. Review browser console for JavaScript errors

The system is now ready to provide an enhanced patient experience with AI assistance and multi-hospital support!