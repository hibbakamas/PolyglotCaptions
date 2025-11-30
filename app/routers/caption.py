from fastapi import APIRouter, UploadFile, Form, Depends, HTTPException, Request
from datetime import datetime
import logging

from app.services.stt_azure import azure_transcribe
from app.services.translator_azure import azure_translate_async
from app.db.db import insert_caption_entry, fetch_captions, delete_caption_entry
from app.utils.auth import get_current_user_from_token
from app.utils.metrics import metric_caption_processed, metric_processing_time

router = APIRouter(prefix="/api/captions", tags=["captions"])
logger = logging.getLogger("polyglot")


# -----------------------
# TOKEN → USER HELPER
# -----------------------
async def get_current_user(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.split(" ")[1]
    return get_current_user_from_token(token)


# -----------------------
# CREATE CAPTION (Audio)
# -----------------------
@router.post("")
async def create_caption(
    audio: UploadFile,
    from_lang: str = Form(...),
    to_lang: str = Form(...),
    user_id: str = Depends(get_current_user),
):
    start_time = datetime.utcnow()

    audio_bytes = await audio.read()
    if not audio_bytes or len(audio_bytes) < 50:
        raise HTTPException(status_code=400, detail="Audio file is empty or corrupted")

    # --- Speech to Text ----
    transcript = azure_transcribe(audio_bytes, from_lang)
    if not transcript:
        raise HTTPException(status_code=500, detail="Speech recognition failed")

    # --- Translation ----
    translated = await azure_translate_async(transcript, from_lang, to_lang)
    if not translated:
        raise HTTPException(status_code=500, detail="Translation failed")

    # --- Processing time ----
    processing_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

    # --- Save to DB ----
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

    logger.info("Caption created", extra={
        "caption_id": caption_id,
        "transcript": transcript,
        "translated": translated,
        "from": from_lang,
        "to": to_lang,
        "user": user_id,
        "processing_ms": processing_ms,
    })

    metric_caption_processed()
    metric_processing_time(processing_ms)

    # MATCH WHAT record.js EXPECTS
    return {
        "id": caption_id,
        "transcript": transcript,
        "translated": translated
    }


# -----------------------
# GET ALL CAPTIONS
# -----------------------
@router.get("")
def get_captions(user_id: str = Depends(get_current_user)):
    return fetch_captions(user_id=user_id)


# -----------------------
# DELETE CAPTION
# -----------------------
@router.delete("/{caption_id}")
def delete_caption(caption_id: int, user_id: str = Depends(get_current_user)):
    deleted = delete_caption_entry(caption_id, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Caption not found or not owned by user")

    logger.info("Caption deleted", extra={"caption_id": caption_id, "user": user_id})
    return {"deleted": caption_id}
