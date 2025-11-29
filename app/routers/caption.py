from fastapi import APIRouter, UploadFile, Form
from datetime import datetime

from app.services.stt_azure import azure_transcribe
from app.services.translator_azure import azure_translate_async
from app.db.db import insert_caption_entry, fetch_captions, delete_caption_entry

router = APIRouter(
    prefix="/api/captions",
    tags=["captions"]
)


@router.post("")
async def create_caption(
    audio: UploadFile,
    from_lang: str = Form(...),
    to_lang: str = Form(...),
):
    audio_bytes = await audio.read()

    # STT
    transcript = azure_transcribe(audio_bytes, from_lang)

    # Translation
    translated = await azure_translate_async(transcript, from_lang, to_lang)

    # Save to DB
    caption_id = insert_caption_entry(
        transcript=transcript,
        translated_text=translated,
        from_lang=from_lang,
        to_lang=to_lang,
        processing_ms=0,
        session_id=None,
        created_at=datetime.utcnow(),
    )

    return {
        "id": caption_id,
        "transcript": transcript,
        "translated": translated,
    }


@router.get("")
def get_captions():
    return fetch_captions()


@router.delete("/{caption_id}")
def delete_caption(caption_id: int):
    delete_caption_entry(caption_id)
    return {"deleted": caption_id}
