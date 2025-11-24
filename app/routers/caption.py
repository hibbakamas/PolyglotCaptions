from typing import Optional
import time
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.services.stt_azure import azure_transcribe
from app.services.translator_azure import azure_translate
from app.services.translator_stub import fake_translate
from app.services.db import insert_caption_entry

logger = logging.getLogger("polyglot.api")

router = APIRouter(prefix="/api", tags=["caption"])

class CaptionResponse(BaseModel):
    transcript: str
    translated_text: str
    from_lang: str
    to_lang: str
    processing_ms: int

@router.post("/caption", response_model=CaptionResponse)
async def caption_endpoint(
    audio: UploadFile = File(...),
    from_lang: str = Form(...),
    to_lang: str = Form(...),
    session_id: Optional[str] = Form(None),
):
    start = time.perf_counter()

    try:
        audio_bytes = await audio.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="No audio received")

        logger.info(f"Received /caption {from_lang}->{to_lang} size={len(audio_bytes)}")

        # --- SPEECH → TEXT (Azure with fallback stub) ---
        transcript = azure_transcribe(audio_bytes, from_lang)
        if not transcript:
            transcript = ""

        # --- TRANSLATION (Azure with fallback stub) ---
        try:
            translated = (
                azure_translate(transcript, from_lang, to_lang)
                if settings.use_azure_translator else
                fake_translate(transcript, from_lang, to_lang)
            )
        except Exception:
            translated = fake_translate(transcript, from_lang, to_lang)

        total_ms = int((time.perf_counter() - start) * 1000)

        # --- Save DB log (safe) ---
        if settings.log_captions_to_db:
            try:
                insert_caption_entry(
                    transcript=transcript,
                    translation=translated,
                    from_lang=from_lang,
                    to_lang=to_lang,
                    processing_ms=total_ms,
                    session_id=session_id,
                )
            except Exception as exc:
                logger.error(f"DB logging failed: {exc}")

        return CaptionResponse(
            transcript=transcript,
            translated_text=translated,
            from_lang=from_lang,
            to_lang=to_lang,
            processing_ms=total_ms
        )

    except Exception as exc:
        logger.exception(f"Caption endpoint crashed: {exc}")
        raise HTTPException(status_code=500, detail="Internal server error")
