from typing import Optional
from pydantic import BaseModel

class CaptionResponse(BaseModel):
    id: int
    transcript: str
    translated_text: str
    from_lang: str
    to_lang: str
    processing_ms: int
    created_at: str
    session_id: Optional[str] = None
