from fastapi.testclient import TestClient
from app.main import app


client=TestClient(app)


def test_transcribe_stub():
    """testing /transcribe endpoint with a stub audio file."""

    files={"audio":("chunk.webm", b"fake-bytes", "audio/webm")}
    r=client.post("/transcribe?from_lang=en&to_lang=es", files=files)
    j=r.json()
    assert r.status_code==200
    assert "original" in j and "translated" in j
    assert j["fromLang"]=="en" and j["toLang"]=="es"
