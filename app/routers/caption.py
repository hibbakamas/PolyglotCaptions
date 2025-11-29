from typing import Optional, List
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from app.config import settings
from app.db.db import insert_caption_entry, fetch_captions, update_caption_entry, delete_caption_entry
from app.utils import process_audio_translation, format_caption_row, safe_db_call, build_caption_metadata
from app.schemas.caption import CaptionResponse

logger = logging.getLogger("polyglot.api")
router = APIRouter(prefix="/api", tags=["captions"])


class CaptionUpdate(BaseModel):
    transcript: Optional[str] = None
    translated_text: Optional[str] = None


# --- CREATE ---
@router.post("/captions", response_model=CaptionResponse)
async def create_caption(
    audio: UploadFile = File(...),
    from_lang: str = Form(...),
    to_lang: str = Form(...),
    session_id: Optional[str] = Form(None),
):
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="No audio received")

    transcript, translated, processing_ms = process_audio_translation(audio_bytes, from_lang, to_lang)
    metadata = build_caption_metadata(session_id)

    caption_id = None
    if settings.log_captions_to_db:
        caption_id = safe_db_call(
            insert_caption_entry,
            transcript=transcript,
            translated_text=translated,
            from_lang=from_lang,
            to_lang=to_lang,
            processing_ms=processing_ms,
            **metadata
        )

    return CaptionResponse(
        id=caption_id or 0,
        transcript=transcript,
        translated_text=translated,
        from_lang=from_lang,
        to_lang=to_lang,
        processing_ms=processing_ms,
        created_at=metadata["created_at"].strftime("%Y-%m-%d %H:%M:%S"),
        session_id=session_id
    )


# --- READ ---
@router.get("/captions", response_model=List[CaptionResponse])
async def get_captions(session_id: Optional[str] = None):
    rows = safe_db_call(fetch_captions, session_id=session_id)
    if rows is None:
        raise HTTPException(status_code=500, detail="Failed to fetch captions")
    return [format_caption_row(r) for r in rows]


# --- UPDATE ---
@router.put("/captions/{caption_id}", response_model=CaptionResponse)
async def update_caption(caption_id: int, update: CaptionUpdate):
    updated_row = safe_db_call(update_caption_entry, caption_id, update.transcript, update.translated_text)
    if not updated_row:
        raise HTTPException(status_code=404, detail="Caption not found")
    return format_caption_row(updated_row)


# --- DELETE ---
@router.delete("/captions/{caption_id}")
async def delete_caption(caption_id: int):
    deleted = safe_db_call(delete_caption_entry, caption_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Caption not found")
    return {"detail": f"Caption {caption_id} deleted"}
