import requests
import os
import io
import tempfile
from pydub import AudioSegment

class VoiceService:
    def __init__(self):
        self.hf_token = os.environ.get('HF_API_TOKEN')
        if not self.hf_token:
            print("WARNING: HF_API_TOKEN not set. Voice service will fail.")
        # TTS endpoint (English)
        self.tts_url = "https://api-inference.huggingface.co/models/facebook/mms-tts-eng"
        # STT endpoint (Whisper small)
        self.stt_url = "https://api-inference.huggingface.co/models/openai/whisper-small"
        self.headers = {"Authorization": f"Bearer {self.hf_token}"} if self.hf_token else {}

    def synthesize_speech(self, text: str) -> bytes | None:
        """Convert text to MP3 using Hugging Face TTS model."""
        if not self.hf_token:
            return None
        try:
            payload = {"inputs": text}
            response = requests.post(self.tts_url, headers=self.headers, json=payload)
            if response.status_code != 200:
                print(f"TTS error: {response.status_code} - {response.text}")
                return None
            # The model returns WAV audio; convert to MP3 for smaller size
            wav_io = io.BytesIO(response.content)
            audio = AudioSegment.from_wav(wav_io)
            mp3_io = io.BytesIO()
            audio.export(mp3_io, format="mp3")
            mp3_io.seek(0)
            return mp3_io.read()
        except Exception as e:
            print(f"TTS exception: {e}")
            return None

    def transcribe_audio(self, audio_file) -> str | None:
        """Transcribe audio file to text using Hugging Face Whisper model."""
        if not self.hf_token:
            return None
        try:
            # Read file bytes
            audio_bytes = audio_file.read()
            # Whisper expects the file as multipart/form-data
            files = {"audio": audio_bytes}
            response = requests.post(self.stt_url, headers=self.headers, files=files)
            if response.status_code != 200:
                print(f"STT error: {response.status_code} - {response.text}")
                return None
            result = response.json()
            return result.get("text", "")
        except Exception as e:
            print(f"STT exception: {e}")
            return None  