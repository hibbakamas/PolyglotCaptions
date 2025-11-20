import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi.testclient import TestClient 
from main import app 
from config import settings

client = TestClient(app)


def _post_caption(from_lang: str, to_lang: str):
    files = {
        "audio": ("chunk.webm", b"fake-audio-bytes", "audio/webm")
    }
    data = {
        "from_lang": from_lang,
        "to_lang": to_lang,
    }
    return client.post("/caption", files=files, data=data)


def test_caption_en_to_es_stub_mode():
    settings.use_azure_translator = False
    settings.log_captions_to_db = False

    resp = _post_caption("en", "es")
    assert resp.status_code == 200

    data = resp.json()
    assert "transcript" in data
    assert "translated_text" in data
    assert data["from_lang"] == "en"
    assert data["to_lang"] == "es"
    assert isinstance(data["processing_ms"], int)
    assert data["transcript"]
    assert data["translated_text"]
