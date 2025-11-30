from fastapi import APIRouter
from pydantic import BaseModel
from app.db.db import get_connection

router = APIRouter(prefix="/api/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str


@router.get("", response_model=HealthResponse)
def health():
    """
    Basic health check: the API is running.
    """
    return HealthResponse(status="ok")


@router.get("/live", response_model=HealthResponse)
def live():
    """
    Liveness probe: App is running (no external dependencies).
    """
    return HealthResponse(status="alive")


@router.get("/ready", response_model=HealthResponse)
def ready():
    """
    Readiness probe: Checks database connectivity.
    If DB cannot be reached, the app is not ready.
    """
    try:
        conn = get_connection()
        conn.close()
        return HealthResponse(status="ready")
    except Exception:
        return HealthResponse(status="not ready")
