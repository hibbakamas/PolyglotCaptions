# app/services/stt_azure.py

import logging
import subprocess
import tempfile

import azure.cognitiveservices.speech as speechsdk

from app.config import settings
from app.services.stt_stub import fake_transcribe

logger = logging.getLogger("polyglot.services.stt_azure")

LANG_MAP = {
    "en": "en-US",
    "es": "es-ES",
    "fr": "fr-FR",
    "de": "de-DE",
    "it": "it-IT",
}


def convert_webm_to_wav(input_bytes: bytes) -> str:
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f_in:
        f_in.write(input_bytes)
        src = f_in.name
    wav_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    cmd = ["ffmpeg", "-y", "-i", src, wav_file]
    subprocess.run(cmd, capture_output=True, check=True)
    return wav_file


def azure_transcribe(audio_bytes: bytes, from_lang: str) -> str:
    """
    Transcribe audio to text.
    Returns just the transcript text (no auto-detection).
    """
    if not audio_bytes:
        return ""

    if not settings.azure_speech_key or not settings.azure_speech_region or speechsdk is None:
        if speechsdk is None:
            logger.warning("Azure Speech SDK not installed; using stub transcript.")
        return fake_transcribe(audio_bytes, from_lang)

    wav_path = convert_webm_to_wav(audio_bytes)

    speech_config = speechsdk.SpeechConfig(
        subscription=settings.azure_speech_key, region=settings.azure_speech_region
    )

    # Always use the specified language (no auto-detection)
    speech_config.speech_recognition_language = LANG_MAP.get(from_lang, "en-US")

    audio_config = speechsdk.AudioConfig(filename=wav_path)
    recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    result = recognizer.recognize_once()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        return result.text

    return ""
