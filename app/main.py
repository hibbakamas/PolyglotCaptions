import os
import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer

from app.routers.caption import router as caption_router
from app.routers.manual import router as manual_router
from app.routers.logs import router as logs_router
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.config import settings




app = FastAPI()

# ===================================================================
#                    APPLICATION INSIGHTS SETUP  
# ===================================================================

if settings.app_insights_key:
    tracer = Tracer(
        exporter=AzureExporter(
            connection_string=f"InstrumentationKey={settings.app_insights_key}"
        ),
        sampler=ProbabilitySampler(1.0),
    )

    ai_handler = AzureLogHandler(
        connection_string=f"InstrumentationKey={settings.app_insights_key}"
    )
    logger = logging.getLogger("polyglot")
    logger.setLevel(logging.INFO)
    logger.addHandler(ai_handler)

    class RequestTraceMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            with tracer.span(name=f"{request.method} {request.url.path}"):
                return await call_next(request)

    app.add_middleware(RequestTraceMiddleware)

# ===================================================================
#                          CORS (REQUIRED ON AZURE)  
# ===================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================================================================
#                          FRONTEND ROUTES
# ===================================================================

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/", include_in_schema=False)
async def serve_login():
    return FileResponse(os.path.join(FRONTEND_DIR, "login.html"))

@app.get("/record", include_in_schema=False)
async def serve_record():
    return FileResponse(os.path.join(FRONTEND_DIR, "record.html"))

@app.get("/manual", include_in_schema=False)
async def serve_manual():
    return FileResponse(os.path.join(FRONTEND_DIR, "manual.html"))

@app.get("/history", include_in_schema=False)
async def serve_history():
    return FileResponse(os.path.join(FRONTEND_DIR, "history.html"))

# ===================================================================
#                           API ROUTERS
# ===================================================================

app.include_router(caption_router)
app.include_router(manual_router)
app.include_router(logs_router)
app.include_router(auth_router)
app.include_router(health_router)

# ===================================================================
#                           ROOT HEALTH
# ===================================================================

@app.get("/health")
async def root_health():
    return {"status": "ok"}
