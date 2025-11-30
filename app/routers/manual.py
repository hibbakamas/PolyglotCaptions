from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from datetime import datetime
import logging

from app.services.translator_azure import azure_translate_async
from app.db.db import insert_caption_entry
from app.utils.auth import get_current_user_from_token
from app.utils.metrics import metric_caption_processed, metric_processing_time

router = APIRouter(prefix="/api/manual", tags=["manual"])
logger = logging.getLogger("polyglot")


async def get_current_user(request: Request) -> str:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    return get_current_user_from_token(auth_header.split(" ")[1])


class ManualRequest(BaseModel):
    text: str
    from_lang: str
    to_lang: str


class ManualSaveRequest(BaseModel):
    transcript: str
    translated_text: str
    from_lang: str
    to_lang: str


@router.post("/translate")
async def manual_translate(req: ManualRequest, user_id: str = Depends(get_current_user)):
    start_time = datetime.utcnow()

    translated = await azure_translate_async(req.text, req.from_lang, req.to_lang)

    processing_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

    metric_processing_time(processing_ms)

    logger.info("Manual translation request", extra={
        "text": req.text,
        "translated": translated,
        "user": user_id,
        "processing_ms": processing_ms
    })

    return {"translated_text": translated}


@router.post("/save")
def manual_save(req: ManualSaveRequest, user_id: str = Depends(get_current_user)):
    caption_id = insert_caption_entry(
        transcript=req.transcript,
        translated_text=req.translated_text,
        from_lang=req.from_lang,
        to_lang=req.to_lang,
        processing_ms=0,
        session_id=None,
        user_id=user_id,
        created_at=datetime.utcnow(),
    )

    metric_caption_processed()

    logger.info("Manual caption saved", extra={
        "caption_id": caption_id,
        "transcript": req.transcript,
        "translated": req.translated_text,
        "from": req.from_lang,
        "to": req.to_lang,
        "user": user_id,
    })

    return {"status": "saved", "id": caption_id}
