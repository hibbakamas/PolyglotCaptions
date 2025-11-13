from .stt_stub import fake_transcribe as _fallback_fake_transcribe
from app.config import settings


def azure_transcribe(audio_url: str | None = None) -> str:
    """
    Placeholder implementation.

    Later:
    - Download audio from URL or receive bytes
    - Send to Azure Speech service
    """

    return _fallback_fake_transcribe(audio_url=audio_url)
