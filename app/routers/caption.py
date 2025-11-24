from __future__ import annotations


from typing import Optional
import time
import logging


from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel


from app.config import settings
from app.services.stt_azure import azure_transcribe
from app.services.translator_stub import fake_translate
from app.services.translator_azure import azure_translate
from app.services.db import insert_caption_entry


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
   start = time.perf_counter()


   try:
       audio_bytes = await audio.read()
       if not audio_bytes:
           raise HTTPException(status_code=400, detail="No audio content received")


       logger.info(
           "Received /api/caption request pair=%s->%s size=%d",
           from_lang,
           to_lang,
           len(audio_bytes),
       )


       # ---- STT ----
       try:
           transcript = azure_transcribe(audio_bytes)
       except Exception as stt_exc:
           logger.exception("Azure STT failed: %s", stt_exc)
           raise HTTPException(status_code=500, detail="Azure STT failed")


       # ---- Translation ----
       try:
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
       except Exception as trans_exc:
           logger.exception("Translation error, using stub: %s", trans_exc)
           translated = fake_translate(
               text=transcript,
               from_lang=from_lang,
               to_lang=to_lang,
           )


       total_ms = int((time.perf_counter() - start) * 1000)


       # ---- DB logging (optional) ----
       if settings.log_captions_to_db:
           try:
               insert_caption_entry(
                   from_lang=from_lang,
                   to_lang=to_lang,
                   transcript=transcript,
                   translated_text=translated,
                   processing_ms=total_ms,
                   session_id=session_id,
               )
           except Exception as db_exc:
               logger.exception("DB logging failed: %s", db_exc)


       return CaptionResponse(
           transcript=transcript,
           translated_text=translated,
           from_lang=from_lang,
           to_lang=to_lang,
           processing_ms=total_ms,
       )


   except HTTPException:
       raise
   except Exception as exc:
       logger.exception("Unhandled error in /api/caption endpoint: %s", exc)
       raise HTTPException(status_code=500, detail="Internal error in caption endpoint")