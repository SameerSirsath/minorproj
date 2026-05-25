"""
services/tts_service.py
-----------------------
Voice assistant backend using gTTS (Google Text-to-Speech).
This is a standalone service file — no changes to existing service files needed.

Install dependency:
    pip install gTTS
"""

from gtts import gTTS
import io
import re


class TTSService:
    """
    Converts chatbot text responses to MP3 audio using Google TTS.
    Supports English (en) and Hindi (hi) out of the box.
    """

    SUPPORTED_LANGS = {
        'en': 'English',
        'hi': 'Hindi',
        'mr': 'Marathi',
    }

    def __init__(self):
        pass

    def clean_text(self, text: str) -> str:
        """Strip HTML tags and clean text before passing to TTS."""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove special characters that sound bad when read aloud
        text = re.sub(r'[*_`#]', '', text)
        return text

    def generate_audio(self, text: str, lang: str = 'en') -> bytes | None:
        """
        Generate MP3 audio bytes from text.

        Args:
            text: The text to convert to speech.
            lang: Language code ('en', 'hi', 'mr'). Defaults to 'en'.

        Returns:
            MP3 audio as bytes, or None on failure.
        """
        if not text or not text.strip():
            return None

        # Sanitise language code
        if lang not in self.SUPPORTED_LANGS:
            lang = 'en'

        clean = self.clean_text(text)
        if not clean:
            return None

        # gTTS has a max ~5000 chars; truncate gracefully
        if len(clean) > 4000:
            clean = clean[:4000] + '.'

        try:
            tts = gTTS(text=clean, lang=lang, slow=False)
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            buffer.seek(0)
            return buffer.read()
        except Exception as e:
            print(f"[TTSService] Error generating audio: {e}")
            return None
