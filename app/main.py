# app/main.py

from pathlib import Path
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers.caption import router as caption_router
from app.routers.health import router as health_router

# ----- Logging -----
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("polyglot.api")

# ----- FastAPI App -----
app = FastAPI(
    title="PolyglotCaptions API",
    version="0.4.0",
)

# ----- CORS -----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # local dev-friendly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----- Routers -----
app.include_router(health_router)
app.include_router(caption_router)

# ------------------------------------------------------------
# Correct STATIC FILE SERVING
# Your actual folder is: PolyglotCaptions/frontend/
# ------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT_DIR / "frontend"

if not FRONTEND_DIR.exists():
    logger.error("❌ Frontend directory not found: %s", FRONTEND_DIR)
else:
    logger.info("✅ Serving frontend from %s", FRONTEND_DIR)

app.mount(
    "/",
    StaticFiles(directory=str(FRONTEND_DIR), html=True),
    name="frontend",
)
