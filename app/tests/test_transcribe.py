from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _post_caption(from_lang: str, to_lang: str):
    # Fake audio bytes; the stub ignores actual content
    files = {"audio": ("chunk.webm", b"fake-audio-bytes", "audio/webm")}
    data = {
        "from_lang": from_lang,
        "to_lang": to_lang,
    }
    return client.post("/caption", files=files, data=data)


def test_caption_en_to_es():
    resp = _post_caption("en", "es")
    assert resp.status_code == 200

    data = resp.json()
    # basic shape
    assert "transcript" in data
    assert "translated_text" in data
    assert "from_lang" in data
    assert "to_lang" in data
    assert "processing_ms" in data

    assert data["from_lang"] == "en"
    assert data["to_lang"] == "es"
    assert isinstance(data["transcript"], str)
    assert isinstance(data["translated_text"], str)
    assert data["transcript"] != ""
    assert data["translated_text"] != ""


def test_caption_es_to_en():
    resp = _post_caption("es", "en")
    assert resp.status_code == 200

    data = resp.json()
    assert data["from_lang"] == "es"
    assert data["to_lang"] == "en"
    assert isinstance(data["transcript"], str)
    assert isinstance(data["translated_text"], str)
