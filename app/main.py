from typing import Optional
import time
import logging

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings
from services.stt_azure import azure_transcribe
from services.stt_stub import fake_transcribe
from services.translator_stub import fake_translate
from services.translator_azure import azure_translate
from services.db import insert_caption_entry

# -------- logging  ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("polyglot.api")

if settings.enable_app_insights and settings.app_insights_instrumentation_key:
    from opencensus.ext.azure.log_exporter import AzureLogHandler
    handler = AzureLogHandler(
        connection_string=f'InstrumentationKey={settings.app_insights_instrumentation_key}'
    )
    logger.addHandler(handler)
    logger.info("Azure App Insights logging enabled")

app = FastAPI(
    title="PolyglotCaptions API",
    description="API for multi-language captions (Sprint 4 – Azure + DB + Monitoring).",
    version="0.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthResponse(BaseModel):
    status: str


class CaptionResponse(BaseModel):
    transcript: str
    translated_text: str
    from_lang: str
    to_lang: str
    processing_ms: int


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/caption", response_model=CaptionResponse)
async def caption_endpoint(
    audio: UploadFile = File(..., description="Audio file (webm/ogg/wav/mp3)"),
    from_lang: str = Form(..., description="Source language code, e.g. en, es, fr"),
    to_lang: str = Form(..., description="Target language code, e.g. en, es, fr"),
    session_id: Optional[str] = Form(None, description="Optional session identifier"),
):
    """
    Takes an audio file + language selection:
    1. Azure or stub STT
    2. Azure Translator if enabled, otherwise stub
    3. Optionally logs to Azure SQL (Captions table)
    4. Improved error handling
    """
    start = time.perf_counter()

    try:
        audio_bytes = await audio.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="No audio content received")

        logger.info(
            "Received /caption request pair=%s->%s size=%d",
            from_lang,
            to_lang,
            len(audio_bytes),
        )

        # ---- STT ----
        try:
            transcript = azure_transcribe(audio_bytes)
            if not transcript:
                logger.warning("Azure STT returned empty transcript; falling back to stub")
                transcript = fake_transcribe(audio_bytes, from_lang)
        except Exception as stt_exc:
            logger.exception("STT error, using fallback stub: %s", stt_exc)
            transcript = fake_transcribe(audio_bytes, from_lang)

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
        logger.exception("Unhandled error in /caption endpoint: %s", exc)
        raise HTTPException(status_code=500, detail="Internal error in caption endpoint")
