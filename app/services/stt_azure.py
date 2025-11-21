from azure.ai.speech import SpeechClient, SpeechConfig, AudioConfig, SpeechRecognizer
from app.config import settings
import logging

logger = logging.getLogger("polyglot.services.stt_azure")

def azure_transcribe(audio_bytes: bytes | None = None) -> str:
    """
    Use Azure Speech-to-Text to transcribe audio.

    Args:
        audio_bytes (bytes | None): Raw audio bytes.

    Returns:
        str: Transcribed text.
    """
    if audio_bytes is None:
        return ""

    try:
        speech_config = SpeechConfig(
            subscription=settings.azure_speech_key,
            region=settings.azure_speech_region
        )

        # Save audio bytes to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
            tmp_audio.write(audio_bytes)
            tmp_audio_path = tmp_audio.name

        audio_config = AudioConfig(filename=tmp_audio_path)
        recognizer = SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        result = recognizer.recognize_once()
        if result.reason == result.Reason.RecognizedSpeech:
            return result.text
        else:
            logger.warning("Azure STT could not recognize speech: %s", result.reason)
            return ""
    except Exception as e:
        logger.exception("Azure STT error: %s", e)
        # fallback to stub
        from .stt_stub import fake_transcribe as _fallback_fake_transcribe
        return _fallback_fake_transcribe()
