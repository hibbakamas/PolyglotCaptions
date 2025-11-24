from __future__ import annotations


from typing import Optional
import time
import logging
logger = logging.getLogger("polyglot.api")




from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel


from app.config import settings
from app.services.stt_azure import azure_transcribe
from app.services.translator_stub import fake_translate
from app.services.translator_azure import azure_translate
from app.services.db import insert_caption_entry


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
) -> CaptionResponse:
   start = time.perf_counter()
   logger.info("Caption request received: %s->%s", from_lang, to_lang) 


   try:
       audio_bytes = await audio.read()
       if not audio_bytes:
           logger.warning("Caption request with empty audio")  
           raise HTTPException(status_code=400, detail="No audio content received")


       # ---- STT ----
       stt_start = time.perf_counter()
       transcript = azure_transcribe(audio_bytes)
       stt_duration = int((time.perf_counter() - stt_start) * 1000)
       logger.info("Azure STT completed in %dms", stt_duration)  


       # ---- Translation ----
       translation_start = time.perf_counter()
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
       translation_duration = int((time.perf_counter() - translation_start) * 1000)
       logger.info("Translation completed in %dms", translation_duration)


       total_ms = int((time.perf_counter() - start) * 1000)


       # ---- DB logging (optional) ----
       if settings.log_captions_to_db:
           success = insert_caption_entry(
               from_lang=from_lang,
               to_lang=to_lang,
               transcript=transcript,
               translated_text=translated,
               processing_ms=total_ms,
               session_id=session_id,
           )
           if not success:
               logger.warning("DB logging failed for session: %s", session_id)  


       logger.info("Caption request processed in %dms", total_ms)  
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