import time
import logging
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from app.services.stt_azure import azure_transcribe
from app.services.translator_azure import azure_translate
from app.services.translator_stub import fake_translate
from app.config import settings

from app.schemas.caption import CaptionResponse


logger = logging.getLogger(__name__)


def process_audio_translation(audio_bytes: bytes, from_lang: str, to_lang: str) -> tuple[str, str, int]:
    "process audio bytes to get transcript and translation, returning processing time in ms"
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


def format_caption_row(row) -> CaptionResponse:
    """format a DB row into a CaptionResponse"""
    return CaptionResponse(
        id=row["Id"],
        transcript=row["Transcript"],
        translated_text=row["TranslatedText"],
        from_lang=row["FromLang"],
        to_lang=row["ToLang"],
        processing_ms=row["ProcessingMs"],
        created_at=row["CreatedAt"].strftime("%Y-%m-%d %H:%M:%S"),
        session_id=row.get("SessionId")
    )

def safe_db_call(func, *args, **kwargs):
    """safely call a DB function, logging errors and returning None on failure"""
    try:
        return func(*args, **kwargs)
    except Exception as exc:
        logger.error(f"DB call failed: {exc}")
        return None

def build_caption_metadata(session_id: Optional[str] = None) -> dict:
    """build caption metadata dictionary"""
    return {
        "session_id": session_id,
        "created_at": datetime.utcnow()
    }

class CaptionResponse(BaseModel):
    id: int
    transcript: str
    translated_text: str
    from_lang: str
    to_lang: str
    processing_ms: int
    created_at: str
    session_id: Optional[str] = None