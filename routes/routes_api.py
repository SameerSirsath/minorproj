# routes/api.py
from flask import Blueprint, request, jsonify, Response
from services.chatbot_service import ChatbotService
from services.tts_service import TTSService          # ← NEW import
import requests

api_bp = Blueprint('api', __name__)
chatbot = ChatbotService()
tts     = TTSService()                               # ← NEW instance


# ------------------------------------------------------------------ #
#  Existing endpoints (unchanged)                                      #
# ------------------------------------------------------------------ #

@api_bp.route('/api/chatbot', methods=['POST'])
def chatbot_endpoint():
    """Chatbot API endpoint"""
    data    = request.json
    message = data.get('message', '')
    if not message:
        return jsonify({'error': 'Message is required'}), 400
    response = chatbot.get_response(message)
    return jsonify(response)


@api_bp.route('/api/youtube/search', methods=['GET'])
def youtube_search():
    """YouTube search API endpoint"""
    query = request.args.get('query', '')
    if not query:
        return jsonify({'error': 'Query is required'}), 400

    search_query = f"{query} disability India support"

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


@api_bp.route('/api/analyze/certificate', methods=['POST'])
def analyze_certificate():
    """Analyze disability certificate (mock)"""
    return jsonify({
        'success': True,
        'analysis': {
            'disability_type': 'Visual Impairment',
            'severity': 'Moderate (40-70%)',
            'recommendations': 'Screen reader software, Braille training'
        }
    })


# ------------------------------------------------------------------ #
#  NEW: Text-to-Speech endpoint                                        #
# ------------------------------------------------------------------ #

@api_bp.route('/api/tts', methods=['POST'])
def text_to_speech():
    """
    Convert text to speech using gTTS and return MP3 audio.

    Request JSON:
        {
            "text": "The bot reply to speak aloud",
            "lang": "en"          // optional; 'en' | 'hi' | 'mr'
        }

    Response:
        MP3 audio stream (audio/mpeg)
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
