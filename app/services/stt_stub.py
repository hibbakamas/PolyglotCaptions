# app/services/stt_stub.py
from app.config import settings


def fake_transcribe(audio_bytes: bytes, from_lang: str) -> str:
    lang = (from_lang or "en").lower()
    return settings.sample_transcripts.get(lang, settings.sample_transcripts["en"])
