# """
# API Blueprint – All REST endpoints including chatbot, YouTube search, TTS,
# and OCR certificate analysis.
# """
# from flask import Blueprint, request, jsonify, Response, current_app
# from services.chatbot_service import ChatbotService
# from services.tts_service import TTSService
# from services.ocr_service import allowed_file, extract_text_from_image, extract_text_from_pdf
# from services.disability_service import classify_disability, extract_disability_details, get_benefits
# import os
# from werkzeug.utils import secure_filename
# import requests

# api_bp = Blueprint('api', __name__)
# chatbot = ChatbotService()
# tts = TTSService()

# # Global variable to store uploaded policy text (simple in‑memory storage)
# policy_text = ""

# # ----------------------------------------------------------------------
# # Existing Endpoints (unchanged)
# # ----------------------------------------------------------------------

# @api_bp.route('/chatbot', methods=['POST'])
# def chatbot_endpoint():
#     """Chatbot API endpoint (original) – uses knowledge base or Gemini."""
#     data = request.json
#     message = data.get('message', '')
#     if not message:
#         return jsonify({'error': 'Message is required'}), 400
#     response = chatbot.get_response(message)
#     return jsonify(response)

# @api_bp.route('/youtube/search', methods=['GET'])
# def youtube_search():
#     """YouTube search API endpoint."""
#     query = request.args.get('query', '')
#     if not query:
#         return jsonify({'error': 'Query is required'}), 400
#     search_query = f"{query} disability India support"
#     # Mock response – replace with actual YouTube API call if key is set
#     mock_videos = [
#         {
#             'title': 'Disability Rights in India - Complete Guide',
#             'videoId': 'dQw4w9WgXcQ',
#             'channel': 'Rights Channel'
#         },
#         {
#             'title': 'Understanding PwD Act 2016',
#             'videoId': 'dQw4w9WgXcQ',
#             'channel': 'Legal Awareness'
#         }
#     ]
#     return jsonify({'videos': mock_videos, 'query': search_query})

# @api_bp.route('/analyze/certificate', methods=['POST'])
# def analyze_certificate():
#     """Mock certificate analysis endpoint."""
#     return jsonify({
#         'success': True,
#         'analysis': {
#             'disability_type': 'Visual Impairment',
#             'severity': 'Moderate (40-70%)',
#             'recommendations': 'Screen reader software, Braille training'
#         }
#     })

# @api_bp.route('/tts', methods=['POST'])
# def text_to_speech():
#     """
#     Convert text to speech using gTTS (later replace with Hugging Face).
#     Returns MP3 audio.
#     """
#     data = request.get_json(silent=True) or {}
#     text = data.get('text', '').strip()
#     lang = data.get('lang', 'en')
#     if not text:
#         return jsonify({'error': 'text is required'}), 400
#     audio_bytes = tts.generate_audio(text, lang=lang)
#     if audio_bytes is None:
#         return jsonify({'error': 'Audio generation failed'}), 500
#     return Response(
#         audio_bytes,
#         mimetype='audio/mpeg',
#         headers={
#             'Content-Disposition': 'inline; filename="response.mp3"',
#             'Cache-Control': 'no-cache'
#         }
#     )

# # ----------------------------------------------------------------------
# # New OCR Endpoints (migrated from monolithic app.py)
# # ----------------------------------------------------------------------

# @api_bp.route('/upload', methods=['POST'])
# def upload_certificate():
#     """
#     Upload a disability certificate (image or PDF), extract text via OCR,
#     classify disability type, and return benefits.
#     """
#     if 'file' not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "Empty file"}), 400

#     if not allowed_file(file.filename):
#         return jsonify({"error": "Unsupported file type"}), 400

#     # Save file securely
#     filename = secure_filename(file.filename)
#     filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
#     file.save(filepath)

#     # Extract text based on file extension
#     ext = filename.rsplit('.', 1)[1].lower()
#     if ext == 'pdf':
#         text = extract_text_from_pdf(filepath)
#     else:
#         text = extract_text_from_image(filepath)

#     # If insufficient text, return helpful error
#     if not text or len(text.strip()) < 20:
#         return jsonify({
#             "type": "No Text Found",
#             "info": "Could not extract text from the document. The image might be blurry, low resolution, or handwritten. Please upload a clear, typed certificate.",
#             "percentage": None
#         })

#     # Classify disability and get details
#     disability_type = classify_disability(text)
#     details = extract_disability_details(text)
#     benefits = get_benefits(disability_type)

#     response = {
#         "type": disability_type.replace("_", " ").title(),
#         "info": " | ".join(benefits),
#         "percentage": details["percentage"]
#     }
#     if details.get("diagnosis"):
#         response["diagnosis"] = details["diagnosis"][:100]

#     return jsonify(response)


# @api_bp.route('/upload_policy', methods=['POST'])
# def upload_policy():
#     """
#     Upload a government policy/scheme PDF, extract its text,
#     and store it globally for the chatbot to query.
#     """
#     global policy_text
#     if 'file' not in request.files:
#         return jsonify({"error": "No file uploaded"}), 400

#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "Empty file"}), 400

#     if not file.filename.lower().endswith('.pdf'):
#         return jsonify({"error": "Only PDF files are allowed"}), 400

#     filename = secure_filename(file.filename)
#     filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
#     file.save(filepath)

#     text = extract_text_from_pdf(filepath)
#     if not text:
#         policy_text = ""
#         return jsonify({"error": "Could not extract text from PDF. It may be scanned or image-based."}), 400

#     policy_text = text
#     return jsonify({"message": "Policy uploaded successfully!", "length": len(text)})


# @api_bp.route('/chatbot_policy', methods=['POST'])   # Note: different route from the original /chatbot
# def chatbot_policy_query():
#     """
#     Answer questions based on the uploaded policy PDF using simple keyword search.
#     This endpoint is used by the NGO analyze page.
#     """
#     global policy_text
#     data = request.get_json()
#     query = data.get('query', '').lower()
#     if not policy_text:
#         return jsonify({"reply": "Please upload a policy PDF first to enable question answering."})

#     # Split into sentences (by period)
#     sentences = policy_text.split('.')
#     keywords = query.split()
#     results = []
#     for sent in sentences:
#         sent_lower = sent.lower()
#         if any(keyword in sent_lower for keyword in keywords):
#             results.append(sent.strip())

#     if results:
#         # Return up to 3 relevant sentences
#         reply = ". ".join(results[:3]) + "."
#     else:
#         reply = "Sorry, no relevant information found in the uploaded policy."

#     return jsonify({"reply": reply})

"""
API Blueprint – All REST endpoints including chatbot, YouTube search, TTS,
OCR certificate analysis, and voice assistant (STT + TTS).
"""
from flask import Blueprint, request, jsonify, Response, current_app
from services.chatbot_service import ChatbotService
from services.tts_service import TTSService               # Original gTTS service (fallback)
from services.ocr_service import allowed_file, extract_text_from_image, extract_text_from_pdf
from services.disability_service import classify_disability, extract_disability_details, get_benefits
from services.certificate_authenticity import predict_certificate_authenticity
from services.voice_service import VoiceService           # NEW: Whisper + Kokoro
import os
from werkzeug.utils import secure_filename
import requests

api_bp = Blueprint('api', __name__)
chatbot = ChatbotService()
tts = TTSService()                 # Kept for backward compatibility (uses gTTS)
voice = VoiceService()             # NEW: lightweight local voice models


from services.voice_service import VoiceService

# Initialize voice service
voice = VoiceService()

@api_bp.route('/voice/speak', methods=['POST'])
def voice_speak():
    """Text-to-Speech using Hugging Face model. Returns MP3 audio."""
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    audio_bytes = voice.synthesize_speech(text)
    if audio_bytes is None:
        return jsonify({'error': 'TTS generation failed'}), 500
    return Response(audio_bytes, mimetype='audio/mpeg', headers={
        'Content-Disposition': 'inline; filename="speech.mp3"',
        'Cache-Control': 'no-cache'
    })

@api_bp.route('/voice/transcribe', methods=['POST'])
def voice_transcribe():
    """Speech-to-Text using Hugging Face Whisper. Expects audio file."""
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400
    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({'error': 'Empty audio file'}), 400
    text = voice.transcribe_audio(audio_file)
    if text is None:
        return jsonify({'error': 'Transcription failed'}), 500
    return jsonify({'text': text})
# Global variable to store uploaded policy text (in‑memory)
policy_text = ""

# ----------------------------------------------------------------------
# Existing Endpoints (unchanged)
# ----------------------------------------------------------------------

@api_bp.route('/chatbot', methods=['POST'])
def chatbot_endpoint():
    """Chatbot API endpoint (original) – uses knowledge base or Gemini."""
    data = request.json
    message = data.get('message', '')
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    response = chatbot.get_response(message)
    return jsonify(response)

@api_bp.route('/youtube/search', methods=['GET'])
def youtube_search():
    """YouTube search API endpoint."""
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'Query is required'}), 400
    search_query = f"{query} disability India support"
    # Mock response – replace with actual YouTube API call if key is set
    mock_videos = [
        {
            'title': 'Disability Rights in India - Complete Guide',
            'videoId': 'dQw4w9WgXcQ',
            'channel': 'Rights Channel'
        },
        {
            'title': 'Understanding PwD Act 2016',
            'videoId': 'dQw4w9WgXcQ',
            'channel': 'Legal Awareness'
        }
    ]
    return jsonify({'videos': mock_videos, 'query': search_query})

@api_bp.route('/analyze/certificate', methods=['POST'])
def analyze_certificate():
    """Mock certificate analysis endpoint."""
    return jsonify({
        'success': True,
        'analysis': {
            'disability_type': 'Visual Impairment',
            'severity': 'Moderate (40-70%)',
            'recommendations': 'Screen reader software, Braille training'
        }
    })

@api_bp.route('/tts', methods=['POST'])
def text_to_speech():
    """
    Convert text to speech using gTTS (legacy endpoint).
    Returns MP3 audio.
    """
    data = request.get_json(silent=True) or {}
    text = data.get('text', '').strip()
    lang = data.get('lang', 'en')
    if not text:
        return jsonify({'error': 'text is required'}), 400
    audio_bytes = tts.generate_audio(text, lang=lang)
    if audio_bytes is None:
        return jsonify({'error': 'Audio generation failed'}), 500
    return Response(
        audio_bytes,
        mimetype='audio/mpeg',
        headers={
            'Content-Disposition': 'inline; filename="response.mp3"',
            'Cache-Control': 'no-cache'
        }
    )

# ----------------------------------------------------------------------
# OCR Endpoints (migrated from monolithic app.py)
# ----------------------------------------------------------------------

@api_bp.route('/upload', methods=['POST'])
def upload_certificate():
    """
    Upload a disability certificate (image or PDF), extract text via OCR,
    predict authenticity, classify disability type, and return benefits.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    # Save file securely
    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Extract text based on file extension
    ext = filename.rsplit('.', 1)[1].lower()
    if ext == 'pdf':
        text = extract_text_from_pdf(filepath)
    else:
        text = extract_text_from_image(filepath)

    # If insufficient text, return helpful error
    if not text or len(text.strip()) < 20:
        return jsonify({
            "type": "No Text Found",
            "info": "Could not extract text from the document. The image might be blurry, low resolution, or handwritten. Please upload a clear, typed certificate.",
            "percentage": None
        })

    # Predict certificate authenticity before analysis
    authenticity = predict_certificate_authenticity(text, filename=filename)

    # Classify disability and get details
    disability_type = classify_disability(text)
    details = extract_disability_details(text)
    benefits = get_benefits(disability_type)

    response = {
        "type": disability_type.replace("_", " ").title(),
        "info": " | ".join(benefits),
        "percentage": details["percentage"],
        "authenticity": authenticity
    }
    if details.get("diagnosis"):
        response["diagnosis"] = details["diagnosis"][:100]

    if authenticity["label"] == "Fake":
        response["warning"] = "Certificate appears likely fake. Please verify the original document manually before relying on the analysis."

    return jsonify(response)


@api_bp.route('/upload_policy', methods=['POST'])
def upload_policy():
    """
    Upload a government policy/scheme PDF, extract its text,
    and store it globally for the chatbot to query.
    """
    global policy_text
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Empty file"}), 400

    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    text = extract_text_from_pdf(filepath)
    if not text:
        policy_text = ""
        return jsonify({"error": "Could not extract text from PDF. It may be scanned or image-based."}), 400

    policy_text = text
    return jsonify({"message": "Policy uploaded successfully!", "length": len(text)})


@api_bp.route('/chatbot_policy', methods=['POST'])
def chatbot_policy_query():
    """
    Answer questions based on the uploaded policy PDF using Gemini AI.
    """
    global policy_text
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not policy_text:
        return jsonify({"reply": "Please upload a policy PDF first to enable question answering."})
    if not query:
        return jsonify({"error": "Please provide a question."})

    try:
        import os
        import google.generativeai as genai
        
        api_key = os.environ.get('GEMINI_API_KEY')
        if not api_key:
            return jsonify({"error": "Gemini API key is missing."})
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-flash-latest')
        
        # Limit text to ~100k chars to avoid massive payloads, though Flash handles more.
        context_text = policy_text[:100000]
        
        prompt = (
            f"You are a helpful assistant for persons with disabilities.\n"
            f"Here is the text of a government policy/scheme document:\n"
            f"----------------------------------------\n"
            f"{context_text}\n"
            f"----------------------------------------\n"
            f"Based ONLY on the document above, answer the following question clearly and concisely.\n"
            f"If the document does not contain the answer, politely say that the information is not present in the uploaded document.\n\n"
            f"Question: {query}"
        )
        
        response = model.generate_content(prompt)
        reply = response.text.strip() if response.text else "Sorry, I could not generate an answer."
        
        return jsonify({"reply": reply})
        
    except Exception as e:
        print(f"Policy Chatbot Error: {e}")
        return jsonify({"error": f"AI processing error: {str(e)}"})

# ----------------------------------------------------------------------
# NEW Voice Assistant Endpoints (Phase 3)
# ----------------------------------------------------------------------

@api_bp.route('/voice/transcribe', methods=['POST'])
def transcribe_audio():
    """
    Speech‑to‑Text endpoint.
    Accepts an audio file (WebM, WAV, MP3, etc.) and returns the transcribed text.
    Uses Whisper tiny model – lightweight and fast.
    """
    if 'audio' not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files['audio']
    if audio_file.filename == '':
        return jsonify({"error": "Empty audio file"}), 400

    try:
        transcribed_text = voice.transcribe_audio(audio_file)
        return jsonify({"text": transcribed_text})
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500


@api_bp.route('/voice/speak', methods=['POST'])
def synthesize_speech():
    """
    Text‑to‑Speech endpoint.
    Accepts JSON with 'text' and returns MP3 audio.
    Uses Kokoro lightweight TTS model – no external API calls.
    """
    data = request.get_json(silent=True) or {}
    text = data.get('text', '').strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    audio_bytes = voice.synthesize_speech(text)
    if audio_bytes is None:
        return jsonify({"error": "Speech synthesis failed"}), 500

    return Response(
        audio_bytes,
        mimetype='audio/mpeg',
        headers={
            'Content-Disposition': 'inline; filename="speech.mp3"',
            'Cache-Control': 'no-cache'
        }
    )