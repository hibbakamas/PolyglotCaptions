import logging
import tempfile
from app.config import settings
import azure.cognitiveservices.speech as speechsdk


logger = logging.getLogger("polyglot.services.stt_azure")


def azure_transcribe(audio_bytes: bytes | None = None) -> str:
   if audio_bytes is None:
       return ""


   try:
       speech_config = speechsdk.SpeechConfig(
           subscription=settings.azure_speech_key,
           region=settings.azure_speech_region
       )

       with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_audio:
           tmp_audio.write(audio_bytes)
           tmp_audio_path = tmp_audio.name


       audio_config = speechsdk.AudioConfig(filename=tmp_audio_path)
       recognizer = speechsdk.SpeechRecognizer(
           speech_config=speech_config,
           audio_config=audio_config
       )


       result = recognizer.recognize_once()
       if result.reason == speechsdk.ResultReason.RecognizedSpeech:
           return result.text
       else:
           logger.error("Azure STT could not recognize speech: %s", result.reason)
           raise RuntimeError(f"Azure STT could not recognize speech: {result.reason}")


   except Exception as e:
       logger.exception("Azure STT error: %s", e)
       raise RuntimeError("Azure STT failed") from e