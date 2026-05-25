# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
"""
OCR Service – Extracts text from images and PDFs using Tesseract and pdfplumber.
"""
import os
import re
import pytesseract
from PIL import Image, ImageEnhance
import pdfplumber
from flask import current_app

# Allowed file extensions
ALLOWED_EXT = {"pdf", "png", "jpg", "jpeg", "tiff", "bmp", "gif"}

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT

def extract_text_from_image(path):
    """
    Extract text from an image using Gemini API since Tesseract is not installed.
    """
    try:
        import os
        import google.generativeai as genai
        from PIL import Image
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            print("GEMINI_API_KEY not found. OCR cannot proceed without Tesseract or Gemini.")
            return ""
            
        genai.configure(api_key=api_key)
        # Use gemini-flash-latest for fast multimodal tasks (avoids quota issues on older aliases)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        image = Image.open(path)
        
        # Prompt Gemini to extract text
        response = model.generate_content([
            "Please act as an OCR system. Extract all the text you can see in this document accurately.", 
            image
        ])
        
        text = response.text if response.text else ""
        return text

    except Exception as e:
        print(f"Gemini OCR image error: {e}")
        return ""

def extract_text_from_pdf(path):
    """
    Extract text from a PDF file using pdfplumber.
    If pages are scanned images, this will return empty – use OCR for those.
    """
    try:
        text_parts = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text_parts.append(t)
        return "\n".join(text_parts)
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def preprocess_text(text):
    """Clean and normalize text: lowercase, collapse whitespace."""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text.strip()