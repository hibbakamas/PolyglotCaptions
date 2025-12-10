from fastapi import APIRouter

from app.db.db import fetch_recent_captions

router = APIRouter(prefix="/api/logs", tags=["logs"])


@router.get("/recent")
def get_recent_logs():
    logs = fetch_recent_captions()
    if not logs:
        return []
    return logs
