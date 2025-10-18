"""
Gemini AI Chatbot Service for Medical Queries
"""
import google.generativeai as genai
import os
import json
import time
from django.conf import settings
from typing import Dict, List, Optional

class MedicalChatbotService:
    """Service for handling medical chatbot interactions using Gemini AI"""
    
    def __init__(self):
        """Initialize the Gemini AI client with fallback to predefined responses"""
        # Get API key from environment variables
        api_key = os.environ.get('GEMINI_API_KEY')
        self.api_available = False
        
        try:
            if api_key:
                genai.configure(api_key=api_key)
                # Configure the model
                self.model = genai.GenerativeModel(
                    model_name="gemini-pro",
                    generation_config={
                        "temperature": 0.7,
                        "top_p": 0.8,
                        "top_k": 40,
                        "max_output_tokens": 1024,
                    }
                )
                self.api_available = True
            else:
                self.model = None
        except Exception as e:
            print(f"Warning: Gemini API not available: {e}")
            self.model = None
            self.api_available = False
        
        # Predefined Q&A database
        self.predefined_qa = self._load_predefined_responses()

        # Medical context and guidelines
        self.system_prompt = """
        You are a helpful medical assistant chatbot for a hospital appointment booking system called CliniQ. 
        Your role is to:
        
        1. Provide general health information and education
        2. Help patients understand common symptoms and when to seek care
        3. Guide patients through the appointment booking process
        4. Answer questions about hospital services and departments
        5. Provide first aid and emergency guidance when appropriate
        
        Important Guidelines:
        - NEVER provide specific medical diagnoses
        - NEVER prescribe medications
        - ALWAYS recommend consulting with a healthcare professional for serious concerns
        - Encourage booking appointments for proper medical evaluation
        - Provide clear, empathetic, and helpful responses
        - If asked about emergency symptoms, advise immediate medical attention
        - Keep responses concise but informative
        - Maintain a professional yet friendly tone
        
        If someone describes emergency symptoms (chest pain, difficulty breathing, severe allergic reactions, etc.), 
        immediately advise them to call emergency services or visit the emergency department.
        """
    
    def _load_predefined_responses(self) -> Dict:
        """Load predefined Q&A responses for common medical queries"""
        return {
            # Chest pain and heart-related
            "chest pain": {
                "response": """🫀 **Chest Pain - Department Recommendations**

**For SEVERE chest pain with:**
- Difficulty breathing
- Crushing sensation
- Pain radiating to arm/jaw
- Sweating, nausea
→ **EMERGENCY DEPARTMENT IMMEDIATELY** 🚨

**For mild to moderate chest pain:**
- **Cardiology Department** - Heart-related concerns
- **General Medicine** - Initial evaluation
- **Pulmonology** - If related to breathing

**When to seek immediate care:**
Call 911 if you experience severe chest pain, especially with shortness of breath.

Would you like help booking an appointment?""",
                "department_recommendations": [
                    {"department": "Emergency Medicine", "reason": "For severe symptoms", "priority": "high"},
                    {"department": "Cardiology", "reason": "Heart-related chest pain", "priority": "high"},
                    {"department": "General Medicine", "reason": "Initial evaluation", "priority": "medium"}
                ]
            },
            
            "heart pain": {
                "response": """🫀 **Heart Pain - Immediate Guidance**

**URGENT - Go to Emergency if you have:**
- Severe crushing chest pain
- Pain spreading to arm, jaw, or back
- Shortness of breath
- Cold sweats, nausea

**For concerning heart symptoms:**
- **Cardiology Department** - Specialized heart care
- **Emergency Medicine** - Immediate evaluation

**Don't wait** - heart symptoms can be serious. When in doubt, seek immediate medical attention.

Would you like me to help you book an urgent appointment?""",
                "department_recommendations": [
                    {"department": "Emergency Medicine", "reason": "Immediate heart symptom evaluation", "priority": "high"},
                    {"department": "Cardiology", "reason": "Specialized heart care", "priority": "high"}
                ]
            },
            
            # Common symptoms
            "headache": {
                "response": """🧠 **Headache - Department Recommendations**

**For severe headaches with:**
- Sudden onset ("worst headache of life")
- Fever, neck stiffness
- Vision changes, confusion
→ **EMERGENCY DEPARTMENT**

**For regular headaches:**
- **Neurology** - Chronic headaches, migraines
- **General Medicine** - Initial evaluation
- **ENT** - If related to sinus issues

**Self-care tips:**
- Stay hydrated
- Rest in dark, quiet room
- Over-the-counter pain relief as directed

Book an appointment if headaches are frequent or severe.""",
                "department_recommendations": [
                    {"department": "Neurology", "reason": "Specialized headache care", "priority": "high"},
                    {"department": "General Medicine", "reason": "Initial headache evaluation", "priority": "medium"},
                    {"department": "ENT", "reason": "Sinus-related headaches", "priority": "low"}
                ]
            },
            
            "fever": {
                "response": """🌡️ **Fever - Care Guidelines**

**High fever (104°F/40°C or higher):**
→ **EMERGENCY DEPARTMENT**

**Fever with concerning symptoms:**
- Difficulty breathing
- Severe headache
- Stiff neck
- Persistent vomiting
→ **Emergency care needed**

**For mild to moderate fever:**
- **General Medicine** - Most fevers
- **Pediatrics** - Children under 18
- **Internal Medicine** - Adult care

**Home care:**
- Rest and fluids
- Fever reducers as appropriate
- Monitor temperature

Seek care if fever persists over 3 days or worsens.""",
                "department_recommendations": [
                    {"department": "General Medicine", "reason": "Most fever cases", "priority": "medium"},
                    {"department": "Pediatrics", "reason": "Children under 18", "priority": "medium"},
                    {"department": "Emergency Medicine", "reason": "High fever or severe symptoms", "priority": "high"}
                ]
            },
            
            # Booking and general questions
            "how to book": {
                "response": """📅 **How to Book an Appointment**

**3 Easy Ways to Book:**

1️⃣ **Online Booking** (Recommended)
   - Visit our patient portal
   - Select department and doctor
   - Choose available time slot
   - Receive QR code for check-in

2️⃣ **Phone Booking**
   - Call hospital reception
   - Speak with booking staff
   - Get confirmation details

3️⃣ **Walk-in Booking**
   - Visit hospital reception
   - Book on-site
   - Get immediate assistance

**What you'll need:**
- Patient name and phone number
- Preferred department
- Any specific doctor preference

**Online booking is fastest** - you get instant confirmation and QR code!""",
                "department_recommendations": []
            },
            
            "departments": {
                "response": """🏥 **Available Departments**

**Emergency & Urgent Care:**
- Emergency Medicine
- Urgent Care

**Medical Specialties:**
- Cardiology (Heart)
- Neurology (Brain/Nervous system)
- Gastroenterology (Digestive)
- Pulmonology (Lungs)

**Other Services:**
- General Medicine
- Dermatology (Skin)
- Ophthalmology (Eyes)
- ENT (Ear, Nose, Throat)

**Not sure which department?** 
Start with General Medicine - they can refer you to the right specialist.""",
                "department_recommendations": [
                    {"department": "General Medicine", "reason": "Best starting point for most conditions", "priority": "medium"}
                ]
            }
        }
    
    def _find_best_predefined_response(self, user_message: str) -> Dict:
        """Find the best matching predefined response"""
        message_lower = user_message.lower()
        
        # Direct keyword matching
        for keyword, response_data in self.predefined_qa.items():
            if keyword in message_lower:
                return {
                    'success': True,
                    'response': response_data['response'],
                    'type': self._categorize_response(user_message),
                    'suggestions': self._get_follow_up_suggestions(user_message),
                    'emergency_detected': self._detect_emergency(user_message),
                    'department_recommendations': response_data.get('department_recommendations', []),
                    'source': 'predefined'
                }
        
        # Symptom-based matching
        symptom_keywords = {
            'chest pain': ['chest', 'heart pain', 'cardiac'],
            'headache': ['head', 'migraine'],
            'fever': ['fever', 'temperature', 'hot']
        }
        
        for main_keyword, synonyms in symptom_keywords.items():
            if any(synonym in message_lower for synonym in synonyms):
                if main_keyword in self.predefined_qa:
                    response_data = self.predefined_qa[main_keyword]
                    return {
                        'success': True,
                        'response': response_data['response'],
                        'type': self._categorize_response(user_message),
                        'suggestions': self._get_follow_up_suggestions(user_message),
                        'emergency_detected': self._detect_emergency(user_message),
                        'department_recommendations': response_data.get('department_recommendations', []),
                        'source': 'predefined'
                    }
        
        # Service-related matching
        service_keywords = {
            'how to book': ['book', 'appointment', 'schedule'],
            'departments': ['department', 'specialist']
        }
        
        for main_keyword, synonyms in service_keywords.items():
            if any(synonym in message_lower for synonym in synonyms):
                if main_keyword in self.predefined_qa:
                    response_data = self.predefined_qa[main_keyword]
                    return {
                        'success': True,
                        'response': response_data['response'],
                        'type': self._categorize_response(user_message),
                        'suggestions': self._get_follow_up_suggestions(user_message),
                        'emergency_detected': self._detect_emergency(user_message),
                        'department_recommendations': response_data.get('department_recommendations', []),
                        'source': 'predefined'
                    }
        
        # Default response if no match found
        return {
            'success': True,
            'response': """I understand you have a health concern. Here are some helpful options:

**For specific symptoms:**
- Chest pain → Cardiology or Emergency Medicine
- Headaches → Neurology or General Medicine  
- Other symptoms → General Medicine

**To book an appointment:**
1. Use our online booking system
2. Call hospital reception
3. Visit in person

**For emergencies:** Call 911 or visit our Emergency Department.

What specific symptoms or concerns would you like help with?""",
            'type': 'general',
            'suggestions': [
                'Tell me about your specific symptoms',
                'How can I book an appointment?',
                'What departments are available?'
            ],
            'emergency_detected': False,
            'department_recommendations': [
                {"department": "General Medicine", "reason": "Best starting point for evaluation", "priority": "medium"}
            ],
            'source': 'default'
        }

    def get_chat_response(self, user_message: str, conversation_history: List[Dict] = None) -> Dict:
        """
        Get response from predefined Q&A or Gemini AI with retry logic
        
        Args:
            user_message: User's message/question
            conversation_history: Previous conversation context
            
        Returns:
            Dict with response and metadata
        """
        # First, try to find a predefined response (faster and more reliable)
        predefined_response = self._find_best_predefined_response(user_message)
        
        # If we found a good predefined match, use it
        if predefined_response.get('source') in ['predefined', 'default']:
            return predefined_response
        
        # If no predefined response and API is not available, use fallback
        if not self.api_available or not self.model:
            return self._get_fallback_response(user_message)
        
        # Handle emergency keywords first (no API call needed)
        if self._detect_emergency(user_message):
            return {
                'success': True,
                'response': self._get_emergency_response(user_message),
                'type': 'emergency',
                'suggestions': ['Call emergency services immediately', 'Visit nearest emergency room'],
                'emergency_detected': True,
                'source': 'emergency_detection'
            }
        
        # Try Gemini API with minimal retry since we have good fallbacks
        try:
            # Build conversation context
            conversation_text = self.system_prompt + "\n\n"
            conversation_text += f"User: {user_message}\nAssistant:"
            
            # Generate response
            response = self.model.generate_content(conversation_text)
            
            # Process response
            if response.text:
                return {
                    'success': True,
                    'response': response.text.strip(),
                    'type': self._categorize_response(user_message),
                    'suggestions': self._get_follow_up_suggestions(user_message),
                    'emergency_detected': self._detect_emergency(user_message),
                    'source': 'gemini_api'
                }
        except Exception as e:
            print(f"API error: {e}, using predefined responses")
        
        # Use fallback for any issues
        return self._get_fallback_response(user_message)
    
    def _get_emergency_response(self, user_message: str) -> str:
        """Get immediate emergency response for critical symptoms"""
        return """🚨 EMERGENCY DETECTED 🚨

For chest pain, difficulty breathing, or other serious symptoms:

1. Call emergency services immediately (911/108)
2. Visit the nearest emergency department
3. Do not delay seeking immediate medical attention

This is a potential medical emergency that requires immediate professional care.

For chest pain specifically:
- Cardiology Department for heart-related concerns
- Emergency Medicine for immediate evaluation

Please seek immediate medical attention. This chatbot cannot replace emergency medical care."""
    
    def _get_fallback_response(self, user_message: str) -> Dict:
        """Get fallback response when AI service is unavailable"""
        query_type = self._categorize_response(user_message)
        
        fallback_responses = {
            'emergency': """🚨 EMERGENCY DETECTED 🚨
            
For chest pain or other serious symptoms, please:
1. Call emergency services immediately
2. Visit nearest emergency department  
3. Seek immediate medical attention

For chest pain: Visit Cardiology or Emergency Medicine department.""",
            
            'symptoms': """I'm currently experiencing technical difficulties with the AI service.

For chest pain specifically, I recommend:
- **Cardiology Department** - for heart-related chest pain
- **Emergency Medicine** - for immediate evaluation
- **General Medicine** - for initial assessment

Please book an appointment or visit our emergency department if symptoms are severe.""",
            
            'booking': """I'm currently unable to access the AI assistant, but I can still help with basic information.

To book an appointment:
1. Use our online booking system
2. Call hospital reception
3. Visit in person

For chest pain, consider Cardiology or Emergency Medicine departments.""",
            
            'services': """Our main departments include:
- Cardiology (heart conditions)
- Emergency Medicine (urgent care)
- General Medicine (general health)
- And many other specialties

For chest pain, Cardiology or Emergency Medicine would be most appropriate."""
        }
        
        return {
            'success': True,
            'response': fallback_responses.get(query_type, fallback_responses['services']),
            'type': query_type,
            'suggestions': self._get_follow_up_suggestions(user_message),
            'emergency_detected': self._detect_emergency(user_message),
            'fallback_used': True
        }
    
    def _categorize_response(self, user_message: str) -> str:
        """Categorize the type of user query"""
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ['book', 'appointment', 'schedule', 'visit']):
            return 'booking'
        elif any(word in message_lower for word in ['emergency', 'urgent', 'chest pain', 'breathing', 'severe']):
            return 'emergency'
        elif any(word in message_lower for word in ['symptom', 'pain', 'fever', 'headache', 'cough']):
            return 'symptoms'
        elif any(word in message_lower for word in ['department', 'doctor', 'specialist', 'service']):
            return 'services'
        else:
            return 'general'
    
    def _detect_emergency(self, user_message: str) -> bool:
        """Detect if user message contains emergency keywords"""
        emergency_keywords = [
            'chest pain', 'can\'t breathe', 'difficulty breathing', 'heart attack',
            'stroke', 'severe bleeding', 'unconscious', 'overdose',
            'severe allergic reaction', 'choking', 'severe burn', 'seizure'
        ]
        
        message_lower = user_message.lower()
        return any(keyword in message_lower for keyword in emergency_keywords)
    
    def _get_follow_up_suggestions(self, user_message: str) -> List[str]:
        """Get relevant follow-up suggestions based on user query"""
        query_type = self._categorize_response(user_message)
        
        suggestions = {
            'booking': [
                "Would you like to see available doctors in a specific department?",
                "Do you need help choosing the right department for your concern?",
                "Would you like to know about our appointment booking process?"
            ],
            'symptoms': [
                "Would you like to book an appointment to discuss these symptoms?",
                "Do you need information about which department to visit?",
                "Would you like first aid tips for managing symptoms?"
            ],
            'emergency': [
                "Should I help you find the nearest emergency department?",
                "Do you need ambulance contact information?",
                "Would you like emergency first aid instructions?"
            ],
            'services': [
                "Would you like to see our list of available departments?",
                "Do you need information about specific doctors?",
                "Would you like to know about our hospital facilities?"
            ],
            'general': [
                "Do you have any specific health concerns to discuss?",
                "Would you like to book an appointment?",
                "Do you need information about our services?"
            ]
        }
        
        return suggestions.get(query_type, suggestions['general'])
    
    def get_department_recommendations(self, symptoms: str) -> List[Dict]:
        """Get department recommendations based on symptoms"""
        try:
            # Use predefined recommendations for common symptoms
            symptoms_lower = symptoms.lower()
            
            if 'chest' in symptoms_lower or 'heart' in symptoms_lower:
                return [
                    {"department": "Cardiology", "reason": "Heart-related chest pain", "priority": "high"},
                    {"department": "Emergency Medicine", "reason": "Immediate evaluation", "priority": "high"},
                    {"department": "General Medicine", "reason": "Initial assessment", "priority": "medium"}
                ]
            elif 'head' in symptoms_lower:
                return [
                    {"department": "Neurology", "reason": "Specialized headache care", "priority": "high"},
                    {"department": "General Medicine", "reason": "Initial evaluation", "priority": "medium"}
                ]
            else:
                return [
                    {"department": "General Medicine", "reason": "Initial evaluation and diagnosis", "priority": "high"}
                ]
                
        except Exception as e:
            print(f"Error getting department recommendations: {e}")
            return [
                {"department": "General Medicine", "reason": "Initial evaluation and diagnosis", "priority": "high"}
            ]