# app/routers/health.py

from fastapi import APIRouter
import pyodbc
import requests
from app.config import settings

router = APIRouter(prefix="/api/health", tags=["health"])

# -------------------------------------------------------------
# LIVENESS: App is running
# -------------------------------------------------------------
@router.get("/live")
async def live_check():
    return {"status": "alive"}

# -------------------------------------------------------------
# READINESS: DB + Azure services reachable
# -------------------------------------------------------------
@router.get("/ready")
async def ready_check():
    checks = {
        "database": False,
        "translator_api": False,
        "speech_api": False,
    }

    # ---- Database check ----
    try:
        conn = pyodbc.connect(settings.azure_sql_connection_string, timeout=3)
        conn.close()
        checks["database"] = True
    except Exception:
        checks["database"] = False

    # ---- Translator API check ----
    try:
        resp = requests.get(settings.azure_translator_endpoint, timeout=3)
        checks["translator_api"] = resp.status_code < 500
    except Exception:
        checks["translator_api"] = False

    # ---- Speech API check ----
    try:
        test_url = f"https://{settings.azure_speech_region}.stt.speech.microsoft.com"
        resp = requests.get(test_url, timeout=3)
        checks["speech_api"] = resp.status_code < 500
    except Exception:
        checks["speech_api"] = False

    return {
        "ready": all(checks.values()),
        "checks": checks
    }
