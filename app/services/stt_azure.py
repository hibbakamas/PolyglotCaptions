# app/services/stt_azure.py
import time
import logging
import tempfile
import subprocess

from app.config import settings
import azure.cognitiveservices.speech as speechsdk
from app.services.stt_stub import fake_transcribe

logger = logging.getLogger("polyglot.services.stt_azure")


def convert_webm_to_wav(input_bytes: bytes) -> str:
    """Convert WebM/Opus bytes → WAV file using ffmpeg."""
    try:
        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f_in:
            f_in.write(input_bytes)
            src = f_in.name

        wav_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name

        cmd = [
            "ffmpeg",
            "-y",
            "-i", src,
            "-acodec", "pcm_s16le",
            "-ar", "16000",
            wav_file
        ]

        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        return wav_file

    except Exception as exc:
        logger.error(f"FFMPEG conversion failed: {exc}")
        raise


def azure_transcribe(audio_bytes: bytes, from_lang: str) -> str:
    if not audio_bytes:
        logger.warning("Empty audio sent to STT")
        return ""

    # If Azure not configured → stub
    if not settings.azure_speech_key or not settings.azure_speech_region:
        logger.warning("Azure STT disabled → using stub transcription.")
        return fake_transcribe(audio_bytes, from_lang)

    stt_start = time.perf_counter()

    try:
        wav_path = convert_webm_to_wav(audio_bytes)

        speech_config = speechsdk.SpeechConfig(
            subscription=settings.azure_speech_key,
            region=settings.azure_speech_region
        )
        speech_config.speech_recognition_language = {
            "en": "en-US",
            "es": "es-ES",
            "fr": "fr-FR",
            "de": "de-DE",
            "it": "it-IT",
        }.get(from_lang, "en-US")

        audio_config = speechsdk.AudioConfig(filename=wav_path)
        recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_config
        )

        result = recognizer.recognize_once()
        duration_ms = int((time.perf_counter() - stt_start) * 1000)

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            logger.info(f"Azure STT OK ({duration_ms}ms)")
            return result.text

        logger.error(f"Azure STT returned: {result.reason}")
        raise RuntimeError("Azure STT failed")

    except Exception as exc:
        logger.error(f"Azure STT crashed → fallback stub: {exc}")
        return fake_transcribe(audio_bytes, from_lang)
