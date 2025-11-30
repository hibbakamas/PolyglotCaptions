# app/routers/logs.py

from fastapi import APIRouter, Query
from typing import Any, Dict, List
from app.db.db import fetch_recent_captions

router = APIRouter(prefix="/api", tags=["logs"])

@router.get("/captions/logs")
def get_caption_logs(limit: int = Query(20, ge=1, le=100)) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = fetch_recent_captions(limit=limit)
    return {"count": len(items), "items": items}
