# config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'pwd-assistant-secret-key-2024'
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp', 'gif'}
    
    # Session lifetime
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # YouTube API (optional)
    YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY') or 'AIzaSyC5QkXoeKQsJG2h2EPODipskalKHEPa3J8'

    # Gemini API (optional, for AI chatbot)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY') or 'AIzaSyC5V3NI2cOdbjY39GxeNKbTR2iBhO5xEBY'