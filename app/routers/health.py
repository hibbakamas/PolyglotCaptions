from fastapi import APIRouter
import requests

router = APIRouter(prefix="/api", tags=["health"])

@router.get("/ready")
def readiness():
    checks = {}

    # Basic check: app is alive
    checks["app"] = True

    # Optional: Azure Speech API check
    try:
        test_url = "https://eastus.stt.speech.microsoft.com"
        resp = requests.get(test_url, timeout=2)
        checks["speech_api"] = resp.status_code < 500
    except Exception:
        checks["speech_api"] = False

    ready = all(checks.values())
    return {"ready": ready, "checks": checks}
