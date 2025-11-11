from fastapi import FastAPI, UploadFile, File, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
from config import settings
from services.stt_stub import fake_stt
from services.translator_stub import fake_translate

app = FastAPI(title="Polyglot Captions — Sprint 1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TranscribeResponse(BaseModel):
    original: str
    translated: str
    fromLang: str
    toLang: str
    sttLatencyMs: int
    transLatencyMs: int
    totalLatencyMs: int
    chunkBytes: int

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(
    audio: UploadFile = File(...),
    from_lang: str = Query(default=settings.FROM_LANG),
    to_lang: str = Query(default=settings.TO_LANG),
):
    try:
        start = time.perf_counter()
        blob = await audio.read()
        size = len(blob)

        # simulate STT
        t0 = time.perf_counter()
        original = fake_stt(blob, from_lang)
        stt_ms = int((time.perf_counter() - t0) * 1000)

        # simulate translation
        t1 = time.perf_counter()
        translated = fake_translate(original, from_lang, to_lang)
        trans_ms = int((time.perf_counter() - t1) * 1000)

        total_ms = int((time.perf_counter() - start) * 1000)

        return TranscribeResponse(
            original=original,
            translated=translated,
            fromLang=from_lang,
            toLang=to_lang,
            sttLatencyMs=stt_ms,
            transLatencyMs=trans_ms,
            totalLatencyMs=total_ms,
            chunkBytes=size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))