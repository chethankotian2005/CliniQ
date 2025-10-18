"""
Gemini AI Chatbot Service for Medical Queries - Fixed Version
"""
import google.generativeai as genai
import os
import json
import time
from django.conf import settings
from typing import Dict, List, Optional

class MedicalChatbotService:
    """Service for handling medical chatbot interactions with predefined responses"""
    
    def __init__(self):
        """Initialize with predefined responses - no API required"""
        self.api_available = False
        self.model = None
        
        # Try to set up API but don't fail if unavailable
        try:
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel("gemini-pro")
                self.api_available = True
        except Exception:
            pass
        
        # Predefined responses that work without API
        self.responses = {
            "chest pain": {
                "response": """🫀 **Chest Pain - Department Recommendations**

**For SEVERE chest pain with difficulty breathing, crushing sensation, or pain radiating to arm/jaw:**
→ **EMERGENCY DEPARTMENT IMMEDIATELY** 🚨

**For mild to moderate chest pain:**
- **Cardiology Department** - Heart-related concerns
- **General Medicine** - Initial evaluation

**When to seek immediate care:**
Call 911 if you experience severe chest pain, especially with shortness of breath.

Would you like help booking an appointment?""",
                "departments": ["Emergency Medicine", "Cardiology", "General Medicine"]
            },
            
            "headache": {
                "response": """🧠 **Headache - Department Recommendations**

**For severe headaches with sudden onset, fever, neck stiffness, or vision changes:**
→ **EMERGENCY DEPARTMENT**

**For regular headaches:**
- **Neurology** - Chronic headaches, migraines
- **General Medicine** - Initial evaluation

**Self-care tips:** Stay hydrated, rest in dark room, appropriate pain relief

Book an appointment if headaches are frequent or severe.""",
                "departments": ["Neurology", "General Medicine"]
            },
            
            "book": {
                "response": """📅 **How to Book an Appointment**

**3 Easy Ways:**
1️⃣ **Online** - Use our patient portal (fastest - instant confirmation + QR code)
2️⃣ **Phone** - Call hospital reception  
3️⃣ **Walk-in** - Visit reception desk

**What you need:** Name, phone number, preferred department

For chest pain: Consider Cardiology or Emergency Medicine departments.""",
                "departments": []
            },
            
            "departments": {
                "response": """🏥 **Available Departments**

**Emergency & Urgent Care:** Emergency Medicine, Urgent Care
**Heart & Circulation:** Cardiology  
**Brain & Nerves:** Neurology
**General Health:** General Medicine
**Bones & Joints:** Orthopedics
**Other:** Dermatology, ENT, Ophthalmology

**Not sure which department?** Start with General Medicine.""",
                "departments": ["General Medicine"]
            }
        }
    
    def get_chat_response(self, user_message: str, conversation_history: List[Dict] = None) -> Dict:
        """Get response using predefined Q&A system"""
        message_lower = user_message.lower()
        
        # Emergency detection first
        if self._is_emergency(message_lower):
            return {
                'success': True,
                'response': """🚨 **EMERGENCY DETECTED** 🚨

For chest pain, difficulty breathing, or serious symptoms:
1. Call 911 immediately
2. Visit Emergency Department
3. Don't delay medical attention

For chest pain: Emergency Medicine or Cardiology departments.""",
                'type': 'emergency',
                'emergency_detected': True
            }
        
        # Find matching response
        for keyword, data in self.responses.items():
            if keyword in message_lower:
                return {
                    'success': True,
                    'response': data['response'],
                    'type': self._get_type(message_lower),
                    'emergency_detected': False,
                    'department_recommendations': data.get('departments', [])
                }
        
        # Default response
        return {
            'success': True,
            'response': """I can help with common health questions:

**Chest pain** → Cardiology or Emergency Medicine
**Headaches** → Neurology or General Medicine  
**Booking** → Use online portal or call reception
**Departments** → We have Cardiology, Neurology, General Medicine, and more

**For emergencies:** Call 911 or visit Emergency Department

What specific concern can I help you with?""",
            'type': 'general',
            'emergency_detected': False
        }
    
    def _is_emergency(self, message: str) -> bool:
        """Check for emergency keywords"""
        emergency_words = ['chest pain', 'heart attack', 'difficulty breathing', 'severe pain']
        return any(word in message for word in emergency_words)
    
    def _get_type(self, message: str) -> str:
        """Get message type"""
        if 'book' in message:
            return 'booking'
        elif any(word in message for word in ['pain', 'hurt', 'sick']):
            return 'symptoms'
        elif 'department' in message:
            return 'services'
        return 'general'
    
    def get_department_recommendations(self, symptoms: str) -> List[Dict]:
        """Get department recommendations"""
        symptoms_lower = symptoms.lower()
        
        if 'chest' in symptoms_lower or 'heart' in symptoms_lower:
            return [
                {"department": "Cardiology", "reason": "Heart-related concerns", "priority": "high"},
                {"department": "Emergency Medicine", "reason": "Immediate evaluation", "priority": "high"}
            ]
        elif 'head' in symptoms_lower:
            return [
                {"department": "Neurology", "reason": "Headache specialist", "priority": "high"}
            ]
        else:
            return [
                {"department": "General Medicine", "reason": "Initial evaluation", "priority": "medium"}
            ]