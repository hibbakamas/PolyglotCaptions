import time
import logging
from datetime import datetime
from typing import Optional
from app.services.stt_azure import azure_transcribe
from app.services.translator_azure import azure_translate
from app.services.translator_stub import fake_translate
from app.config import settings
from app.schemas.caption import CaptionResponse

logger = logging.getLogger("polyglot.utils")

def process_audio_translation(audio_bytes: bytes, from_lang: str, to_lang: str):
    start = time.perf_counter()

    transcript = azure_transcribe(audio_bytes, from_lang) or ""

    try:
        translated = (
            azure_translate(transcript, from_lang, to_lang)
            if settings.use_azure_translator else
            fake_translate(transcript, from_lang, to_lang)
        )
    except Exception:
        translated = fake_translate(transcript, from_lang, to_lang)

    total_ms = int((time.perf_counter() - start) * 1000)
    return transcript, translated, total_ms


def safe_db_call(func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        logger.error(f"DB call failed: {exc}")
        return None


def build_caption_metadata(session_id: Optional[str] = None):
    return {
        "session_id": session_id,
        "created_at": datetime.utcnow()
    }


def format_caption_row(row):
    return CaptionResponse(
        id=row["Id"],
        transcript=row["Transcript"],
        translated_text=row["TranslatedText"],
        from_lang=row["FromLang"],
        to_lang=row["ToLang"],
        processing_ms=row["ProcessingMs"],
        created_at=row["CreatedAt"].strftime("%Y-%m-%d %H:%M:%S"),
        session_id=row.get("SessionId"),
    )
