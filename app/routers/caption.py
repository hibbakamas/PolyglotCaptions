from __future__ import annotations


from typing import Optional
import time
import logging


from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel


from config import settings
from services.stt_stub import fake_transcribe
from services.translator_stub import fake_translate
from services.translator_azure import azure_translate
from services.db import insert_caption_entry


router = APIRouter(prefix="/api", tags=["caption"])
logger = logging.getLogger("polyglot.api.caption")




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
) -> CaptionResponse:
   """
   1) Stub STT
   2) Azure Translator if enabled, else stub
   3) Optional DB logging
   """
   start = time.perf_counter()


   try:
       audio_bytes = await audio.read()
       logger.info(
           "Received /api/caption request pair=%s->%s size=%d",
           from_lang,
           to_lang,
           len(audio_bytes),
       )


       # STT (stub)
       transcript = fake_transcribe(audio_bytes, from_lang)


       # Translation
       if settings.use_azure_translator:
           translated = azure_translate(
               text=transcript,
               from_lang=from_lang,
               to_lang=to_lang,
           )
       else:
           translated = fake_translate(
               text=transcript,
               from_lang=from_lang,
               to_lang=to_lang,
           )


       total_ms = int((time.perf_counter() - start) * 1000)


       # DB logging (optional)
       if settings.log_captions_to_db:
           insert_caption_entry(
               from_lang=from_lang,
               to_lang=to_lang,
               transcript=transcript,
               translated_text=translated,
               processing_ms=total_ms,
               session_id=session_id,
           )


       return CaptionResponse(
           transcript=transcript,
           translated_text=translated,
           from_lang=from_lang,
           to_lang=to_lang,
           processing_ms=total_ms,
       )
   except Exception as exc:  # noqa: BLE001
       logger.exception("Error in /api/caption endpoint: %s", exc)
       raise HTTPException(status_code=500, detail="Internal error in caption endpoint")
