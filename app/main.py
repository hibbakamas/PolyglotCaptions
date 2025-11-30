import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers.caption import router as caption_router
from app.routers.manual import router as manual_router
from app.routers.logs import router as logs_router
from app.routers.auth import router as auth_router
from app.routers.health import router as health_router

app = FastAPI()

# Serve frontend folder
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ---- ROUTES FOR PAGES --------------------------------------

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


# ---- API ROUTES --------------------------------------------
app.include_router(caption_router)
app.include_router(manual_router)
app.include_router(logs_router)
app.include_router(auth_router)
app.include_router(health_router)


# ---- ROOT HEALTH CHECK (legacy) -----------------------------
@app.get("/health")
async def root_health():
    return {"status": "ok"}
