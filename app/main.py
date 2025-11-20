from typing import Optional
import time
import logging

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings
from services.stt_stub import fake_transcribe
from services.translator_stub import fake_translate
from services.translator_azure import azure_translate
from services.db import insert_caption_entry

# -------- logging (will flow into App Service / App Insights) ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("polyglot.api")

# ----------------------------------------------------------------------
app = FastAPI(
    title="PolyglotCaptions API",
    description="API for multi-language captions (Sprint 3 – Azure + DB).",
    version="0.3.0",
)

# CORS so frontend (localhost:5500) can call backend
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
    1. Fake STT (transcription) – still stub for Sprint 3.
    2. Translation – Azure Translator if enabled, otherwise stub.
    3. Optionally logs to Azure SQL (Captions table).
    """

    start = time.perf_counter()
    try:
        audio_bytes = await audio.read()
        logger.info(
            "Received /caption request pair=%s->%s size=%d",
            from_lang,
            to_lang,
            len(audio_bytes),
        )

        # ---- STT (stub) ----
        transcript = fake_transcribe(audio_bytes, from_lang)

        # ---- Translation (Azure or stub) ----
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

        # ---- DB logging (optional) ----
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

    except Exception as e:  # noqa: BLE001
        logger.exception("Error in /caption endpoint: %s", e)
        raise HTTPException(status_code=500, detail="Internal error in caption endpoint")