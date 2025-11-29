import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers.caption import router as caption_router
from app.routers.manual import router as manual_router
from app.routers.logs import router as logs_router

app = FastAPI()

# Serve frontend folder
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

# ---- ROUTES FOR PAGES --------------------------------------

@app.get("/")
async def serve_home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/record")
async def serve_record():
    return FileResponse(os.path.join(FRONTEND_DIR, "record.html"))

@app.get("/manual")
async def serve_manual():
    return FileResponse(os.path.join(FRONTEND_DIR, "manual.html"))

@app.get("/history")
async def serve_history():
    return FileResponse(os.path.join(FRONTEND_DIR, "history.html"))


# ---- API ROUTES --------------------------------------------
app.include_router(caption_router)
app.include_router(manual_router)
app.include_router(logs_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
