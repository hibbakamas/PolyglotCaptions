import time
import logging
import tempfile
from app.config import settings
import azure.cognitiveservices.speech as speechsdk


logger = logging.getLogger("polyglot.services.stt_azure")


def azure_transcribe(audio_bytes: bytes | None = None) -> str:
   if audio_bytes is None:
       logger.warning("STT called with empty audio") 
       return ""


   stt_start = time.perf_counter()
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
       duration_ms = int((time.perf_counter() - stt_start) * 1000)  


       if result.reason == speechsdk.ResultReason.RecognizedSpeech:
           logger.info("Azure STT recognized speech in %dms", duration_ms)  
           return result.text
       else:
           logger.error("Azure STT could not recognize speech: %s", result.reason)
           raise RuntimeError(f"Azure STT could not recognize speech: {result.reason}")


   except Exception as e:
       duration_ms = int((time.perf_counter() - stt_start) * 1000)
       logger.exception("Azure STT failed after %dms: %s", duration_ms, e)  
       raise RuntimeError("Azure STT failed") from e