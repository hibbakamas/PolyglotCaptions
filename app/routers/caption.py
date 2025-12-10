import logging
from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request, UploadFile

from app.db.db import (
    delete_caption_entry,
    fetch_captions,
    insert_caption_entry,
    update_caption_entry,
)
from app.services.stt_azure import azure_transcribe
from app.services.translator_azure import azure_translate_async
from app.utils.auth import get_current_user_from_token
from app.utils.metrics import metric_caption_processed, metric_processing_time

router = APIRouter(prefix="/api/captions", tags=["captions"])
logger = logging.getLogger("polyglot")


# --- AUTH HELPERS ---
async def get_current_user(request: Request) -> str:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth.split(" ")[1]
    return get_current_user_from_token(token)


# --- CREATE CAPTION ---
@router.post("")
async def create_caption(
    audio: UploadFile,
    from_lang: str = Form(...),  # e.g. "en", "es", "fr", "de", "it"
    to_lang: str = Form(...),  # same codes as in manual translation
    user_id: str = Depends(get_current_user),
):
    """
    Create a new caption entry:
    1. Transcribes audio from `from_lang` (no auto-detect).
    2. Translates transcript into `to_lang`.
    3. Logs + stores both transcript and translation.
    """
    start_time = datetime.utcnow()
    audio_bytes = await audio.read()

    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file")

    # 1) Transcribe (Azure Speech to Text)
    transcript = azure_transcribe(audio_bytes, from_lang)

    # Guard: if STT returns nothing, don't blow up the UI
    if not transcript:
        raise HTTPException(status_code=500, detail="Transcription failed")

    # 2) Translate into selected language (Azure Translator)
    translated = await azure_translate_async(transcript, from_lang, to_lang)

    processing_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

    # 3) Store result in DB
    caption_id = insert_caption_entry(
        transcript=transcript,
        translated_text=translated,
        from_lang=from_lang,
        to_lang=to_lang,
        processing_ms=processing_ms,
        session_id=None,
        user_id=user_id,
        created_at=datetime.utcnow(),
    )

    logger.info(
        "Caption created",
        extra={
            "caption_id": caption_id,
            "user": user_id,
            "from": from_lang,
            "to": to_lang,
            "transcript": transcript,
            "translated": translated,
            "processing_ms": processing_ms,
        },
    )

    # Metrics
    metric_caption_processed()
    metric_processing_time(processing_ms)

    return {
        "id": caption_id,
        "transcript": transcript,
        "translated": translated,
        "processing_ms": processing_ms,
    }


# --- READ CAPTIONS ---
@router.get("")
def get_captions(user_id: str = Depends(get_current_user)):
    """Fetch all captions for a user."""
    return fetch_captions(user_id=user_id)


# --- UPDATE CAPTION ---
@router.put("/{caption_id}")
def update_caption(
    caption_id: int,
    body: dict,
    user_id: str = Depends(get_current_user),
):
    """
    Update an existing caption's translated text.
    """
    new_text = body.get("translated_text")
    if not new_text:
        raise HTTPException(status_code=400, detail="Missing translated_text field")

    updated = update_caption_entry(caption_id, new_text, user_id)
    if not updated:
        raise HTTPException(
            status_code=404,
            detail="Caption not found or not owned by user",
        )

    logger.info("Caption updated", extra={"caption_id": caption_id, "user": user_id})
    return {"updated": caption_id, "new_text": new_text}


# --- DELETE CAPTION ---
@router.delete("/{caption_id}")
def delete_caption(caption_id: int, user_id: str = Depends(get_current_user)):
    """Delete a caption owned by the user."""
    deleted = delete_caption_entry(caption_id, user_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Caption not found or not owned by user",
        )

    logger.info("Caption deleted", extra={"caption_id": caption_id, "user": user_id})
    return {"deleted": caption_id}
