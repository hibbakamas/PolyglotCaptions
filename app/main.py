from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
import time

from app.services.stt_stub import fake_transcribe
from app.services.translator_stub import fake_translate

app = FastAPI(
    title="PolyglotCaptions API",
    description="API for multi-language captions (Sprint 2 – stub backend).",
    version="0.2.0",
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
):

    start = time.perf_counter()

    try:
        audio_bytes = await audio.read()
        transcript = fake_transcribe(audio_bytes, from_lang)

        translated = fake_translate(
            text=transcript,
            from_lang=from_lang,
            to_lang=to_lang
        )

        total_ms = int((time.perf_counter() - start) * 1000)

        return CaptionResponse(
            transcript=transcript,
            translated_text=translated,
            from_lang=from_lang,
            to_lang=to_lang,
            processing_ms=total_ms,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
