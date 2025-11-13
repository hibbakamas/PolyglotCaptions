from fastapi import FastAPI
from pydantic import BaseModel


from app.services.translator_stub import fake_translate
from app.services.stt_stub import fake_transcribe


app = FastAPI(
   title="PolyglotCaptions API",
   description="Local API for live translation & captions (Sprint 1 – stub implementation).",
   version="0.1.0",
)


class HealthResponse(BaseModel):
   status: str



class TranslateRequest(BaseModel):
   text: str
   from_lang: str
   to_lang: str


class TranslateResponse(BaseModel):
   translated_text: str
   from_lang: str
   to_lang: str


class TranscribeRequest(BaseModel):
   text: str | None = None
   audio_url: str | None = None



class TranscribeResponse(BaseModel):
   transcript: str


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
   """
    health-check endpoint 
   """
   return HealthResponse(status="ok")




@app.post("/translate", response_model=TranslateResponse)
def translate(body: TranslateRequest) -> TranslateResponse:
   """
   Translate text between languages using the stubbed translator
   """
   translated = fake_translate(
       text=body.text,
       from_lang=body.from_lang,
       to_lang=body.to_lang,
   )
   return TranslateResponse(
       translated_text=translated,
       from_lang=body.from_lang,
       to_lang=body.to_lang,
   )




@app.post("/transcribe", response_model=TranscribeResponse)
def transcribe(body: TranscribeRequest) -> TranscribeResponse:
   """
   Fake STT endpoint
   """
   transcript = fake_transcribe(text=body.text, audio_url=body.audio_url)
   return TranscribeResponse(transcript=transcript)
