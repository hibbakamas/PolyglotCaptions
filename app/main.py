from typing import Optional
import time
import logging


from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


from app.services.stt_azure import azure_transcribe
from app.routers import caption
from app.config import settings
from app.services.stt_stub import fake_transcribe
from app.services.translator_stub import fake_translate
from app.services.translator_azure import azure_translate
from app.services.db import insert_caption_entry


from dotenv import load_dotenv
load_dotenv()


# -------- logging ----------
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

app.include_router(caption.router)


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