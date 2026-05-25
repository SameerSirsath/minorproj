import google.generativeai as genai
import os
from typing import Dict, List
import json

class ChatbotService:
    
    def __init__(self):
        self.knowledge_base = self.load_knowledge_base()
        self.setup_gemini()
    
    def setup_gemini(self):
        """Setup Gemini AI (if API key is available)"""
        api_key = os.environ.get('AIzaSyDOQUPocxTz3GRIIAlUkkXqfY92weh7xMA')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
    
    def load_knowledge_base(self) -> Dict:
        """Load PwD knowledge base"""
        return {
            'disabilitydefinitions': {
                'title': 'Disability Definitions - Official Categories',
                'content': 'Official Disability Categories as per Government Guidelines...',
                'category': 'definitions',
                'source': 'Government of India - PwD FAQ',
                'pdfreference': 'Pages 2-3 Official disability definitions'
            },
            'reservationeligibility': {
                'title': 'Reservation Eligibility - 40% Disability Requirement',
                'content': 'Eligibility Criteria for Government Job Reservation...',
                'category': 'reservation',
                'source': 'Government of India - PwD FAQ Q.4 & Q.5',
                'pdfreference': 'Page 3 Q.4 & Q.5 - Disability percentage and certificate authority'
            },
            # Add more knowledge base entries...
        }
    
    def get_response(self, user_message: str) -> Dict:
        """Get chatbot response based on user message"""
        # First check knowledge base
        response = self.check_knowledge_base(user_message)
        
        # If no match in knowledge base and Gemini is available, use AI
        if not response and self.model:
            response = self.get_ai_response(user_message)
        
        # Default response
        if not response:
            response = {
                'title': 'PWD Assistant',
                'content': 'I can help you with disability rights, benefits, and support services. Try asking about specific topics like employment reservations, education benefits, or healthcare schemes.',
                'category': 'general',
                'source': 'PWD Assistant Knowledge Base'
            }
        
        return response
    
    def check_knowledge_base(self, message: str) -> Dict:
        """Check if message matches knowledge base entries"""
        message_lower = message.lower()
        
        keyword_mapping = {
            'blind': 'disabilitydefinitions',
            'blindness': 'disabilitydefinitions',
            'vision': 'disabilitydefinitions',
            'reservation': 'reservationeligibility',
            'job': 'reservationeligibility',
            'employment': 'reservationeligibility',
            # Add more mappings...
        }
        
        for keyword, response_key in keyword_mapping.items():
            if keyword in message_lower:
                return self.knowledge_base.get(response_key)
        
        return None
    
    def get_ai_response(self, message: str) -> Dict:
        """Get AI-generated response using Gemini"""
        if not self.model:
            return None
        
        try:
            prompt = f"""You are PWD Assistant, a helpful AI for Persons with Disabilities in India.
            User query: {message}
            
            Provide accurate, helpful information about PwD rights, benefits, and support services in India.
            Format your response as a clear, structured answer.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                'title': 'AI Assistant Response',
                'content': response.text,
                'category': 'ai_response',
                'source': 'Gemini AI'
            }
        except Exception as e:
            print(f"AI response error: {e}")
            return None