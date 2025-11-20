from pathlib import Path
import logging


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


from routers.health import router as health_router
from routers.caption import router as caption_router
from routers.logs import router as logs_router


# -------- logging ----------
logging.basicConfig(
   level=logging.INFO,
   format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("polyglot.api")


# -------- FastAPI app ----------
app = FastAPI(
   title="PolyglotCaptions API",
   description="API for multi-language captions (Sprint 3 – routers + Azure + DB).",
   version="0.3.0",
)


# CORS – safe and simple
app.add_middleware(
   CORSMiddleware,
   allow_origins=["*"],
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)


# -------- Routers (all under /api/...) ----------
app.include_router(health_router)
app.include_router(caption_router)
app.include_router(logs_router)


# -------- Serve frontend from ../frontend ----------
BASE_DIR = Path(__file__).resolve().parent.parent  # .../FakeTR
FRONTEND_DIR = BASE_DIR / "frontend"


if not FRONTEND_DIR.is_dir():
   logger.warning("Frontend directory not found at %s", FRONTEND_DIR)


# Mount root so http://127.0.0.1:8000/ -> index.html
app.mount(
   "/",
   StaticFiles(directory=str(FRONTEND_DIR), html=True),
   name="frontend",
)