import sys
import os
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

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


@patch("app.services.translator_azure.azure_translate")
def test_azure_translation(mock_translate):
    mock_translate.return_value = "Hola mundo"
    settings.use_azure_translator = True
    settings.log_captions_to_db = False
    resp = _post_caption("en", "es")
    data = resp.json()
    assert data["translated_text"] == "Hola mundo"
