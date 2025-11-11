from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time

app = FastAPI(title="Polyglot Captions")

#allows local frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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


@app.get("/healthz")
def health_check():
    """Simple health check for CI/CD pipelines."""
    return {"status": "ok"}


@app.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(audio: UploadFile = File(...)):
    """Mock transcription + translation for MVP."""
    start = time.perf_counter()

    blob = await audio.read()
    chunk_bytes = len(blob)

    #pretends to do speech to text and translation

    t0 = time.perf_counter()
    original = "Hello world, this is a demo."
    stt_latency = int((time.perf_counter() - t0) * 1000)

    t1 = time.perf_counter()
    translated = "Hola mundo, esta es una demostración."
    trans_latency = int((time.perf_counter() - t1) * 1000)

    total_latency = int((time.perf_counter() - start) * 1000)

    return TranscribeResponse(
        original=original,
        translated=translated,
        fromLang="en",
        toLang="es",
        sttLatencyMs=stt_latency,
        transLatencyMs=trans_latency,
        totalLatencyMs=total_latency,
    )
