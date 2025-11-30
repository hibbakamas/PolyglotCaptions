# app/routers/manual.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from datetime import datetime
from app.services.translator_azure import azure_translate_async
from app.db.db import insert_caption_entry
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/manual", tags=["manual"])

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
    translated = await azure_translate_async(req.text, req.from_lang, req.to_lang)
    return {"translated_text": translated}

@router.post("/save")
def manual_save(req: ManualSaveRequest, user_id: str = Depends(get_current_user)):
    insert_caption_entry(
        transcript=req.transcript,
        translated_text=req.translated_text,
        from_lang=req.from_lang,
        to_lang=req.to_lang,
        processing_ms=0,
        session_id=None,
        user_id=user_id,
        created_at=datetime.utcnow(),
    )
    return {"status": "saved"}
