from pydantic import BaseModel

class CaptionResponse(BaseModel):
    transcript: str
    translated_text: str
    from_lang: str
    to_lang: str
    processing_ms: int
